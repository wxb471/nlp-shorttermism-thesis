# -*- coding: utf-8 -*-
"""
run_all.py —— 五步流水线一键运行
===============================
依次执行：语料获取 -> 预处理 -> 特征提取 -> 测度构建 -> 信效度检验。
全部使用演示(合成)数据，开箱可复现；如需真实数据，请将
data/raw_corpus/corpus.jsonl 替换为真实 MD&A 文本（字段保持一致），
即可复用 step2~step5。

用法：
    python code/run_all.py
"""
import runpy
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    "step1_corpus_acquisition.py",
    "step2_preprocessing.py",
    "step3_feature_extraction.py",
    "step4_measure_construction.py",
    "step5_validity_checks.py",
]


def main():
    t0 = time.time()
    for i, s in enumerate(STEPS, 1):
        print(f"\n========== 步骤 {i}/5：{s} ==========")
        runpy.run_path(os.path.join(HERE, s), run_name="__main__")
    print(f"\n[完成] 全流程耗时 {time.time() - t0:.1f}s。产出见 thesis_nlp_project/output/")


if __name__ == "__main__":
    main()
