import unireedsolomon as rs
import math
import random


class ErrorCorrectingCodesForSlidingWindows:

    def __init__(self, n, p, r, q, epsilon, s, k):
        self.N = n
        self.p = p
        self.s = s  # The sender maintains blocks of elements of size s from the current window
        self.R = r  # At each time step R symbols are communicated over the channel
        self.k = k  # number of blocks
        self.sigma_size_ecc = int(math.pow(2, 8))
        self.q = q
        self.sigma_c_size = math.ceil(self.sigma_size_ecc / q)
        self.epsilon = epsilon

    def run(self):
        sliding_window_blocks_sender_ecc = []
        sliding_window_blocks_receiver = []
        # Maintain a counter for each block initialized to -1 when the block is added.
        block_counter = [-1] * self.k
        # For the very first elements of the stream, we artificially create a window of size N with, say, all 0’s
        # and similarly divide it up into blocks. This is done to keep notation consistent.
        sliding_window_blocks_sender = self.init_sender(sliding_window_blocks_sender_ecc)
        decoded_blocks = []
        erasures = []
        self.init_receiver(sliding_window_blocks_receiver, decoded_blocks, erasures)
        # chosen block k is known via the shared randomness
        chosen_blocks = []
        index = 0
        while index < 20:  # foreach time step t do
            new_bit = random.randint(0, 1)  # create new bit in the data stream
            index += 1
            # every time step randomize the mapping from sigma to sigma_c
            random_map = self.randomize_map().copy()
            self.sender(new_bit, sliding_window_blocks_sender, block_counter, sliding_window_blocks_receiver,
                        chosen_blocks, decoded_blocks, random_map, sliding_window_blocks_sender_ecc, erasures)
            receiver_final = self.receiver(sliding_window_blocks_receiver, chosen_blocks, decoded_blocks, 255,
                                           random_map, erasures)
        current_window = []
        for block in sliding_window_blocks_sender:
            # last block was not send to receiver
            if len(block) != self.s:
                break
            str_block = [str(x) for x in block]
            in_string = ''.join(str_block)
            current_window.append(in_string)
        result = self.check_results(''.join(current_window), ''.join(receiver_final))
        return result

    def check_results(self, sender_window, receiver_window):
        prefix_size = int((1-self.p-self.epsilon) * self.N)
        prefix_sender = sender_window[:prefix_size]
        prefix_receiver = receiver_window[:prefix_size]
        if prefix_sender == prefix_receiver:
            return 1
        return 0

    def init_sender(self, ecc_block):
        # initiate the sliding window. create the blocks and add N 0's
        block = [0] * self.s
        last_block = [0] * (self.N % self.s)
        all_blocks = [block] * (self.k - 1)
        all_blocks.append(last_block)
        for i in range(self.k - 1):
            self.ecc(block, ecc_block)
        return all_blocks

    def init_receiver(self, blocks, the_decoded_blocks, erasures_blocks):
        # create the blocks -  partition of the stream into blocks
        for i in range(self.k-1):
            blocks.append([])
            the_decoded_blocks.append([])
            erasures_blocks.append([])

    def send_symbol(self, symbol, blocks, current_block):
        if random.random() <= self.p:
            # the data is corrupted by the channel
            blocks[current_block].append(random.randint(0, self.sigma_c_size - 1))
            return
        blocks[current_block].append(symbol)

    def randomize_map(self):
        sampled_list = random.sample(range(self.sigma_c_size - 1), self.sigma_size_ecc)
        return sampled_list

    @staticmethod
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

    @staticmethod
    def ecc_minus_1(block, erasures_pos):
        msg = ''.join(block)
        coder = rs.RSCoder(255, 223)
        try:
            dec, dec_ecc = coder.decode_fast(msg, True, None, erasures_pos, False)
            list1 = list(dec)
            ret_list = []
            for item in list1:
                bits = bin(ord(item))[2:]
                bits = '00000000'[len(bits):] + bits
                ret_list.append(bits)
            return ''.join(ret_list)
        except rs.RSCodecError:
            ret = ['0'] * 223 * 8
            return ''.join(ret)
        except:
            ret = ['0'] * 223 * 8
            return ''.join(ret)

    @staticmethod
    def bc(symbol, the_map):
        # turn symbol in chr to dec number for map array index
        symbol_number = ord(symbol)
        return the_map[symbol_number]

    @staticmethod
    def bc_minus_1(symbol, the_map):
        if symbol in the_map:
            return the_map.index(symbol)
        return '+'

    def sender(self, data, blocks, block_count, receiver_blocks, random_blocks,
               the_decoded_blocks, the_map, ecc_blocks, erasures_blocks):
        # any arriving element is appended to the last non-empty block
        blocks[self.k - 1].append(data)
        # if last block is now full - need to delete first block and add a new one
        if len(blocks[self.k - 1]) == self.s:
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
            self.ecc(blocks[self.k - 2], ecc_blocks)
            # update block counter
            block_count.pop(0)
            block_count.append(-1)
        for repeat in range(self.R):
            block_chosen = random.randint(1, self.k - 1)  # choose from k-1 blocks
            block_count[block_chosen - 1] += 1
            random_blocks.append(block_chosen - 1)
            # if all the symbols of the block were already communicated send a random symbol
            if block_count[block_chosen - 1] < self.sigma_size_ecc-1:
                # Send the next symbol of BC(ECC(Bk)) that has not yet been sent according to count_k
                self.send_symbol(self.bc(ecc_blocks[block_chosen - 1][block_count[block_chosen - 1]], the_map),
                                 receiver_blocks, block_chosen - 1)
            else:
                self.send_symbol(random.randint(0, self.sigma_c_size - 1), receiver_blocks, block_chosen - 1)

    def receiver(self, blocks, chosen_block_k, after_bc_decode_blocks, size_of_blocks, the_map, erasures_blocks):
        for repeat in range(self.R):
            bk = chosen_block_k.pop(0)
            decoded_size = len(after_bc_decode_blocks[bk])
            if decoded_size == size_of_blocks:
                continue
            symbol = self.bc_minus_1(blocks[bk][decoded_size], the_map)
            if symbol == '+':
                after_bc_decode_blocks[bk].append("\x00")
                erasures_blocks[bk].append(len(after_bc_decode_blocks[bk]) - 1)
            else:
                after_bc_decode_blocks[bk].append(chr(symbol))
        after_ecc_decode_blocks = []
        block_num = 0
        for block in after_bc_decode_blocks:
            block_copy = block.copy()
            erasures_copy = erasures_blocks[block_num].copy()
            # pad block with null bytes
            while len(block_copy) < 255:
                block_copy.append("\x00")
                erasures_copy.append(len(block_copy)-1)
            after_ecc_decode_blocks.append(self.ecc_minus_1(block_copy, erasures_copy))
            block_num += 1
        return after_ecc_decode_blocks
