# 管理者短视主义对企业研发投入的影响 —— 基于年报文本的NLP测度构建（毕业论文预演稿）

> 课程：管理研究中的NLP测度构建方法  
> 提交物：论文全文（Word）、可复现代码（五步流水线）、测度结果表（企业—年份面板 CSV/Excel）、数据来源说明

本仓库完整呈现一个**可复现**的文本测度研究案例：以上市公司年报“管理层讨论与分析（MD&A）”文本为语料，
按“语料获取 → 预处理 → 特征提取 → 指标构建 → 信度与效度检验”五步法构建管理者短视主义测度（ShortTerm），
并以企业—年份面板回归检验其对研发投入的抑制作用。

## 目录结构

```
thesis_nlp_project/
├── README.md                  # 本说明
├── data_sources.md            # 数据来源与真实数据获取说明
├── code/
│   ├── run_all.py             # 一键运行五步流水线
│   ├── step1_corpus_acquisition.py   # 步骤1 语料获取（含合成演示语料生成器）
│   ├── step2_preprocessing.py        # 步骤2 分词/去噪/词性过滤
│   ├── step3_feature_extraction.py   # 步骤3 词典法特征提取
│   ├── step4_measure_construction.py # 步骤4 指标构建 + 财务面板
│   ├── step5_validity_checks.py      # 步骤5 信度/效度/回归
│   └── dicts/                 # 短视词典(43词)、长期视域词典(20词)、停用词
├── data/
│   ├── raw_corpus/corpus.jsonl      # 原始语料（演示）
│   ├── tokenized/tokenized.jsonl    # 分词后词序列
│   └── features/features.jsonl      # 词典命中特征
├── output/
│   ├── panel_measure.csv / .xlsx    # ★ 测度结果表（企业—年份面板）
│   ├── descriptive_stats.csv        # 描述性统计
│   ├── validity_correlations.csv     # 信度与效度相关矩阵
│   ├── regression_results.csv        # 回归结果
│   └── validity_summary.txt          # 检验摘要
└── paper/
    ├── 预演论文.docx          # ★ 论文全文（含封面/目录/正文/表格/参考文献）
    └── generate_docx.py       # 论文生成脚本
```

## 快速复现

```bash
pip install pandas numpy jieba statsmodels python-docx openpyxl
python code/run_all.py          # 依次跑完五步，产物写入 output/
python paper/generate_docx.py   # 由产出数据生成 Word 论文
```

随机种子已固定（`PYTHONHASHSEED=0` + 确定性哈希种子），任何机器运行均得到一致结果。

## 核心结论（演示数据）

- 短视测度 ShortTerm 均值 34.26（每千词），分布跨度大，异质性明显。
- 信度：折半相关 0.261（Spearman-Brown 校正≈0.41）；聚合效度 r=0.822；区分效度 r=-0.589。
- 预测效度：ShortTerm 对研发投入强度显著为负（β=-0.120，t=-25.65，p<0.01，含公司+年度固定效应）。

> ⚠️ 说明：为完整演示方法流程，实证部分采用**结构受控的合成演示语料**，结论方向用于验证方法可行性；
> 真实研究请按 `data_sources.md` 获取巨潮年报 + CSMAR 财务数据后替换 `data/raw_corpus/corpus.jsonl` 复现。

## 交付物清单（对应作业要求）

| 要求 | 文件 |
|------|------|
| 论文全文（Word，含封面/目录/正文/参考文献） | `paper/预演论文.docx` |
| 可复现代码（五步流水线） | `code/step1~step5.py`、`run_all.py` |
| 测度结果表（企业—年份面板 CSV/Excel） | `output/panel_measure.csv`、`.xlsx` |
| 数据来源说明 | `data_sources.md` |
