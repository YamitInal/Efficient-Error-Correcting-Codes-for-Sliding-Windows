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


def send_symbol(symbol, blocks, current_block):
    blocks[current_block].append(symbol)


def ecc(symbol):
    return symbol


def ecc_minus_1(string):
    return string


def bc(symbol):
    return symbol


def bc_minus_1(string):
    return string


def sender(block_num, data, size_of_block, blocks, r, block_count, receiver_blocks, random_blocks, the_decoded_blocks):
    # any arriving element is appended to the last non-empty block
    blocks[block_num-1].append(data)
    bit_index = 0
    # If all elements in the first block expire, add a new (empty) block and remove B1
    for bit in blocks[0]:
        if bit == '-':
            bit_index = bit_index+1
            if bit_index == size_of_block-1:    # need to delete block and add a new one
                blocks.pop(0)
                blocks.append([])
                receiver_blocks.pop(0)
                receiver_blocks.append([])
                the_decoded_blocks.pop(0)
                the_decoded_blocks.append('')
                # update block counter
                block_count.pop(0)
                block_count.append(-1)
                break
        else:
            blocks[0][bit_index] = '-'
            break
    for repeat in range(r):
        block_chosen = random.randint(1, block_num-1)   # choose from k-1 blocks
        block_count[block_chosen-1] += 1
        random_blocks.append(block_chosen-1)
        # if If all the symbols of the block were already communicated send a random symbol
        if block_count[block_chosen - 1] < size_of_block:
            # Send the next symbol of BC(ECC(Bk)) that has not yet been sent according to count_k
            send_symbol(bc(ecc(blocks[block_chosen-1][block_count[block_chosen-1]])), receiver_blocks, block_chosen-1)
        else:
            send_symbol(4, receiver_blocks, block_chosen-1)


def receiver(blocks, r, chosen_block_k, the_decoded_blocks, size_of_blocks):
    for repeat in range(r):
        bk = chosen_block_k.pop(0)
        block_string = ''
        for symbol in blocks[bk]:
            if len(block_string) == size_of_blocks:
                break
            block_string += ''.join(str(symbol))
        # block_string = ecc_minus_1(bc_minus_1()))
        the_decoded_blocks[bk] = block_string
    for block in the_decoded_blocks:
        print(block)


if __name__ == '__main__':
    # N is  the size of the window and is assumed to be very large.
    N = int(input("please enter the size of the sliding window"))
    p = float(input("please enter the noise level"))     # noise level p < 1
    epsilon = 0.0001    # epsilon > 0
    s = math.floor(pow(math.log2(N), 2))    # The sender maintains blocks of elements of size s from the current window
    # s|n without remainder
    while not (N % s == 0):
        s += 1
    R = 3   # At each time step R symbols are communicated over the channel
    k = math.floor(N/s) + 1    # number of blocks
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
    print('The sliding window is of size ' + str(N) + '\nThere are ' + str(k) + ' blocks\nEach block of size ' + str(s))
    index = 0
    while True:     # foreach time step t do
        new_bit = new_data[index]  # create new bit in the data stream
        data_stream.append(new_bit)
        index += 1
        sender(k, new_bit, s, sliding_window_blocks_sender, R, block_counter, sliding_window_blocks_receiver,
               chosen_blocks, decoded_blocks)
        receiver(sliding_window_blocks_receiver, R, chosen_blocks, decoded_blocks, s)
