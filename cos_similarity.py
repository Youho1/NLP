# 数式計算のライブラリ
import numpy as np

def cos_similarity(x, y, epsilon=1e-8): # epsilonとは数学や科学分野などで非常に小さい数字という意味
    nx = x / (np.sqrt(np.sum(x**2)) + epsilon) # 0除算を防ぐ
    ny = y / (np.sqrt(np.sum(y**2)) + epsilon) # 0除算を防ぐ
    result = np.dot(nx, ny)
    return result
