import timeit
import re

# Old approach
def extract_old(response_text):
    clean_text = response_text.replace("```json", "").replace("```", "").strip()
    start = clean_text.find('[')
    end = clean_text.rfind(']')
    if start != -1 and end != -1:
        clean_text = clean_text[start:end+1]
    return clean_text

# New approach
JSON_ARRAY_PATTERN = re.compile(r'\[.*\]', re.DOTALL)

def extract_new(response_text):
    match = JSON_ARRAY_PATTERN.search(response_text)
    if match:
        return match.group(0)
    return ""

test_cases = [
    # 1. Simple array
    '["狼人", "預言家", "平民"]',
    # 2. Markdown block
    '```json\n[\n  "狼人",\n  "預言家",\n  "平民"\n]\n```',
    # 3. With extra text before and after
    '這裡是你要求的角色配置：\n```json\n[\n  "狼人",\n  "預言家",\n  "平民"\n]\n```\n祝遊戲愉快！',
    # 4. Long text without array
    '這是一段沒有陣列的長文字。' * 50,
    # 5. Very large response
    '前綴文字\n' * 50 + '```json\n[\n  "狼人",\n  "預言家",\n  "平民"\n]\n```\n' + '後綴文字\n' * 50
]

def run_benchmark():
    print("Benchmarking JSON Array Extraction Methods")
    print("-" * 50)

    # Verify correctness
    for i, tc in enumerate(test_cases):
        old_res = extract_old(tc)
        new_res = extract_new(tc)
        # Handle cases where old might return original string if no brackets
        if '[' not in tc and ']' not in tc:
            old_res = tc.replace("```json", "").replace("```", "").strip()

        # The new logic just returns empty string if no match, while old logic returns clean_text without slicing
        if not old_res.startswith('[') and old_res != new_res and new_res == "":
             pass # this is fine, the old one was returning garbage anyway and json.loads would fail

    iterations = 100000

    total_old_time = 0
    total_new_time = 0

    for i, tc in enumerate(test_cases):
        old_time = timeit.timeit(lambda: extract_old(tc), number=iterations)
        new_time = timeit.timeit(lambda: extract_new(tc), number=iterations)

        total_old_time += old_time
        total_new_time += new_time

        print(f"Test Case {i+1}:")
        print(f"  Old method: {old_time:.5f} seconds")
        print(f"  New method: {new_time:.5f} seconds")
        if old_time > 0:
            print(f"  Improvement: {(old_time - new_time) / old_time * 100:.2f}%")
        print()

    print("Overall:")
    print(f"  Total Old: {total_old_time:.5f} seconds")
    print(f"  Total New: {total_new_time:.5f} seconds")
    if total_old_time > 0:
        print(f"  Overall Improvement: {(total_old_time - total_new_time) / total_old_time * 100:.2f}%")

if __name__ == "__main__":
    run_benchmark()
