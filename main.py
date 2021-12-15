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


def send_symbol(symbol):
    print(f"the symbol {symbol} was send to receiver")


def ecc(symbol):
    return symbol


def bc(symbol):
    return symbol


def sender(block_num, data, size_of_block, blocks, r, block_count):
    print("the new data is " + str(data))
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
        # Send the next symbol of BC(ECC(Bk)) that has not yet been sent according to count_k
        send_symbol(bc(ecc(blocks[block_chosen-1][block_count[block_chosen-1]])))


# def receiver():


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
    sliding_window_blocks = []
    block_counter = []
    for num in range(k):    # Maintain a counter for each block initialized to -1 when the block is added.
        block_counter.append(-1)
    # For the very first elements of the stream, we artificially create a window of size N with, say, all 0’s
    # and similarly divide it up into blocks. This is done to keep notation consistent.
    init_sender(k, data_stream, s, sliding_window_blocks)
    while True:
        print('i am main')
        new_bit = random.randint(0, 1)  # create new bit in the data stream
        print('the new bit is ' + str(new_bit))
        data_stream.append(new_bit)
        sender(k, new_bit, s, sliding_window_blocks, R, block_counter)
