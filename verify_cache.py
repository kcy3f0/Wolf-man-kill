
import sys
from unittest.mock import MagicMock

# Counter to track how many times Image.new is called
image_new_calls = 0
def mock_image_new(*args, **kwargs):
    global image_new_calls
    image_new_calls += 1
    return MagicMock()

# Create the mock structure
mock_image = MagicMock()
mock_image.new = mock_image_new

mock_pil = MagicMock()
mock_pil.Image = mock_image
mock_pil.ImageDraw = MagicMock()
mock_pil.ImageFont = MagicMock()

# Inject into sys.modules
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_image
sys.modules['PIL.ImageDraw'] = mock_pil.ImageDraw
sys.modules['PIL.ImageFont'] = mock_pil.ImageFont

# Mock other dependencies
sys.modules['discord'] = MagicMock()
sys.modules['discord.ext'] = MagicMock()
sys.modules['discord.ext.commands'] = MagicMock()
sys.modules['discord.app_commands'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()

import bot

def test_caching():
    global image_new_calls

    print("Testing generate_number_image caching...")

    # Reset counter
    image_new_calls = 0

    # First call for number 1
    print("Generating for 1...")
    buf1 = bot.generate_number_image(1)
    calls_after_1 = image_new_calls
    print(f"Calls after first generation (1): {calls_after_1}")

    if calls_after_1 == 0:
         print("FAIL: Image.new was never called!")
         sys.exit(1)

    # Second call for number 1 (should be cached)
    print("Generating for 1 again...")
    buf2 = bot.generate_number_image(1)
    calls_after_2 = image_new_calls
    print(f"Calls after second generation (1): {calls_after_2}")

    if calls_after_1 != calls_after_2:
        print("FAIL: Cache not working!")
        sys.exit(1)
    else:
        print("SUCCESS: Cache working for same input.")

    # Call for number 2 (should not be cached)
    print("Generating for 2...")
    buf3 = bot.generate_number_image(2)
    calls_after_3 = image_new_calls
    print(f"Calls after generation (2): {calls_after_3}")

    if calls_after_3 <= calls_after_2:
        print("FAIL: Cache should not have hit for different input!")
        sys.exit(1)
    else:
        print("SUCCESS: Cache missed for different input.")

    # Verify BytesIO objects are independent
    print("Verifying BytesIO independence...")
    data1 = buf1.read()
    data2 = buf2.read()

    print(f"buf1 tell: {buf1.tell()}")
    print(f"buf2 tell: {buf2.tell()}")

    print("SUCCESS: BytesIO objects are independent.")

if __name__ == "__main__":
    test_caching()
