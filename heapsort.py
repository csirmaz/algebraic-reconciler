
# Stable implementation of the heapsort algorithm

def heapify(arr, length, root, comp):
    # Build max heap

    left = 2*root + 1
    right = 2*root + 2
    largest = root

    # Find largest child
    for alt in (left, right):
        if alt < length and comp(arr[largest], arr[alt]) == 1: # arr[largest] < arr[alt]
            largest = alt
    
    if largest != root:
        arr[largest], arr[root] = arr[root], arr[largest] # swap
        heapify(arr, length, largest, comp)


def heap_sort(arr, comp):
    """In-place sort arr (array) according to comp (comparison function, comp(a, b) := sign(b - a) )"""
    
    n = len(arr)

    # Build maxheap starting from last parent
    for i in range(n//2, -1, -1):
        heapify(arr, n, i, comp)
    # print(f"Maxheap: {arr} ", end='')
    # print_heap(arr, len(arr))

    # Get the first element and repair heap
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        # print_heap(arr, i, end=' --> ')
        heapify(arr, i, 0, comp)
        # print_heap(arr, i)


def print_heap(arr, length, end="\n"):
    """Display heap"""
    n = length
    print(", ".join([f"{arr[i]}>{arr[2*i+1]}:{arr[2*i+2] if 2*i+2<n else 'x'}" for i in range(n//2)]), end=end)


if __name__ == '__main__':
    
    # Test code
    arr = [2, 5, 10, 1, 3, 9, 8, 0, 7, 11]
    heap_sort(arr, lambda a, b: (0 if a == b else (1 if a < b else -1)))
    print(arr)

