# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 16:51
# @Author  : blue
# @Description :
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder


def find_ngrams(input_string, n):
    """将输入字符串分解为n-grams。"""
    return [''.join(grams) for grams in zip(*[input_string[i:] for i in range(n)])]


def find_frequent_patterns(strings, n, min_support=0.5):
    """使用FP-growth算法找到频繁模式。"""
    # 分解字符串为n-grams
    ngrams = [find_ngrams(string, n) for string in strings]
    print(ngrams)
    # 使用TransactionEncoder进行编码
    te = TransactionEncoder()
    te_ary = te.fit(ngrams).transform(ngrams)
    # 寻找频繁项集
    df = pd.DataFrame(te_ary, columns=te.columns_)
    frequent_patterns = fpgrowth(df, min_support=min_support, use_colnames=True)
    return frequent_patterns


# 示例字符串list
strings = ['adadadedfgdf','asdasd']

# 寻找频繁的双字母pattern
frequent_patterns = find_frequent_patterns(strings, n=3, min_support=0.8)
print(frequent_patterns)
