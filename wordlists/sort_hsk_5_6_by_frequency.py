"""
Sort HSK 5 and HSK 6 vocabulary by estimated frequency of usage.

Approach: use HSK 1-4 word lists as a reference corpus. Each Chinese
character gets a score based on the LOWEST HSK level it appears in
(HSK 1-2 → 4, HSK 3 → 3, HSK 4 → 2, otherwise → 0). A word's frequency
score is the sum of its character scores; ties broken by word length
(shorter first) and then original order. This captures the reasonable
heuristic that words built from common characters tend to be more common.

Not a substitute for a real corpus frequency list (BCC, SUBTLEX-CH), but
produces a usable rough ordering without external data.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
HSK_5 = ROOT / "hsk_5.txt"
HSK_6 = ROOT / "hsk_6.txt"

HSK_1 = ROOT / "hsk_1.txt"
HSK_2 = ROOT / "hsk_2.txt"
HSK_3 = ROOT / "hsk_3.txt"
HSK_4 = ROOT / "hsk_4.txt"


def read_word_rows(path, has_header=False):
    """Yield (idx, chinese, pinyin, english) tuples. Tolerant of format quirks."""
    rows = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if has_header and i == 0:
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            # First column may be blank in some rows; fall back to line number.
            try:
                idx = int(parts[0].strip())
            except ValueError:
                idx = i
            chinese = parts[1].strip()
            pinyin = parts[2]
            english = parts[3]
            rows.append((idx, chinese, pinyin, english))
    return rows


def build_char_scores():
    """Map each CJK character to a score: higher = more common."""
    score = {}

    def assign(rows, value):
        for _, chinese, *_ in rows:
            for ch in chinese:
                if '\u4e00' <= ch <= '\u9fff':
                    # Keep the highest score ever assigned (i.e. lowest HSK level).
                    if score.get(ch, 0) < value:
                        score[ch] = value

    # Apply lowest level last so highest score wins via the `if` above.
    # HSK 5/6 characters get a small baseline so words made of them still
    # rank against each other, rather than all collapsing to zero.
    assign(read_word_rows(HSK_6), 0.5)
    assign(read_word_rows(HSK_5), 1.0)
    assign(read_word_rows(HSK_4), 2.0)
    assign(read_word_rows(HSK_3, has_header=True), 3.0)
    assign(read_word_rows(HSK_2), 4.0)
    assign(read_word_rows(HSK_1), 4.0)
    return score


# Hand-placed top tiers — words I can confidently say are very common in
# modern Mandarin, placed at the front regardless of character-score.
HSK_5_TOP = [
    # Core connectors, modals, discourse markers
    "其实", "然后", "其他", "其余", "实在", "实际", "实现", "实行", "实话", "实在",
    "显得", "显然", "因而", "从而", "从此", "以及", "以来", "以免", "以上", "以下",
    "反而", "反正", "反映", "反应", "反复", "何必", "何况", "难怪", "至于",
    "似乎", "简直", "毕竟", "到底", "究竟", "始终", "果然", "居然", "竟然",
    "于是", "否则", "不论", "不如", "不要紧", "与其", "只得", "只不过",
    "总之", "总算", "总共", "总是", "必须", "必要", "必然", "曾经",
    "按", "凭", "靠", "依", "趁", "朝", "向", "至", "自",
    "及", "乃至", "万一", "此外", "此时", "此刻", "此事",
    # Very common abstract/functional
    "观点", "原则", "方式", "方针", "趋势", "结构", "系统", "制度", "体系",
    "功能", "作用", "影响", "效率", "能源", "资源", "资金", "资料", "资本",
    "成果", "成就", "成立", "成分", "成员", "成熟", "形式", "形成", "形象",
    "形势", "意义", "意识", "意图", "意志", "道德", "道理", "规模", "规矩",
    "规则", "范围", "范畴", "程度", "程序", "状况", "状态", "现象", "现状",
    "现代", "现实", "现场", "实力", "实质", "实施", "实验", "实习",
    "条例", "规律", "原理", "原则", "原始", "原先", "过分", "过度", "过期",
    "矛盾", "冲突", "困惑", "疑问", "问题", "事实", "事件", "事物", "事业",
    # Common verbs / actions
    "采取", "采用", "构成", "形成", "组成", "造成", "产生", "创造", "制造",
    "创新", "改革", "改进", "改善", "发挥", "发表", "发布", "发动", "发扬",
    "实施", "实行", "进展", "进步", "进一步", "进入", "推广", "推动", "推进",
    "保持", "保留", "保存", "保卫", "维持", "维护", "维修", "控制",
    "掌握", "把握", "承担", "承认", "承受", "承诺", "接触", "接待", "接近",
    "连接", "连续", "集中", "集合", "达到", "实现", "体现", "表现",
    "表达", "反映", "证实", "展开", "展览", "展示", "显示", "显然",
    "体验", "体会", "感受", "经历", "经受", "培养", "训练", "培训",
    "从事", "投入", "参与", "参考", "参照", "涉及", "涵盖", "包括", "包含",
    "符合", "相当", "相对", "相应", "相似", "相关", "合作", "配合",
    "赞成", "赞同", "赞美", "鼓掌", "支持", "反对", "抵抗", "拒绝",
    # Common adjectives
    "明显", "明确", "明白", "清楚", "清晰", "清洁", "清醒", "清新",
    "重要", "必要", "主要", "次要", "基本", "根本", "全面", "全体",
    "整个", "整体", "部分", "全部", "某", "某些", "某种",
    "优秀", "优点", "优势", "优先", "先进", "高级", "高档", "高档",
    "一致", "一同", "一律", "一向", "一概", "一再", "一心",
    "各种", "各自", "各地", "各式各样", "每逢", "每当",
    "大量", "大批", "大型", "大多", "大多数", "少数",
    # Common nouns - people/society/time
    "人士", "人口", "人类", "人员", "人物", "人才", "人格", "人生",
    "公民", "公众", "群众", "居民", "农民", "工人", "学者", "专家",
    "政府", "政治", "政策", "政党", "党员", "领导", "领袖", "主任",
    "主席", "主任", "委员", "代表", "代理", "官员", "当局",
    "社会", "社区", "国家", "国民", "国王", "民族", "民间", "民主",
    "经济", "市场", "企业", "公司", "商业", "工业", "农业", "产业",
    "生产", "消费", "投资", "投入", "成本", "价值", "价格", "成本",
    "时代", "时期", "时刻", "时光", "时尚", "时机", "时事", "时常",
    "年代", "年度", "季节", "时节", "场合", "场所", "地区", "地带",
    # Modern life
    "网络", "网上", "信息", "通讯", "通信", "资讯", "媒体", "媒介",
    "新闻", "报道", "报纸", "杂志", "电视", "广播", "宣传", "广告",
    "文明", "文化", "传统", "现代化", "国际化", "全球", "全球化",
    "环境", "生态", "自然", "天然", "保护", "保育", "资源", "能源",
    "污染", "清洁", "治理", "改造", "建设", "发展",
    "健康", "疾病", "病人", "医疗", "医生", "护理", "治疗", "病毒",
    "安全", "危险", "风险", "威胁", "紧急", "急救", "事故", "灾害",
    # Common feelings / states
    "情绪", "心理", "精神", "感情", "感觉", "感受", "体会", "感想",
    "态度", "观念", "思想", "思路", "理念", "理论", "学说", "主张",
    "习惯", "传统", "风俗", "礼节", "风格", "特色", "特点", "特征",
    "水平", "程度", "范围", "限度", "界限", "标准", "指标",
    "能力", "水平", "本领", "技能", "技巧", "本事", "才能", "才华",
    # Very common spoken
    "的话", "似的", "一般", "一直", "一旦", "一度", "往往", "常常",
    "经常", "平常", "日常", "随时", "即时", "及时", "当场", "当前",
    "如今", "目前", "近来", "最近", "从前", "以前", "过去", "将来",
    # Common words made of HSK-5-exclusive characters (heuristic under-rates these)
    "欣赏", "逐渐", "遵守", "遗憾", "英雄", "限制", "挑战", "咨询", "装饰",
    "宿舍", "坦率", "逃避", "叙述", "犹豫", "粘贴", "出版", "出色", "初级",
    "创业", "创作", "出席", "辞职", "刺激", "辞典", "促进", "催", "达成",
    "打喷嚏", "大方", "代替", "耽误", "导致", "独立", "独特", "对比", "对待",
    "对手", "对象", "队伍", "兑换", "恶劣", "耳环", "发愁", "发达", "发抖",
    "发挥", "发明", "分别", "分布", "分配", "风险", "否认", "服装", "辅导",
    "妇女", "改革", "改善", "感激", "干燥", "高档", "高级", "个别", "个人",
    "个性", "根据", "工程师", "公布", "公平", "姑姑", "姑娘", "鼓舞", "古典",
    "古代", "股票", "骨头", "挂号", "观察", "观点", "光滑", "光临", "光明",
    "光盘", "灰", "灰尘", "灰心", "恢复", "汇率", "婚礼", "婚姻", "活跃",
    "急忙", "急诊", "集合", "集体", "疾病", "寂寞", "夹子", "简历", "建立",
    "建设", "建筑", "健身", "讲究", "交换", "交际", "角度", "教材", "教练",
    "结构", "结合", "结论", "结实", "接触", "戒指", "经典", "经营", "精力",
    "精神", "景色", "救", "居然", "具备", "具体", "俱乐部", "绝对", "角色",
    "军事", "均匀", "看不起", "看望", "靠", "颗", "可见", "可靠", "可怕",
    "克服", "客观", "课程", "空间", "空闲", "宽", "矿产", "昆虫", "扩大",
    "辣椒", "老百姓", "老板", "乐观", "类型", "冷淡", "离婚", "理论", "利润",
    "利益", "利用", "连忙", "联合", "恋爱", "良好", "粮食", "了不起", "临时",
    "灵活", "铃", "领导", "领域", "浏览", "陆地", "陆续", "录取", "录音",
    "落后", "骂", "馒头", "猫头鹰", "媒体", "煤炭", "美术", "魅力", "梦想",
    "秘密", "秘书", "密切", "棉花", "面对", "面积", "面临", "苗条", "描写",
    "敏感", "名牌", "名片", "名胜", "命令", "命运", "模仿", "模糊", "模特",
    "摩托车", "陌生", "目标", "目录", "哪怕", "难怪", "脑袋", "内部", "内科",
    "嫩", "能干", "能源", "年代", "念", "宁静", "农村", "农民", "浓", "女士",
    "偶然", "派", "盼望", "陪伴", "培训", "培养", "赔偿", "佩服", "配合",
    "盆", "碰见", "批", "批准", "披", "疲劳", "匹", "骗", "片", "片面",
    "频道", "平", "平安", "平等", "平方", "平衡", "平静", "平均", "评价",
    "凭", "迫切", "破产", "破坏", "迫不及待",
]

HSK_6_TOP = [
    # Common higher-register / literary connectors
    "何况", "况且", "姑且", "倘若", "若干", "乃至", "以便", "以致", "以至",
    "反之", "反倒", "毋宁", "宁可", "宁愿", "与否", "无非", "未免", "未必",
    "未尝", "索性", "不止", "不料", "岂不", "莫非", "难免", "从容", "从而",
    "而已", "而言", "就此", "就是说", "由此", "至今", "至于", "顷刻", "片刻",
    "一旦", "一度", "一向", "一律", "一概", "一心", "一举", "一贯",
    "凡是", "凡事", "比方", "比如说", "例如",
    # High-frequency abstracts
    "局面", "局势", "局限", "格局", "结局", "构造", "构思", "构想",
    "原本", "本质", "根源", "根据", "依据", "凭借", "借助", "借此",
    "来源", "起源", "起初", "末端", "开端", "始终", "终究", "终于",
    "倾向", "趋向", "走向", "导致", "引发", "引导", "主导", "主宰",
    "操纵", "操控", "掌控", "控制", "支配", "支撑", "支援",
    "秩序", "次序", "顺序", "先后", "优先", "优劣", "长短",
    "比重", "比例", "规模", "幅度", "力度", "密度", "强度",
    # Common content
    "普及", "涉及", "涉足", "牵涉", "牵扯", "关联", "关系", "联合",
    "结合", "综合", "整合", "融合", "合并", "兼并", "配备", "配套",
    "形态", "形式", "内涵", "外延", "外表", "表象", "本身", "本能",
    "本性", "本意", "实质", "实际上", "本来", "原来", "起先",
    "基础", "前提", "先决", "条件", "要素", "因素", "成分", "元素",
    "环节", "关节", "环境", "气氛", "氛围", "场面", "情形", "情境",
    # Common higher verbs
    "弘扬", "发扬", "推行", "践行", "履行", "遵守", "遵循", "依照",
    "依赖", "依靠", "仰赖", "仰仗", "寄托", "寄予", "给予", "赋予",
    "授予", "传授", "传承", "继承", "接替", "替换", "取代", "替代",
    "恢复", "复原", "复兴", "兴起", "兴盛", "兴衰", "衰退", "衰落",
    "盛行", "流行", "风行", "普及", "传播", "散布", "分散", "分布",
    # Abstract adjectives
    "显著", "明显", "鲜明", "突出", "杰出", "卓越", "优越", "优异",
    "巨大", "庞大", "浩大", "宏大", "宏伟", "壮丽", "辉煌",
    "深刻", "深远", "长远", "久远", "永恒", "永久", "持久", "长期",
    "严峻", "严厉", "严密", "周密", "周到", "周全", "完善", "完备",
    "精确", "精密", "精细", "细致", "细腻", "微妙", "奥妙", "巧妙",
]


def parse_level_file(path):
    return read_word_rows(path)


def main():
    char_score = build_char_scores()

    for label, path, top in [("HSK 5", HSK_5, HSK_5_TOP), ("HSK 6", HSK_6, HSK_6_TOP)]:
        rows = parse_level_file(path)
        # Score each entry.
        headwords = {r[1] for r in rows}

        # Hand-placed front tier: assign sequential high scores.
        manual_rank = {}
        for i, w in enumerate(top):
            if w in headwords and w not in manual_rank:
                manual_rank[w] = i

        def freq_score(chinese):
            total = 0
            hits = 0
            for ch in chinese:
                if '\u4e00' <= ch <= '\u9fff':
                    total += char_score.get(ch, 0)
                    hits += 1
            # Avg char score (so 2- and 4-char words are comparable), then add
            # a small bonus for shorter words.
            avg = total / hits if hits else 0
            length_bonus = max(0, 4 - len(chinese)) * 0.05
            return avg + length_bonus

        def sort_key(row):
            idx, chinese, pinyin, english = row
            if chinese in manual_rank:
                # Manual entries beat all heuristic entries.
                return (0, manual_rank[chinese], idx)
            return (1, -freq_score(chinese), idx)

        rows.sort(key=sort_key)

        out = path.with_name(path.stem + "_by_frequency.txt")
        with out.open("w", encoding="utf-8") as f:
            for new_rank, (orig_idx, chinese, pinyin, english) in enumerate(rows, 1):
                f.write(f"{new_rank}\t{orig_idx}\t{chinese}\t{pinyin}\t{english}\n")

        placed = sum(1 for w in top if w in headwords)
        print(f"{label}: wrote {len(rows)} entries to {out.name}  "
              f"(hand-placed top: {placed} / {len(top)})")


if __name__ == "__main__":
    main()
