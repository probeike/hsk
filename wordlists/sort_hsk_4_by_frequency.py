"""
Sort HSK 4 vocabulary by estimated frequency of usage in modern Mandarin.

Ordering reflects general-purpose Chinese corpus frequency (written + spoken,
roughly aligned with BCC / SUBTLEX-CH style rankings) based on the
assistant's judgement. Function words, connectors and broad abstract content
sit near the top; concrete or specialised vocabulary sits lower.
"""

from pathlib import Path

SRC = Path(__file__).parent / "hsk_4.txt"
DST = Path(__file__).parent / "hsk_4_by_frequency.txt"

# Ranked list of HSK 4 headwords, from most → least frequent (by estimate).
# Each string must match the Chinese column in hsk_4_words.txt EXACTLY,
# including any trailing spaces ("棒 ", "百分之 ", "互联网 ", "左右 ").
RANKED = [
    # -- Tier 1: function words, connectors, discourse markers --
    "可是", "不过", "却", "而", "并且", "因此", "由于", "于是", "然而", "否则",
    "不仅", "既然", "尽管", "即使", "不管", "无论", "要是", "只要", "只好",
    "不得不", "得（助动词）", "以", "与", "之", "其中", "所有", "全部",
    "部分", "各", "任何", "一切", "另外", "以为", "也许", "大概", "大约",
    "左右 ", "差不多", "挺", "十分", "完全", "重新", "本来", "原来", "刚",
    "甚至", "仍然", "确实", "竟然", "究竟", "到底", "到处", "从来", "当",
    "当时", "偶尔", "往往", "首先", "其次", "接着", "同时", "平时", "随着",
    "随便", "稍微", "互相", "共同", "是否", "连", "由",

    # -- Tier 2: broad abstract verbs / state (very high usage) --
    "生活", "感觉", "发生", "发展", "出现", "继续", "进行", "改变", "使用",
    "接受", "成为", "成功", "通过", "表示", "说明", "理解", "考虑", "使",
    "受到", "获得", "提供", "提醒", "提前", "提", "引起", "支持", "反对",
    "批评", "禁止", "鼓励", "感动", "同情", "保护", "保证", "坚持", "联系",
    "等 （动）", "行", "敢", "负责", "麻烦", "著名", "有趣",
    "交流", "合适", "合格", "适合", "适应", "直接", "相同", "相反", "真正",
    "正确", "正常", "正好", "正式", "至少", "主意", "决定".replace("决定", "坚持"),

    # -- Tier 3: core abstract nouns --
    "经济", "社会", "经验", "经历", "活动", "过程", "内容", "情况", "方法",
    "方面", "方向", "条件", "结果", "原因", "目的", "效果", "作用", "关键",
    "能力", "技术", "信息", "消息", "知识", "教育", "研究", "科学", "艺术",
    "法律", "国际", "民族", "世纪", "生命", "地球", "自然", "气候", "温度",
    "速度", "压力", "空气", "阳光", "海洋", "数字", "数量", "距离", "周围",
    "地点", "地址", "号码", "密码", "看法", "意见", "建议", "态度", "性格",
    "脾气", "印象", "心情", "爱情", "感情", "友谊", "友好", "理想", "将来",
    "回忆", "计划", "任务", "规定", "管理", "责任", "通知", "证明", "解释",
    "阅读", "准确", "判断", "调查", "估计", "怀疑", "熟悉",

    # -- Tier 4: high-frequency daily verbs & adjectives --
    "感谢", "祝贺", "原谅", "道歉", "抱歉", "打扰", "邀请", "陪", "留", "交",
    "寄", "收", "取", "存", "够", "满", "缺少", "缺点", "优点", "优秀",
    "精彩", "丰富", "复杂", "详细", "严格", "严重", "普遍", "流行", "重点",
    "重视", "值得", "符合", "肯定", "实在", "实际", "总结", "整理", "收拾",
    "安排", "参观", "举办", "举行", "举", "抬", "推", "拉", "挂", "敲",
    "指", "掉", "丢", "扔", "戴", "脱", "抱", "躺", "醒", "响", "剩",
    "赶", "输", "赢", "弄", "转", "赚", "租", "擦", "猜", "尝", "骗",

    # -- Tier 5: emotion / personality / trait --
    "开心", "愉快", "轻松", "紧张", "激动", "兴奋", "难受", "失望", "伤心",
    "后悔", "害羞", "吃惊", "骄傲", "勇敢", "冷静", "活泼", "浪漫", "幽默",
    "诚实", "辛苦", "懒", "笨", "帅", "美丽", "可怜", "可惜", "厉害",
    "顺便", "顺利", "顺序", "按时", "按照", "千万", "恐怕", "难道",
    "粗心", "马虎", "仔细", "耐心", "自信", "得意", "幸福", "困", "困难",
    "故意", "礼貌", "流利", "富", "穷", "座位", "味道", "小吃",
    "烦恼", "无聊", "孤单".replace("孤单", "无聊"), "暖和", "凉快", "热闹",

    # -- Tier 6: concrete daily-life nouns --
    "空", "光", "梦", "火", "云", "汗", "毛", "盐", "糖", "汤", "酸",
    "辣", "咸", "苦", "香", "假", "低", "底", "厚", "轻", "重", "深",
    "短信", "对话", "词语", "文章", "小说", "杂志", "页", "篇", "节",
    "信封", "信心", "答案", "错误",
    "工资", "奖金", "收入", "现金", "零钱", "价格", "付款", "打折", "免费",
    "购物", "顾客", "售货员", "商量", "生意", "招聘", "应聘", "申请",
    "加班", "出差", "出发", "出生", "毕业", "报名", "登机牌", "签证",

    # -- Tier 7: roles / people / relationships --
    "动作", "表演", "表扬", "表格", "演出", "演员", "观众", "记者", "警察",
    "律师", "教授", "硕士", "博士", "大夫", "护士", "师傅", "作家", "作者",
    "房东", "孙子", "亲戚", "儿童", "小伙子", "俩", "咱们", "父亲", "母亲",
    "专业", "专门", "职业", "公里", "功夫", "力气", "年龄", "性别", "国籍",
    "首都", "省", "郊区",

    # -- Tier 8: daily actions / services / more verbs --
    "翻译", "复印", "打印", "打扮", "打招呼", "打针", "抽烟", "养成",
    "降低", "降落", "减少", "减肥", "增加", "超过", "推迟", "停", "吸引",
    "积累", "积极", "及时", "节约", "浪费", "误会", "破", "乱", "脏",
    "对面", "对于", "比如", "例如", "尤其", "特点", "区别", "好处", "好像",
    "倒", "无", "逛",
    "样子", "景色", "场", "座", "台", "趟", "倍", "遍", "份", "秒", "棵",
    "棒 ", "百分之 ", "材料", "质量", "内",

    # -- Tier 9: themed lexicon (food, home, objects, travel) --
    "饺子", "包子", "饼干", "葡萄", "果汁", "巧克力", "烤鸭", "矿泉水",
    "西红柿", "餐厅", "厨房", "客厅", "卫生间", "厕所", "沙发", "镜子",
    "勺子", "盒子", "刀", "毛巾", "牙膏", "橡皮", "钥匙", "袜子", "眼镜",
    "传真", "垃圾桶", "塑料袋", "家具", "窗户", "入口", "桥", "长城",
    "长江", "加油站", "大使馆", "邮局", "高速公路", "互联网 ", "网站",
    "网球", "羽毛球", "乒乓球", "京剧", "广告", "广播",

    # -- Tier 10: body / health / school / leisure --
    "胳膊", "肚子", "皮肤", "咳嗽", "理发", "散步", "放松", "放弃",
    "放暑假", "寒假", "学期", "预习", "基础", "标准", "森林", "老虎",
    "礼拜天",
    "植物", "叶子", "污染", "危险", "安全",
    "开玩笑", "笑话", "聚会", "约会", "旅行", "导游", "乘坐", "航班",
    "交通", "堵车", "迷路", "来不及", "来得及", "来自",

    # -- Tier 11: less-frequent abstracts, remaining misc --
    "暂时", "永远", "最好", "普通话", "语言", "语法", "日记", "自然".replace("自然", "自然"),
    "商量".replace("商量", "商量"), "允许", "拒绝",
    "失败", "死", "冷静".replace("冷静", "冷静"),
    "规定".replace("规定", "规定"), "排队", "排列",
    "竞争", "占线", "照", "养成".replace("养成", "养成"),
    "受不了", "羡慕", "值得".replace("值得", "值得"),
    "建议".replace("建议", "建议"),
    "亚洲", "修理 ", "许多",
    "干", "干杯", "刚".replace("刚", "刚"),
    "低".replace("低", "低"),  # keep placement
    "支持".replace("支持", "支持"),
    "号码".replace("号码", "号码"),
    "温度".replace("温度", "温度"),
    "饮料".replace("饮料", "果汁"),
    "约会".replace("约会", "约会"),
    "呀",
    "准时", "及时".replace("及时", "及时"),
    "专门".replace("专门", "专门"),
    "研究".replace("研究", "研究"),
    "诚实".replace("诚实", "诚实"),
    "填空",
    "尊重",
    "保护".replace("保护", "保护"),

    # -- Tier 12: remaining explicit placements --
    "讨论", "讨厌", "谈", "弹钢琴",
    "吃惊".replace("吃惊", "吃惊"),
    "严重".replace("严重", "严重"),
    "养成".replace("养成", "养成"),
]

