# -*- coding: utf-8 -*-
"""
步骤 2：文本预处理 (Preprocessing)
===============================
对步骤1得到的原始语料做中文分词、去停用词、去标点数字、词性过滤，
得到"干净词序列"，供步骤3做词典特征提取。

处理要点：
  - 使用 jieba 分词（管理学研究中文文本分词主流工具）；
  - 去除标点、纯数字、长度<=1 的 token；
  - 去除停用词（dicts/stopwords.txt）；
  - 可选词性过滤：保留名词(n*)、动词(v*)，过滤虚词/标点/空格，
    以降低噪声并提升词典命中精度（与胡楠等 2021 处理思路一致）。
"""
import os
import json
import re

import jieba
from jieba import posseg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW_DIR = os.path.join(ROOT, "data", "raw_corpus")
OUT_DIR = os.path.join(ROOT, "data", "tokenized")
os.makedirs(OUT_DIR, exist_ok=True)
STOP_PATH = os.path.join(ROOT, "code", "dicts", "stopwords.txt")

# 加载停用词
with open(STOP_PATH, "r", encoding="utf-8") as f:
    STOPWORDS = set(w.strip() for w in f if w.strip())

# 允许保留的词性前缀（名词/动词为主，过滤虚词、标点、代词等噪声）
KEEP_FLAG_PREFIX = ("n", "v", "a", "i")  # 名/动/形/习语


def tokenize(text):
    tokens = []
    for w, flag in posseg.cut(text):
        w = w.strip()
        if not w:
            continue
        if re.fullmatch(r"[\s\W\d]+", w):   # 标点/空白/纯数字
            continue
        if len(w) <= 1:                       # 单字噪声
            continue
        if w in STOPWORDS:
            continue
        if flag and flag[0] not in KEEP_FLAG_PREFIX:
            continue
        tokens.append(w)
    return tokens


def main():
    inp = os.path.join(RAW_DIR, "corpus.jsonl")
    outp = os.path.join(OUT_DIR, "tokenized.jsonl")
    n = 0
    with open(inp, "r", encoding="utf-8") as fi, \
         open(outp, "w", encoding="utf-8") as fo:
        for line in fi:
            r = json.loads(line)
            toks = tokenize(r["text"])
            r["tokens"] = toks
            r["ntoken"] = len(toks)
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    print(f"[步骤2] 已完成分词与清洗：{n} 篇，输出 {outp}")


if __name__ == "__main__":
    # 关闭 jieba 日志
    jieba.setLogLevel(60)
    main()
