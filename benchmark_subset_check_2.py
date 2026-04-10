import timeit

def benchmark_location_2():
    existing_roles_set = {"狼人", "預言家", "平民", "女巫", "獵人", "守衛", "騎士"}
    roles = ["狼人", "預言家", "平民", "平民", "平民", "女巫"]

    # Current approach
    def current_all_gen():
        return all(r in existing_roles_set for r in roles)

    # set(roles).issubset(existing_roles_set)
    def set_issubset():
        return set(roles).issubset(existing_roles_set)

    # existing_roles_set.issuperset(roles)
    def set_issuperset():
        return existing_roles_set.issuperset(roles)

    iterations = 1000000

    t1 = timeit.timeit(current_all_gen, number=iterations)
    t2 = timeit.timeit(set_issubset, number=iterations)
    t3 = timeit.timeit(set_issuperset, number=iterations)

    print(f"Current (all gen):  {t1:.4f}s")
    print(f"set.issubset:       {t2:.4f}s")
    print(f"set.issuperset:     {t3:.4f}s")

    print(f"\nImprovement (issubset vs Current): {t1/t2:.2f}x")
    print(f"Improvement (issuperset vs Current): {t1/t3:.2f}x")

if __name__ == "__main__":
    benchmark_location_2()
