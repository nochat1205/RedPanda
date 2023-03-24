def swap(li, p1, p2):
    li[p1], li[p2] = li[p2], li[p1]

def partition(li, lower, upper):
    pivot = li[upper-1]
    miner_empty_pos = lower
    for sear_pos in range(lower, upper-1):
        if li[sear_pos] < pivot:
            swap(li, sear_pos, miner_empty_pos)
            miner_empty_pos += 1
    swap(li, upper-1, miner_empty_pos)
    return miner_empty_pos

def quicksort(li, lower, upper):
    if upper-lower > 1:
        mid = partition(li, lower, upper)
        quicksort(li, lower, mid)
        quicksort(li, mid+1, upper)

import random

if __name__ == '__main__':
    for _ in range(100):
        array = [random.randint(0,100) for a in range(50)]
        ans1 = sorted(array)
        quicksort(array, 0, len(array))
        if array != ans1:
            print(array)
            print(ans1)
            break

