import sys
sys.path.insert(0, '.')
from src.services import markdown_export

tests = [
    'Cuộc họp: SME / mẹo & thủ thuật!?.md',
    'Normal meeting title',
    'A' * 200,
    '  ...hidden...  ',
    '',
]
results = []
for t in tests:
    r = markdown_export.sanitize_filename(t)
    results.append(f'{repr(t)[:40]} -> {repr(r)} (len={len(r)})')

with open('_test_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print("done")
