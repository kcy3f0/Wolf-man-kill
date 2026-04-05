import timeit

def append_loop():
    target = []
    source = list(range(1000))
    for item in source:
        target.append(item)

def extend_method():
    target = []
    source = list(range(1000))
    target.extend(source)

if __name__ == '__main__':
    iterations = 10000

    append_time = timeit.timeit(append_loop, number=iterations)
    extend_time = timeit.timeit(extend_method, number=iterations)

    print("Performance Baseline Measurement")
    print("--------------------------------")
    print(f"Items to add: 1000")
    print(f"Iterations: {iterations}")
    print(f"Loop with append: {append_time:.5f} seconds")
    print(f"List extend:      {extend_time:.5f} seconds")
    print(f"Improvement:      {append_time / extend_time:.2f}x faster")
