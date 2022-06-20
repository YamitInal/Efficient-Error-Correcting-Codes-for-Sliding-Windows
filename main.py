import unireedsolomon as rs
import math
import random


def init_sender(block_num, data, size_of_block, blocks, ecc_block):
    # initiate the sliding window. create the blocks and add N 0's
    for i in range(block_num):
        block = []
        for bits in range(i * size_of_block, i * size_of_block + size_of_block):
            if bits < len(data):
                block.append(data[bits])
            else:
                blocks.append(list(block))
                return
        blocks.append(list(block))
        ecc(block, ecc_block)


def init_receiver(num_of_blocks, blocks, the_decoded_blocks, erasures_blocks):
    # create the blocks -  partition of the stream into blocks
    for i in range(num_of_blocks-1):
        blocks.append([])
        the_decoded_blocks.append([])
        erasures_blocks.append([])


def create_file():
    file = open('data_stream.txt', "w")
    file.write('')  # overwrite any existing content
    file.close()
    file = open('data_stream.txt', "a")
    for i in range(1000000):
        bit = random.randint(0, 1)  # create new bit in the data stream
        file.write(str(bit))
    file.close()


def send_symbol(symbol, blocks, current_block, err_prob, sigma_c):
    if random.randint(1, 100) / 100 <= err_prob:
        # the data is corrupted by the channel
        blocks[current_block].append(random.randint(0, sigma_c - 1))
        return
    blocks[current_block].append(symbol)


def randomize_map(sigma_c, sigma_ecc):
    sampled_list = random.sample(range(sigma_c - 1), sigma_ecc)
    return sampled_list


def ecc(block_to_decode, ecc_blocks):
    byte_block = []
    # every 8 bits is a symbol - separate block to chunks 223 of size 8
    for i in range(0, len(block_to_decode), 8):
        eight_bits = [str(x) for x in block_to_decode[i:i+8]]
        bits = ''.join(eight_bits)
        chr_byte = chr(int(bits, 2))
        byte_block.append(chr_byte)
    msg = ''.join(byte_block)
    coder = rs.RSCoder(255, 223)
    enc = coder.encode_fast(msg)
    list1 = list(enc)
    ecc_blocks.append(list1)


def ecc_minus_1(block, erasures_pos):
    msg = ''.join(block)
    coder = rs.RSCoder(255, 223)
    try:
        dec, dec_ecc = coder.decode_fast(msg, erasures_pos)
        return dec
    except rs.RSCodecError:
        return "Block error"
    except:
        list_of_zeros = [0] * 223 * 8
        return "Block error"


def bc(symbol, the_map):
    symbol_number = ord(symbol)
    return the_map[symbol_number]


def bc_minus_1(symbol, the_map):
    if symbol in the_map:
        return the_map.index(symbol)
    return '+'


def sender(block_num, data, size_of_block, blocks, r, block_count, receiver_blocks, random_blocks, the_decoded_blocks,
           the_map, sigma_c, err_prob, ecc_blocks, size_of_block_ecc, erasures_blocks):
    # any arriving element is appended to the last non-empty block
    blocks[block_num - 1].append(data)
    # if last block is now full - need to delete first block and add a new one
    if len(blocks[block_num - 1]) == size_of_block:
        blocks.pop(0)
        blocks.append([])
        receiver_blocks.pop(0)
        receiver_blocks.append([])
        the_decoded_blocks.pop(0)
        the_decoded_blocks.append([])
        erasures_blocks.pop(0)
        erasures_blocks.append([])
        ecc_blocks.pop(0)
        # encode the full block with ecc
        ecc(blocks[block_num - 2], ecc_blocks)
        # update block counter
        block_count.pop(0)
        block_count.append(-1)
    for repeat in range(r):
        block_chosen = random.randint(1, block_num - 1)  # choose from k-1 blocks
        block_count[block_chosen - 1] += 1
        random_blocks.append(block_chosen - 1)
        # if all the symbols of the block were already communicated send a random symbol
        if block_count[block_chosen - 1] < size_of_block_ecc-1:
            # Send the next symbol of BC(ECC(Bk)) that has not yet been sent according to count_k
            send_symbol(bc(ecc_blocks[block_chosen - 1][block_count[block_chosen - 1]], the_map), receiver_blocks,
                        block_chosen - 1, err_prob, sigma_c)
        else:
            send_symbol(random.randint(0, sigma_c - 1), receiver_blocks, block_chosen - 1, err_prob, sigma_c)


