import asyncio
import random
import time

async def sequential_voting(num_players):
    start = time.perf_counter()
    results = []
    for _ in range(num_players):
        await asyncio.sleep(random.uniform(0.5, 1.5))
        results.append(1)
    end = time.perf_counter()
    return end - start

async def concurrent_voting(num_players):
    start = time.perf_counter()
    async def process_vote():
        await asyncio.sleep(random.uniform(0.5, 1.5))
        return 1

    tasks = [process_vote() for _ in range(num_players)]
    results = await asyncio.gather(*tasks)
    end = time.perf_counter()
    return end - start

async def main():
    num_players = 10
    print(f"Simulating voting for {num_players} AI players...")

    seq_time = await sequential_voting(num_players)
    print(f"Sequential time: {seq_time:.2f} seconds")

    conc_time = await concurrent_voting(num_players)
    print(f"Concurrent time: {conc_time:.2f} seconds")

    improvement = (seq_time - conc_time) / seq_time * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
