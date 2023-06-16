def max_sum(arr, window_size):
    array_size = len(arr)
    # n must be greater than k
    if array_size <= window_size:
        print("Invalid operation")
        return -1
    print(window_size, " size of current window")

    # Compute sum of first window of size k
    window_sum = sum([arr[i] for i in range(window_size)])

    print("First window sum is", window_sum)
    max_sum = window_sum

    # Compute sums of remaining windows by
    # removing first element of previous
    # window and adding last element of
    # current window.
    for i in range(array_size - window_size):
        window_sum = window_sum - arr[i] + arr[i + window_size]
        max_sum = max(window_sum, max_sum)
        print("Current window sum is", window_sum, "Max sum is", max_sum)

    return max_sum


# Driver code
arr = [2, 6, 9, 2, 1, 8, 5, 6, 3]
k = 3
print(max_sum(arr, k))

a = {'a': 1, 'b': 2}

a['a'] += 3
print(a)