def receiver(blocks, r, chosen_block_k, the_decoded_blocks, size_of_blocks, the_map, erasures_blocks):
    for repeat in range(r):
        bk = chosen_block_k.pop(0)
        decoded_size = len(the_decoded_blocks[bk])
        if decoded_size == size_of_blocks:
            continue
        symbol = bc_minus_1(blocks[bk][decoded_size], the_map)
        if symbol == '+':
            the_decoded_blocks[bk].append("\x00")
            erasures_blocks[bk].append(len(the_decoded_blocks[bk])-1)
        else:
            the_decoded_blocks[bk].append(chr(symbol))
    block_num =0
    for block in the_decoded_blocks:
        block_copy = block.copy()
        erasures_copy = erasures_blocks[block_num].copy()
        # pad block with null bytes
        while len(block_copy) != 255:
            block_copy.append("\x00")
            erasures_copy.append(len(block_copy[block_num])-1)
        print(ecc_minus_1(block_copy, erasures_copy))
        block_num += 1


if __name__ == '__main__':
    # N is  the size of the window and is assumed to be very large.
    N = int(input("please enter the size of the sliding window"))
    p = float(input("please enter the noise level"))  # noise level p < 1
    epsilon = 0.0001  # epsilon > 0
    s = 223*8  # The sender maintains blocks of elements of size s from the current window
    R = 3  # At each time step R symbols are communicated over the channel
    k = math.floor(N / s) + 1  # number of blocks
    sigma_size_ecc = int(math.pow(2, 8))
    q = 0.4
    sigma_c_size = math.ceil(sigma_size_ecc / q)
    data_stream = []
    for idx in range(N):
        data_stream.append(0)  # before t=0 all bits are zero
    sliding_window_blocks_sender = []
    sliding_window_blocks_sender_ecc = []
    sliding_window_blocks_receiver = []
    block_counter = []
    for num in range(k):  # Maintain a counter for each block initialized to -1 when the block is added.
        block_counter.append(-1)
    # For the very first elements of the stream, we artificially create a window of size N with, say, all 0’s
    # and similarly divide it up into blocks. This is done to keep notation consistent.
    init_sender(k, data_stream, s, sliding_window_blocks_sender, sliding_window_blocks_sender_ecc)
    decoded_blocks = []
    erasures = []
    init_receiver(k, sliding_window_blocks_receiver, decoded_blocks, erasures)
    # chosen block k is known via the shared randomness
    chosen_blocks = []
    # create file with random data stream
    create_file()
    f = open('data_stream.txt')
    new_data = f.read()
    f.close()
    # random map from a set of inputs sigma_ecc to a larger set sigma_c
    random_map = []
    for num in range(sigma_size_ecc - 1):  # Maintain a counter for each block initialized to -1 when the block is added
        random_map.append(0)
    print('The sliding window is of size ' + str(N) + '\nThere are ' + str(k) + ' blocks\nEach block of size ' + str(s))
    index = 0
    while True:  # foreach time step t do
        new_bit = int(new_data[index])  # create new bit in the data stream
        index += 1
        # every time step randomize the mapping from sigma to sigma_c
        random_map = randomize_map(sigma_c_size, sigma_size_ecc).copy()
        sender(k, new_bit, s, sliding_window_blocks_sender, R, block_counter, sliding_window_blocks_receiver,
               chosen_blocks, decoded_blocks, random_map, sigma_c_size, p, sliding_window_blocks_sender_ecc,
               sigma_size_ecc, erasures)
        receiver(sliding_window_blocks_receiver, R, chosen_blocks, decoded_blocks, s, random_map, erasures)
