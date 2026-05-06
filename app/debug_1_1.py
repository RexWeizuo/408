import re
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'OS_quiz', '1.1.md')
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Try simpler pattern
pattern = r'(\d+)\.\s+\*\*(.+?)\*\*'
matches = re.findall(pattern, content)
print(f'Found {len(matches)} question headers:')
for num, title in matches[:15]:
    print(f'  {num}. {title}')

# Check if the file has the expected format
# Questions start with "  1. **title**:"
q_blocks = re.findall(r'(\d+)\.\s+\*\*([^*]+)\*\*[:\uff1a]', content)
print(f'\nQuestions with colon: {len(q_blocks)}')
for num, title in q_blocks:
    print(f'  {num}. {title}')
