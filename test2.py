import re
text = "探す、ポーションを。"
text = re.sub(r'[、，。,.]+', '', text)
print(text)
