import asyncio
import time
from unittest.mock import MagicMock, AsyncMock

# 模擬 discord.Member
class MockMember:
    def __init__(self, name):
        self.name = name
        self.bot = False

    async def send(self, msg):
        # 模擬網路延遲
        await asyncio.sleep(0.05)

# 原始程式碼邏輯
async def original_send_to_gods(gods, summary_msg):
    for god in gods:
        try:
            await god.send(summary_msg)
        except Exception:
            pass

# 優化後的程式碼邏輯
async def optimized_send_to_gods(gods, summary_msg):
    async def safe_send(god, msg):
        try:
            await god.send(msg)
        except Exception:
            pass

    tasks = [safe_send(god, summary_msg) for god in gods]
    await asyncio.gather(*tasks)

async def run_benchmark():
    num_gods = 10
    gods = [MockMember(f"God_{i}") for i in range(num_gods)]
    summary_msg = "Game Start Summary"

    print(f"Testing with {num_gods} gods and 50ms delay per send.")

    # 測試原始版本
    start_time = time.perf_counter()
    await original_send_to_gods(gods, summary_msg)
    original_duration = time.perf_counter() - start_time
    print(f"Original duration: {original_duration:.4f}s")

    # 測試優化版本
    start_time = time.perf_counter()
    await optimized_send_to_gods(gods, summary_msg)
    optimized_duration = time.perf_counter() - start_time
    print(f"Optimized duration: {optimized_duration:.4f}s")

    improvement = (original_duration - optimized_duration) / original_duration * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
