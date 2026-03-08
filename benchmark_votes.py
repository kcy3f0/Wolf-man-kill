import time
import random

def baseline(votes):
    if not votes:
        return []
    max_votes = max(votes.values())
    candidates = [p for p, c in votes.items() if c == max_votes]
    return candidates

def optimized(votes):
    if not votes:
        return []

    max_votes = -1
    candidates = []
    for p, c in votes.items():
        if c > max_votes:
            max_votes = c
            candidates = [p]
        elif c == max_votes:
            candidates.append(p)
    return candidates

# Generate a mock votes dictionary
# 20 players, 1 vote each for random targets
votes = {}
for i in range(20):
    votes[f'Player_{i}'] = random.randint(1, 10)

def run_benchmark(func, iterations=100000):
    start = time.perf_counter()
    for _ in range(iterations):
        func(votes)
    end = time.perf_counter()
    return end - start

base_time = run_benchmark(baseline)
opt_time = run_benchmark(optimized)

print(f"Baseline: {base_time:.5f}s")
print(f"Optimized: {opt_time:.5f}s")
if base_time > 0:
    print(f"Improvement: {(base_time - opt_time) / base_time * 100:.2f}%")
