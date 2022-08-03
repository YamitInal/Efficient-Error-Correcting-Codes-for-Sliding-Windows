import math
import ecc_for_sliding_windows as ecc_code

if __name__ == '__main__':
    # rate of ecc
    k = 223
    n = 255
    r = k/n
    # constant
    epsilon = 0.01
    ksi = epsilon
    ksi_tag = epsilon
    sigma = 256
    delta = 0.001
    q = 0.3
    # from user
    N = int(input("please enter the size of the sliding window"))
    p = float(input("please enter the noise level"))  # noise level p < 1
    p_top = (epsilon * (1 - r)) / r
    R = math.floor((1+ksi_tag) / (r*(p+epsilon) * math.log(sigma, 2)))
    size_of_blocks = 223 * 8
    number_of_blocks = math.floor(N / size_of_blocks) + 1
    ecc_run = ecc_code.ErrorCorrectingCodesForSlidingWindows(N, p, R, q, epsilon, size_of_blocks, number_of_blocks)
    success_number = 0
    number_of_runs = 100
    print(
        'The sliding window is of size ' + str(N) + '\nThere are ' + str(number_of_blocks)
        + ' blocks\nEach block of size ' + str(size_of_blocks) + '\nThe noise level is ' + str(p)
        + '\nPlease wait...')
    for x in range(number_of_runs):
        result = ecc_run.run()
        success_number += result
    success_rate = (success_number/number_of_runs) * 100
    print("the code scheme success rate for p=" + str(p) + " is " + str(success_number) + "%")
