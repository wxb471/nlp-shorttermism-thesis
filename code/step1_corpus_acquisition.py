# -*- coding: utf-8 -*-
"""
步骤 1：语料获取 (Corpus Acquisition)
=====================================
研究方向：基于上市公司年报"管理层讨论与分析(MD&A)"文本，构建管理者短视主义测度。

本脚本提供两种语料来源：
  (A) 真实数据模式（需自行下载）：说明见 data_sources.md。真实流程为
      从巨潮资讯网下载年报 PDF -> 解析/定位 MD&A 章节 -> 抽取正文文本。
  (B) 演示模式（默认，开箱即复现）：生成结构受控的合成 MD&A 文本语料，
      使各公司-年度的"短视词命中强度"可由潜在参数决定，从而完整跑通后续
      五步流水线并得到符合理论预期的面板测度。

注意：演示模式用于方法教学与流水线复现，不代表真实企业数据；真实回归
请在获取 CSMAR/巨潮数据后，将 step1 输出替换为真实文本即可复用 step2-step5。
"""
import os
import json
import random
import hashlib


def _stable_int(*parts):
    """基于字符串的稳定整数种子，避免 PYTHONHASHSEED 影响复现性。"""
    s = "|".join(str(p) for p in parts)
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16) % (2**31)

# ---------- 路径配置（相对脚本所在项目根目录） ----------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW_DIR = os.path.join(ROOT, "data", "raw_corpus")
os.makedirs(RAW_DIR, exist_ok=True)

# ---------- 演示语料参数 ----------
N_FIRMS = 120          # 模拟公司数量
YEARS = [2019, 2020, 2021, 2022, 2023]
SEED = 20240921
TOKENS_PER_DOC = 520   # 每篇 MD&A 约 520 个非词典填充词（贴近真实篇幅）

# 中性（非词典）填充词库：模拟 MD&A 通用表述，避免命中短/长期词典
NEUTRAL = [
    "公司", "主业", "市场", "客户", "产品", "渠道", "产能", "供应链", "营收", "利润",
    "成本", "费用", "现金流", "资产", "负债", "团队", "员工", "技术", "研发", "质量",
    "服务", "品牌", "区域", "海外", "国内", "行业", "政策", "环境", "风险", "机遇",
    "项目", "投资", "并购", "整合", "协同", "效率", "管理", "治理", "合规", "披露",
    "股东", "利益", "价值", "目标", "规划", "布局", "推进", "落实", "优化", "创新",
    "生产", "销售", "采购", "库存", "物流", "网络", "平台", "数据", "系统", "流程",
    "标准", "体系", "能力", "资源", "资本", "信用", "汇率", "利率", "价格", "需求",
]
# 合成句子骨架（含占位，用于拼接出连贯中文）
TEMPLATES = [
    "报告期内，{a}围绕既定经营计划，{b}推进各项业务，整体运行平稳。",
    "面对复杂多变的外部环境，{a}坚持聚焦主业，持续{b}提升核心竞争力。",
    "本年度{a}优化产品结构，{b}拓展市场空间，经营质量稳步改善。",
    "公司董事会认为，{a}所处行业景气温和修复，{b}加强内部精细化管理。",
    "展望后续，{a}将把握产业升级机遇，{b}巩固既有客户合作关系。",
    "在成本控制方面，{a}通过精益管理，{b}降低综合运营费用水平。",
    "人才队伍建设上，{a}完善激励机制，{b}吸引并保留核心技术骨干。",
]


def build_doc(firm_id, year, intensity):
    """
    intensity: 潜在短视强度（短视词每千词基准命中率，范围约 6~60）。
    返回 (text, meta) —— meta 记录真实注入强度，便于步骤5做"已知信效度"对照。
    """
    rnd = random.Random(_stable_int(firm_id, year, SEED))
    short_target = intensity * TOKENS_PER_DOC / 1000.0   # 期望注入短视词数（intensity=每千词）
    long_target = max(0.0, (50.0 - intensity * 0.6) * TOKENS_PER_DOC / 1000.0)  # 与短视负相关

    SHORT_WORDS = ["短期内", "尽快", "立刻", "马上", "眼前", "当前", "当下", "短期",
                   "及时", "快速", "加速", "加快", "抓紧", "尽早", "立即", "赶紧",
                   "即刻", "迅即", "从速", "亟需", "亟待", "火速", "速即", "旋即",
                   "急功近利", "急于求成", "短平快", "迅速", "突击", "仓促"]
    LONG_WORDS = ["长远", "长期", "持久", "可持续", "战略", "远景", "未来", "愿景",
                  "夯实", "积淀", "厚积薄发", "久久为功", "行稳致远", "基业长青",
                  "长期主义", "稳健", "深耕", "远见", "持久战", "百年"]

    sentences = []
    n_sent = 16
    for i in range(n_sent):
        tpl = TEMPLATES[(i + firm_id) % len(TEMPLATES)]
        a = NEUTRAL[(firm_id * 3 + i) % len(NEUTRAL)]
        b = NEUTRAL[(firm_id * 5 + i + 2) % len(NEUTRAL)]
        sentences.append(tpl.format(a=a, b=b))

    # 均匀注入短视/长期词，使文本自然且可被 jieba 切出这些词
    def inject(words, count):
        for _ in range(int(round(count))):
            if not sentences:
                break
            w = rnd.choice(words)
            idx = rnd.randint(0, len(sentences) - 1)
            sentences[idx] = sentences[idx].replace("，", f"，{w}地", 1) if "，" in sentences[idx] else w + "地" + sentences[idx]

    inject(SHORT_WORDS, short_target)
    inject(LONG_WORDS, long_target)

    text = "".join(sentences)
    meta = {
        "firm_id": f"F{firm_id:04d}",
        "year": year,
        "true_intensity": round(float(intensity), 3),
        "source": "demo_synthetic",
    }
    return text, meta


def main():
    rnd = random.Random(SEED)
    records = []
    for firm_id in range(1, N_FIRMS + 1):
        # 每个公司给定一个稳定的潜在短视水平（个体异质性），单位：短视词/千词
        base = rnd.uniform(8.0, 55.0)
        for year in YEARS:
            # 年度波动：轻微漂移 + 噪声
            drift = (year - 2019) * rnd.uniform(-1.5, 2.0)
            intensity = max(4.0, base + drift + rnd.gauss(0, 4.0))
            text, meta = build_doc(firm_id, year, intensity)
            meta["text"] = text
            records.append(meta)

    out_path = os.path.join(RAW_DIR, "corpus.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[步骤1] 已生成演示语料：{len(records)} 篇（{N_FIRMS} 家公司 × {len(YEARS)} 年）")
    print(f"[步骤1] 输出文件：{out_path}")


if __name__ == "__main__":
    main()
