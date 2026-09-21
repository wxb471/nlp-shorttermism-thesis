# -*- coding: utf-8 -*-
"""
步骤 3：特征提取 (Feature Extraction / Dictionary Method)
=========================================================
采用"词典法（Dictionary / Lexicon Approach）"从清洗后的词序列中提取
管理者短视主义相关特征。词典法优点是透明、可解释、可复现，是管理学中
文本测度构建的常用基线方法（参考 Loughran & McDonald 情感词典、
胡楠等 2021 短视词典思路）。

本步骤输出每个文档的：
  - short_hits : 短视词典命中词数（全词典）
  - short_hits_a / short_hits_b : 将短视词典随机等分两半后的命中数（用于折半信度）
  - long_hits  : 长期视域词典命中词数（用于区分效度）

说明：本流水线同时给出"有监督法/词嵌入法"的扩展接口注释，便于后续替换。
"""
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOK_DIR = os.path.join(ROOT, "data", "tokenized")
OUT_DIR = os.path.join(ROOT, "data", "features")
os.makedirs(OUT_DIR, exist_ok=True)

SHORT_DICT = os.path.join(ROOT, "code", "dicts", "short_term_dict.txt")
LONG_DICT = os.path.join(ROOT, "code", "dicts", "long_term_dict.txt")


def load_dict(path):
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


def main():
    short_words = load_dict(SHORT_DICT)
    long_words = load_dict(LONG_DICT)
    short_set = set(short_words)
    long_set = set(long_words)

    # 折半：将短视词典按奇偶序分成 A/B 两组
    a_set = set(short_words[0::2])
    b_set = set(short_words[1::2])

    inp = os.path.join(TOK_DIR, "tokenized.jsonl")
    outp = os.path.join(OUT_DIR, "features.jsonl")
    with open(inp, "r", encoding="utf-8") as fi, \
         open(outp, "w", encoding="utf-8") as fo:
        for line in fi:
            r = json.loads(line)
            toks = r["tokens"]
            sa = sum(1 for t in toks if t in a_set)
            sb = sum(1 for t in toks if t in b_set)
            sl = sum(1 for t in toks if t in long_set)
            r["short_hits_a"] = sa
            r["short_hits_b"] = sb
            r["short_hits"] = sa + sb
            r["long_hits"] = sl
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[步骤3] 词典法特征提取完成：短视词典 {len(short_words)} 词，长期词典 {len(long_words)} 词")
    print(f"[步骤3] 输出 {outp}")


if __name__ == "__main__":
    main()
