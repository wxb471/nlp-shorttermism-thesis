# 数据来源说明（Data Sources）

本研究的实证材料分为**文本侧**与**财务侧**两层。为完整演示NLP测度构建流程，
论文与代码默认使用结构受控的**合成演示数据**；真实研究请按下述路径获取并替换。

## 1. 文本侧：年报 MD&A 文本

| 项目 | 说明 |
|------|------|
| 真实来源 | 巨潮资讯网（www.cninfo.com.cn）——中国证监会指定信息披露网站 |
| 获取方式 | 按“公司代码 + 报告期”检索并下载年度报告 PDF；定位“管理层讨论与分析”章节正文 |
| 解析工具 | `pdfplumber` / `PyMuPDF` 抽取文本；正则定位“管理层讨论与分析”至“重要事项”文本块 |
| 字段约定 | 输出 JSONL，每行含 `firm_id`、`year`、`text` 三个字段 |
| 清洗规则 | 剔除致歉声明、表格、页眉页脚、目录；保留中文正文 |
| 演示替代 | `code/step1_corpus_acquisition.py` 内置合成语料生成器（120 家 × 5 年），可直接复用 step2~step5 |

> 其他可选文本源：交易所“互动易”问答、业绩说明会文字记录、电话会议转录（用于聚合效度中的独立短视代理）。

## 2. 财务侧：企业—年份面板

| 变量 | 真实来源 | 字段/表 |
|------|----------|---------|
| RD_intensity（研发投入强度） | 国泰安 CSMAR / Wind | 研发投入/营业收入×100 |
| Size（总资产对数） | CSMAR 公司研究 | 资产负债表-总资产，取对数 |
| ROA（总资产收益率） | CSMAR 财务指标 | 净利润/总资产 |
| Lev（资产负债率） | CSMAR 财务指标 | 总负债/总资产 |
| Age（上市年限） | CSMAR 公司研究 | 当年 - 上市年份 + 1 |
| Growth（营收增长率） | CSMAR 财务指标 | (营收_t - 营收_t-1)/营收_t-1 |
| Cash（经营现金流比率） | CSMAR 财务指标 | 经营现金流/总资产 |

演示财务面板由 `code/step4_measure_construction.py` 以“随 ShortTerm 上升而下降 + 控制变量效应 + 噪声”
的结构生成，仅用于验证理论预期的负向关系，不代表真实企业财务。

## 3. 词典来源

- 短视词典（43 词）：参考胡楠、薛付婧、王昊楠（2021）《管理者短视主义与企业创新》（管理世界）的构词思路整理，
  详见 `code/dicts/short_term_dict.txt`。
- 长期视域词典（20 词）：为区分效度检验自行整理，详见 `code/dicts/long_term_dict.txt`。
- 停用词表：通用中文停用词 + 年报高频无判别力词，详见 `code/dicts/stopwords.txt`。

## 4. 复现须知

1. 安装依赖：`pip install pandas numpy jieba statsmodels python-docx openpyxl`
2. 真实数据复现：将真实 MD&A 文本写入 `data/raw_corpus/corpus.jsonl`（字段同演示），
   将真实财务指标写入 `output/panel_measure.csv` 的对应列（或改写 step4 读取 CSMAR 导出表），
   然后运行 `python code/run_all.py` 与 `python paper/generate_docx.py` 即可重新生成全部结果与论文。

## 5. 参考文献（数据/方法）

- 胡楠, 薛付婧, 王昊楠. 管理者短视主义与企业创新[J]. 管理世界, 2021(02).
- Loughran T, McDonald B. When is a liability not a liability? Textual analysis of 10-Ks[J]. JF, 2011.
- 巨潮资讯网 https://www.cninfo.com.cn （年报原始文本）
- 国泰安 CSMAR https://www.gtarsc.com （财务与公司治理数据）
