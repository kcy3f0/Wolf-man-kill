import asyncio
import time
import random

class MockMember:
    def __init__(self, name):
        self.name = name

    async def send(self, content):
        # 模擬網路延遲
        await asyncio.sleep(0.05)
        # print(f"Sent to {self.name}: {content}")

async def sequential_send(wolves, msg):
    start = time.perf_counter()
    for wolf in wolves:
        try:
            await wolf.send(msg)
        except Exception:
            pass
    return time.perf_counter() - start

async def concurrent_send(wolves, msg):
    start = time.perf_counter()

    async def safe_send(w, m):
        try:
            await w.send(m)
        except Exception:
            pass

    await asyncio.gather(*(safe_send(wolf, msg) for wolf in wolves))
    return time.perf_counter() - start

async def main():
    num_wolves = 4
    wolves = [MockMember(f"Wolf-{i}") for i in range(num_wolves)]
    msg = "今晚狼隊鎖定目標：**1 號**。"

    print(f"Testing with {num_wolves} wolves...")

    # Warm up
    await sequential_send(wolves, msg)
    await concurrent_send(wolves, msg)

    seq_times = []
    con_times = []

    for _ in range(10):
        seq_times.append(await sequential_send(wolves, msg))
        con_times.append(await concurrent_send(wolves, msg))

    avg_seq = sum(seq_times) / len(seq_times)
    avg_con = sum(con_times) / len(con_times)

    print(f"Average Sequential Time: {avg_seq:.4f}s")
    print(f"Average Concurrent Time: {avg_con:.4f}s")
    print(f"Speedup: {avg_seq / avg_con:.2f}x")

if __name__ == "__main__":
    asyncio.run(main())
