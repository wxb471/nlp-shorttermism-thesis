# -*- coding: utf-8 -*-
"""
步骤 4：测度构建 (Measure Construction)
======================================
将步骤3的词典命中数转化为"企业-年度"面板测度，并构造配套的财务面板
（含被解释变量与 controls），供步骤5做信效度与预测效度检验。

短视测度定义（每千词短视词典命中数，标准化、可比）：
    ShortTerm_{i,t} = (short_hits_{i,t} / ntoken_{i,t}) * 1000

该定义与胡楠等(2021)等研究一致：以"相对词频"而非绝对词数衡量文本倾向，
消除篇幅差异。取值范围为正，数值越大代表管理层讨论越偏向短期视域。

配套财务面板（演示）：以真实研究中常见来源（CSMAR/Wind）的变量为模板，
在演示中由可控随机过程生成，并令 RD_intensity 与 ShortTerm 呈负向关系，
以验证"短视主义抑制研发投入"的理论预期。真实研究请用 CSMAR 数据替换。
"""
import os
import json
import hashlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FEAT_DIR = os.path.join(ROOT, "data", "features")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(OUT_DIR, exist_ok=True)


def _seed(*parts):
    s = "|".join(str(p) for p in parts)
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16) % (2**31)


def main():
    rows = []
    with open(os.path.join(FEAT_DIR, "features.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    df = pd.DataFrame(rows)
    # 核心测度：每千词短视命中数
    df["ShortTerm"] = df["short_hits"] / df["ntoken"] * 1000.0
    df["ShortTerm_A"] = df["short_hits_a"] / df["ntoken"] * 1000.0
    df["ShortTerm_B"] = df["short_hits_b"] / df["ntoken"] * 1000.0
    df["LongTerm"] = df["long_hits"] / df["ntoken"] * 1000.0

    # ---- 构造演示财务面板（与 ShortTerm 负相关的 RD_intensity 等）----
    rng = np.random.default_rng(_seed("finance", 20240921))
    n = len(df)
    size = rng.normal(22.0, 1.2, n)
    roa = rng.normal(0.04, 0.04, n)
    lev = np.clip(rng.normal(0.45, 0.18, n), 0.05, 0.95)
    age = rng.integers(1, 26, n).astype(float)
    growth = rng.normal(0.12, 0.20, n)
    cash = rng.normal(0.05, 0.05, n)

    # 被解释变量：研发投入强度(%)。理论：短视 → 研发↓ + 控制变量效应 + 噪声
    rd = (16.0
          - 0.12 * df["ShortTerm"].values
          + 0.6 * (size - 22.0)
          + 8.0 * roa
          - 1.5 * (lev - 0.45)
          - 0.05 * (age - 13.0)
          + 1.2 * growth
          + 3.0 * cash
          + rng.normal(0.0, 1.2, n))
    rd = np.clip(rd, 0.5, 28.0)

    df["RD_intensity"] = rd
    df["Size"] = size
    df["ROA"] = roa
    df["Lev"] = lev
    df["Age"] = age
    df["Growth"] = growth
    df["Cash"] = cash

    # 整理列顺序
    cols = ["firm_id", "year", "ntoken", "short_hits", "long_hits",
            "ShortTerm", "ShortTerm_A", "ShortTerm_B", "LongTerm",
            "RD_intensity", "Size", "ROA", "Lev", "Age", "Growth", "Cash",
            "true_intensity", "source"]
    panel = df[cols].copy()
    panel = panel.round(4)

    csv_path = os.path.join(OUT_DIR, "panel_measure.csv")
    xlsx_path = os.path.join(OUT_DIR, "panel_measure.xlsx")
    panel.to_csv(csv_path, index=False, encoding="utf-8-sig")
    panel.to_excel(xlsx_path, index=False)

    # 描述性统计
    desc = panel[["ShortTerm", "LongTerm", "RD_intensity", "Size",
                  "ROA", "Lev", "Age", "Growth", "Cash"]].describe().round(4)
    desc.to_csv(os.path.join(OUT_DIR, "descriptive_stats.csv"), encoding="utf-8-sig")

    print(f"[步骤4] 已构建企业-年度面板测度：{len(panel)} 行，"
          f"{panel['firm_id'].nunique()} 家公司 × {sorted(panel['year'].unique())}")
    print(f"[步骤4] 输出：{csv_path}")
    print(f"[步骤4] 描述性统计：{os.path.join(OUT_DIR, 'descriptive_stats.csv')}")
    print(f"[步骤4] ShortTerm 均值={panel['ShortTerm'].mean():.3f}，"
          f"标准差={panel['ShortTerm'].std():.3f}")


if __name__ == "__main__":
    main()
