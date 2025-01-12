from janome.tokenizer import Tokenizer

# 文章を単語に分割するロジック
tokenizer = Tokenizer()

# 用意された文章
s = "朝に学校へ行って、夜に学校から帰ります。"

# 文章を単語に分割
tokens = []
for token in tokenizer.tokenize(s):
    tokens.append(token.surface)

# tokensを確認
print(tokens)

# 単語とそれを表すidを格納するものを用意
id_to_word = {}
word_to_id = {}

# 単語と単語idを格納する
for token in tokens:
    if token not in word_to_id:
        new_id = len(word_to_id)
        word_to_id[token] = new_id
        id_to_word[new_id] = token

# 結果を確認
print("words:", id_to_word)
print("ids:", word_to_id)

# 元の文章をコーパスに変換
corpus = [word_to_id[token] for token in tokens]
print("変換後の結果:", corpus)

