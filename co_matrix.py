import numpy as np
from janome.tokenizer import Tokenizer

def create_co_matrix(corpus, vocab_size, count_size=1):
    corpus_size = len(corpus)
    # 共起行列の形はvocab_size x vocab_size
    co_matrix = np.zeros((vocab_size, vocab_size))

    # コーパスの最初の単語から
    for idx, word_id in enumerate(corpus):
        # カウントする単語のサイズ
        for i in range(1, count_size+1):
            # 左へカウントする
            left_idx = idx - i
            # 右へカウントする
            right_idx = idx + i

            # 左のインデックスは0より小さいことは許されない
            if left_idx < 0:
                pass
            # 単語をカウントする
            else:
                # 左の単語のidを取得
                left_word_id = corpus[left_idx]
                # 現在の単語から左の単語のidをカウントする (行列はmatrix[y][x]のように格納される)
                co_matrix[word_id, left_word_id] += 1
            # 右のインデックスはコーパスの最後の単語のインデックスより大きいことは許されない
            if right_idx > (corpus_size - 1):
                pass
            else:
                # 右の単語のidを取得
                right_word_id = corpus[right_idx]
                # 現在の単語から右の単語のidをカウントする (行列はmatrix[y][x]のように格納される)
                co_matrix[word_id, right_word_id] += 1

    # 作った共起行列をリターン
    return co_matrix

def main():
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

    vocab_size = len(word_to_id)
    count_size = 1
    co_matrix = create_co_matrix(corpus, vocab_size, count_size)
    print("共起行列:")
    print(co_matrix)

if __name__ == "__main__":
    main()
