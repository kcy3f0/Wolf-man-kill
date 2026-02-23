import asyncio
import time
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def run_benchmark_logic(AIManager):
    print("Running Integrated Benchmark: Optimized vs Legacy Gemini CLI")
    print("-" * 60)

    iterations = 50

    # 1. Benchmark Legacy (Subprocess)
    print("Testing Legacy Fallback...")

    # We patch os.environ globally for the duration of legacy test
    with patch.dict(os.environ, {'AI_PROVIDER': 'gemini-cli'}, clear=True):
        # Ensure GEMINI_API_KEY is NOT in env
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']

        ai_manager_legacy = AIManager()

        if ai_manager_legacy.gemini_api_key:
            print("WARNING: gemini_api_key is set in legacy test! Benchmark invalid.")

        async def mock_subprocess_exec(*args, **kwargs):
            # Simulate overhead
            await asyncio.sleep(0.002)
            process = MagicMock()
            process.communicate = AsyncMock(return_value=(b"CLI_RESPONSE", b""))
            process.returncode = 0
            return process

        with patch('asyncio.create_subprocess_exec', side_effect=mock_subprocess_exec):
            start = time.perf_counter()
            for _ in range(iterations):
                await ai_manager_legacy._generate_with_gemini_cli("test")
            end = time.perf_counter()
            legacy_time = (end - start) / iterations
            print(f"Legacy (Subprocess) avg time: {legacy_time*1000:.4f} ms")

    # 2. Benchmark Optimized (API)
    print("Testing Optimized API...")
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key', 'AI_PROVIDER': 'gemini-cli'}):
        ai_manager_opt = AIManager()

        if not ai_manager_opt.gemini_api_key:
             print("WARNING: gemini_api_key NOT set in optimized test!")

        # Mock _generate_with_gemini_api on the instance
        async def mock_api_call(prompt):
             await asyncio.sleep(0) # Minimal async yield
             return "API_RESPONSE"

        # We patch the METHOD on the instance
        ai_manager_opt._generate_with_gemini_api = mock_api_call

        start = time.perf_counter()
        for _ in range(iterations):
            await ai_manager_opt._generate_with_gemini_cli("test")
        end = time.perf_counter()
        optimized_time = (end - start) / iterations
        print(f"Optimized (Direct API) avg time: {optimized_time*1000:.4f} ms")

    if optimized_time > 0:
        speedup = legacy_time / optimized_time
        print(f"Speedup factor: {speedup:.2f}x")

async def main():
    # Setup mocks for dependencies that might be missing
    mock_aiohttp = MagicMock()
    mock_aiohttp.ClientTimeout = MagicMock()

    with patch.dict(sys.modules, {
        'dotenv': MagicMock(),
        'aiohttp': mock_aiohttp
    }):
        # Clean import ensures we get a fresh module with mocks applied if needed
        if 'ai_manager' in sys.modules:
            del sys.modules['ai_manager']

        try:
            from ai_manager import AIManager
            await run_benchmark_logic(AIManager)
        except ImportError as e:
            print(f"Failed to import ai_manager: {e}")

if __name__ == "__main__":
    asyncio.run(main())
