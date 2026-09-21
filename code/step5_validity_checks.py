# -*- coding: utf-8 -*-
"""
步骤 5：信度与效度检验 (Reliability & Validity)
================================================
按课程"测度质量评估"框架，对步骤4得到的 ShortTerm 测度做四类检验：

1) 内部一致性(信度)：折半相关 —— ShortTerm_A 与 ShortTerm_B 的 Pearson 相关
   （两半词典测度高度相关，说明词典内部一致、测度稳定）。
2) 聚合效度：ShortTerm 与"已知Ground-truth潜在短视强度(true_intensity)"相关，
   以及 ShortTerm_A 与 ShortTerm_B 的相关；越高说明测度越能捕捉真实概念。
3) 区分效度：ShortTerm 与 LongTerm(长期视域测度) 的相关应为负向/偏低，
   说明"短视"与"长期主义"是两个可区分的构念。
4) 预测效度：OLS 回归
       RD_intensity = β0 + β1·ShortTerm + γ·Controls + 公司FE + 年度FE + ε
   预期 β1 < 0 且显著，验证"管理者短视主义抑制企业研发投入"的理论预期。
   （演示数据为合成且内置负向关系，真实研究请用 CSMAR 数据替换复现。）

所有结果写入 output/ 供论文"实证分析"章节引用。
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "output")


def main():
    panel = pd.read_csv(os.path.join(OUT_DIR, "panel_measure.csv"))

    # ---------- 相关性矩阵（信度/聚合/区分效度）----------
    corr_vars = ["ShortTerm", "ShortTerm_A", "ShortTerm_B", "LongTerm", "true_intensity"]
    corr = panel[corr_vars].corr(method="pearson").round(4)
    corr.to_csv(os.path.join(OUT_DIR, "validity_correlations.csv"), encoding="utf-8-sig")

    split_half = panel["ShortTerm_A"].corr(panel["ShortTerm_B"])
    conv_gt = panel["ShortTerm"].corr(panel["true_intensity"])
    disc = panel["ShortTerm"].corr(panel["LongTerm"])

    # ---------- 预测效度：OLS 回归（含公司/年度固定效应）----------
    m1 = smf.ols(
        "RD_intensity ~ ShortTerm + Size + ROA + Lev + Age + Growth + Cash",
        data=panel,
    ).fit()
    m2 = smf.ols(
        "RD_intensity ~ ShortTerm + Size + ROA + Lev + Age + Growth + Cash + C(firm_id) + C(year)",
        data=panel,
    ).fit()

    def fmt(res, fe=False):
        rows = []
        for name in res.params.index:
            if fe and (name.startswith("C(")):
                continue
            rows.append({
                "variable": name,
                "coef": round(res.params[name], 4),
                "std_err": round(res.bse[name], 4),
                "t": round(res.tvalues[name], 3),
                "p_value": round(res.pvalues[name], 4),
            })
        return pd.DataFrame(rows), res

    df1, r1 = fmt(m1)
    df2, r2 = fmt(m2, fe=True)
    df1["model"] = "M1(无FE)"
    df2["model"] = "M2(公司+年度FE)"
    reg_tbl = pd.concat([df1, df2], ignore_index=True)
    reg_tbl.to_csv(os.path.join(OUT_DIR, "regression_results.csv"),
                   index=False, encoding="utf-8-sig")

    with open(os.path.join(OUT_DIR, "validity_summary.txt"), "w", encoding="utf-8") as f:
        f.write("===== 信度与效度检验摘要 =====\n")
        f.write(f"样本量 N = {len(panel)}（{panel['firm_id'].nunique()} 家公司 × "
                f"{panel['year'].nunique()} 年）\n")
        f.write(f"[信度] 折半相关 ShortTerm_A~ShortTerm_B = {split_half:.3f}\n")
        f.write(f"[聚合效度] ShortTerm~true_intensity(已知) = {conv_gt:.3f}\n")
        f.write(f"[区分效度] ShortTerm~LongTerm = {disc:.3f}（应负向/偏低）\n")
        f.write(f"[预测效度] β1(ShortTerm, M1) = {r1.params['ShortTerm']:.3f}，"
                f"p = {r1.pvalues['ShortTerm']:.4f}\n")
        f.write(f"[预测效度] β1(ShortTerm, M2) = {r2.params['ShortTerm']:.3f}，"
                f"p = {r2.pvalues['ShortTerm']:.4f}\n")
        f.write(f"M1 R2 = {r1.rsquared:.3f}，M2 R2 = {r2.rsquared:.3f}\n")

    print(f"[步骤5] 折半信度 r={split_half:.3f}；聚合效度 r={conv_gt:.3f}；"
          f"区分效度 r={disc:.3f}")
    print(f"[步骤5] 预测效度 β1(ShortTerm)={r2.params['ShortTerm']:.3f} "
          f"(p={r2.pvalues['ShortTerm']:.4f})")
    print(f"[步骤5] 结果已写入 output/validity_*.csv 与 validity_summary.txt")


if __name__ == "__main__":
    main()
