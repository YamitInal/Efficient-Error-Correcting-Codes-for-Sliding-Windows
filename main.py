import math
import random


def init_sender(block_num, data, size_of_block, blocks):
    # initiate the sliding window. create the blocks and add N 0's
    for i in range(block_num):
        block = []
        for bits in range(i*size_of_block, i*size_of_block+size_of_block):
            if bits < len(data):
                block.append(data[bits])
            else:
                break
        blocks.append(list(block))


def init_receiver(num_of_blocks, blocks, the_decoded_blocks):
    # create the blocks -  partition of the stream into blocks
    for i in range(num_of_blocks):
        blocks.append([])
    for i in range(num_of_blocks):
        the_decoded_blocks.append('')


def create_file():
    file = open('data_stream.txt', "w")
    file.write('')     # overwrite any existing content
    file.close()
    file = open('data_stream.txt', "a")
    for i in range(1000000):
        bit = random.randint(0, 1)  # create new bit in the data stream
        file.write(str(bit))
    file.close()


def send_symbol(symbol, blocks, current_block, err_prob, sigma_c):
    if random.randint(0, 100)/100 <= err_prob:
        # the data is corrupted by the channel
        blocks[current_block].append(str(random.randint(0, sigma_c-1)))
        return
    blocks[current_block].append(symbol)


def randomize_map(sigma_c, the_map):
    sampled_list = random.sample(range(sigma_c), 2)
    the_map[0] = sampled_list[0]
    the_map[1] = sampled_list[1]


def ecc(symbol):
    return symbol


def ecc_minus_1(string):
    return string


def bc(symbol, the_map):
    return the_map[int(symbol)]


def bc_minus_1(symbol, the_map):
    if symbol in the_map:
        return str(the_map.index(symbol))
    return '+'


def sender(block_num, data, size_of_block, blocks, r, block_count, receiver_blocks, random_blocks, the_decoded_blocks,
           the_map, sigma_c, err_prob):
    # if last block is full - need to delete block and add a new one
    if len(blocks[block_num-1]) == size_of_block:
        blocks.pop(0)
        blocks.append([])
        receiver_blocks.pop(0)
        receiver_blocks.append([])
        the_decoded_blocks.pop(0)
        the_decoded_blocks.append('')
        # update block counter
        block_count.pop(0)
        block_count.append(-1)
    # any arriving element is appended to the last non-empty block
    blocks[block_num-1].append(data)
    for repeat in range(r):
        block_chosen = random.randint(1, block_num-1)   # choose from k-1 blocks
        block_count[block_chosen-1] += 1
        random_blocks.append(block_chosen-1)
        # if If all the symbols of the block were already communicated send a random symbol
        if block_count[block_chosen - 1] < size_of_block:
            # Send the next symbol of BC(ECC(Bk)) that has not yet been sent according to count_k
            send_symbol(bc(ecc(blocks[block_chosen-1][block_count[block_chosen-1]]), the_map), receiver_blocks,
                        block_chosen-1, err_prob, sigma_c)
        else:
            send_symbol(random.randint(0, sigma_c-1), receiver_blocks, block_chosen-1, err_prob, sigma_c)


def receiver(blocks, r, chosen_block_k, the_decoded_blocks, size_of_blocks, the_map):
    for repeat in range(r):
        bk = chosen_block_k.pop(0)
        decoded_size = len(the_decoded_blocks[bk])
        if decoded_size == size_of_blocks:
            continue
        symbol = bc_minus_1(blocks[bk][decoded_size], the_map)
        the_decoded_blocks[bk] += symbol
    for block in the_decoded_blocks:
        print(block)


if __name__ == '__main__':
    # N is  the size of the window and is assumed to be very large.
    N = int(input("please enter the size of the sliding window"))
    p = float(input("please enter the noise level"))     # noise level p < 1
    epsilon = 0.0001    # epsilon > 0
    s = 223    # The sender maintains blocks of elements of size s from the current window
    R = 3   # At each time step R symbols are communicated over the channel
    k = math.floor(N/s) + 1    # number of blocks
    sigma_size = 2
    q = 0.4
    sigma_c_size = math.ceil(sigma_size / q)
    data_stream = []
    for idx in range(N):
        data_stream.append(0)   # before t=0 all bits are zero
    sliding_window_blocks_sender = []
    sliding_window_blocks_receiver = []
    block_counter = []
    for num in range(k):    # Maintain a counter for each block initialized to -1 when the block is added.
        block_counter.append(-1)
    # For the very first elements of the stream, we artificially create a window of size N with, say, all 0’s
    # and similarly divide it up into blocks. This is done to keep notation consistent.
    init_sender(k, data_stream, s, sliding_window_blocks_sender)
    decoded_blocks = []
    init_receiver(k, sliding_window_blocks_receiver, decoded_blocks)
    # chosen block k is known via the shared randomness
    chosen_blocks = []
    # create file with random data stream
    create_file()
    f = open('data_stream.txt')
    new_data = f.read()
    f.close()
    # random map from a set of inputs sigma to a larger set sigma_c
    random_map = [0, 0]
    print('The sliding window is of size ' + str(N) + '\nThere are ' + str(k) + ' blocks\nEach block of size ' + str(s))
    index = 0
    while True:     # foreach time step t do
        new_bit = new_data[index]  # create new bit in the data stream
        index += 1
        # every time step randomize the mapping from sigma to sigma_c
        randomize_map(sigma_c_size, random_map)
        sender(k, new_bit, s, sliding_window_blocks_sender, R, block_counter, sliding_window_blocks_receiver,
               chosen_blocks, decoded_blocks, random_map, sigma_c_size, p)
        receiver(sliding_window_blocks_receiver, R, chosen_blocks, decoded_blocks, s, random_map)
