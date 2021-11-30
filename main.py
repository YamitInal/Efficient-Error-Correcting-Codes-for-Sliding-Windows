import math
import random


def init_sender(block_num, data, size_of_block, blocks):
    for i in range(1, block_num+1):
        block = []
        for bits in range((i-1)*size_of_block, (i-1)*size_of_block+size_of_block):
            if bits < len(data):
                block.append(data[bits])
            else:
                break
        blocks.append(list(block))


def sender(block_num, data, size_of_block, blocks):
    print("the new data is " + str(data[len(data)-1]))
    blocks[block_num-1].append(data[len(data)-1])
    bit_index = 0
    for bit in blocks[0]:
        if bit == '-':
            bit_index = bit_index+1
            if bit_index == size_of_block-1: # need to delete block and add a new one
                blocks.pop(0)
                blocks.append([])
                break
        else:
            blocks[0][bit_index] = '-'
            break


# def receiver():


if __name__ == '__main__':
    # N is  the size of the window and is assumed to be very large.
    N = int(input("please enter the size of the sliding window"))
    p = float(input("please enter the noise level"))     # noise level p < 1
    epsilon = 0.0001    # epsilon > 0
    s = math.floor(pow(math.log2(N), 2))    # The sender maintains blocks of elements of size s from the current window
    R = 3   # At each time step R symbols are communicated over the channel
    k = math.floor(N/s) + 1    # number of blocks
    sigma = [0, 1]  # alphabet
    data_stream = []
    for idx in range(N):
        data_stream.append(0)   # before t=0 all bits are zero
    sliding_window_blocks = []
    init_sender(k, data_stream, s, sliding_window_blocks)
    while True:
        print('i am main')
        new_bit = random.randint(0, 1)  # create new bit in the data stream
        print('the new bit is ' + str(new_bit))
        data_stream.append(new_bit)
        sender(k, data_stream, s, sliding_window_blocks)
