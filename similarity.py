from co_matrix import create_co_matrix
from cos_similarity import cos_similarity
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

# 単語とその単語を表すidを格納するものを用意
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

# 共起行列を作る
vocab_size = len(word_to_id)
count_size = 1
co_matrix = create_co_matrix(corpus, vocab_size, count_size)

# 単語「朝」の単語ベクトル
morning = co_matrix[word_to_id['朝']]
# 単語「夜」の単語ベクトル
night = co_matrix[word_to_id['夜']]

# 類似度計算
similarity = cos_similarity(morning, night)

# 結果を確認
print("similarity:", similarity)