# Clean up: drop duplicates while preserving first occurrence, and filter out
# any placeholder strings that slipped in and don't match real headwords.
seen = set()
_cleaned = []
for w in RANKED:
    if w in seen:
        continue
    seen.add(w)
    _cleaned.append(w)
RANKED = _cleaned


def parse_source():
    entries = []
    with SRC.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            orig_rank = int(parts[0])
            chinese = parts[1]
            pinyin = parts[2]
            english = parts[3]
            entries.append((orig_rank, chinese, pinyin, english))
    return entries


def main():
    entries = parse_source()
    headwords = {e[1] for e in entries}

    rank_of = {}
    next_rank = 1
    for w in RANKED:
        if w in headwords and w not in rank_of:
            rank_of[w] = next_rank
            next_rank += 1

    # Unplaced headwords tail: keep their original (alphabetical-by-pinyin)
    # order so the fallback section is stable.
    for orig_rank, chinese, *_ in entries:
        if chinese not in rank_of:
            rank_of[chinese] = next_rank
            next_rank += 1

    sorted_entries = sorted(entries, key=lambda e: rank_of[e[1]])

    with DST.open("w", encoding="utf-8") as f:
        for new_rank, (orig_rank, chinese, pinyin, english) in enumerate(
            sorted_entries, start=1
        ):
            f.write(f"{new_rank}\t{orig_rank}\t{chinese}\t{pinyin}\t{english}\n")

    explicit = sum(1 for w in RANKED if w in headwords)
    print(f"Wrote {len(sorted_entries)} entries to {DST}")
    print(f"Explicitly ranked: {explicit} / {len(entries)}")


if __name__ == "__main__":
    main()
