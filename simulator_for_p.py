import math
import time
import ecc_for_sliding_windows as ecc_code
import ecc_for_sliding_windows_no_bc as ecc_code_no_bc

if __name__ == '__main__':
    # rate of ecc
    k = 223
    n = 255
    r = k/n
    # constant
    epsilon = 0.01
    xi = epsilon
    xi_tag = epsilon
    sigma = 256
    delta = 0.001
    q = 0.3
    N = 5000
    p = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17]
    # compute max noise level allowed
    p_top = (epsilon * (1 - delta - r)) / ((1 + xi) * (1 + xi_tag) * (1 + q) - (1 - delta - r))
    print('P_top: ' + str(p_top))
    size_of_blocks = 223 * 8
    number_of_blocks = math.floor(N / size_of_blocks) + 1
    number_of_runs = 100
    file = open('scheme_run.txt', "w")
    file.write('')  # overwrite any existing content
    file.close()
    file = open('scheme_run.txt', "a")
    for x in p:
        msg = '\nScheme Parameters: \nSliding Windows size: ' + str(N) + '\nBlocks Number: ' + str(number_of_blocks) +\
              ' \nBlock Size: ' + str(size_of_blocks) + '\nNoise Level: ' + str(x) + '\nq value: ' +\
              str(q) + '\nPlease wait...\n'
        print(msg)
        file.write(msg+"\n")
        success_number = 0
        total_time = 0
        R = math.ceil((1 + xi_tag) / (r * (x + epsilon) * math.log(sigma, 2)))
        ecc_run = ecc_code.ErrorCorrectingCodesForSlidingWindows(N, x, R, q, epsilon, size_of_blocks, number_of_blocks)
        for idx in range(number_of_runs):
            start_time = time.time()
            result = ecc_run.run()
            end_time = time.time()
            run_time = end_time-start_time
            total_time += run_time
            success_number += result
        success_rate = (success_number / number_of_runs) * 100
        avr_run_time = total_time/number_of_runs
        msg = "Scheme Average Run Time: " + str(avr_run_time) + " seconds\nScheme Success Rate for p=" +\
              str(x) + " is " + str(success_rate) + "%\n"
        print(msg)
        file.write(msg+"\n")
    file.close()
