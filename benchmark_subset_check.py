import timeit

def benchmark():
    entry = {"player_count": 5, "existing_roles": [1, 2, 3], "roles": [4, 5, 6], "extra": "data"}
    keys_tuple = ("player_count", "existing_roles", "roles")
    keys_set = {"player_count", "existing_roles", "roles"}

    # Current approach
    def current_all_gen():
        return all(k in entry for k in keys_tuple)

    # Explicit check
    def explicit_check():
        return "player_count" in entry and "existing_roles" in entry and "roles" in entry

    # Set subset check
    def set_subset():
        return keys_set.issubset(entry)

    # Dictionary keys subset check
    def keys_subset():
        return keys_set <= entry.keys()

    # map approach
    def map_check():
        return all(map(entry.__contains__, keys_tuple))

    iterations = 1000000

    t1 = timeit.timeit(current_all_gen, number=iterations)
    t2 = timeit.timeit(explicit_check, number=iterations)
    t3 = timeit.timeit(set_subset, number=iterations)
    t4 = timeit.timeit(keys_subset, number=iterations)
    t5 = timeit.timeit(map_check, number=iterations)

    print(f"Current (all gen): {t1:.4f}s")
    print(f"Explicit check:    {t2:.4f}s")
    print(f"Set issubset:      {t3:.4f}s")
    print(f"Keys <= (set):     {t4:.4f}s")
    print(f"Map check:         {t5:.4f}s")

    print(f"\nImprovement (Explicit vs Current): {t1/t2:.2f}x")
    print(f"Improvement (Set issubset vs Current): {t1/t3:.2f}x")
    print(f"Improvement (Keys <= vs Current): {t1/t4:.2f}x")

if __name__ == "__main__":
    benchmark()
