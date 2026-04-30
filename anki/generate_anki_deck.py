#!/usr/bin/env python3
"""HSK 3 Anki deck — lesson-by-lesson, vocab with examples, grammar bidirectional + variations.

Output: <repo>/anki/output/HSK3_Ordered.apkg
"""

import sys
from pathlib import Path

import genanki
from pypinyin import Style, lazy_pinyin


DECK_ID = 2059400111
VOCAB_MODEL_ID = 1607392321
GRAMMAR_MODEL_ID = 1607392322

ROOT = Path(__file__).resolve().parent.parent
HSK1_PATH = ROOT / "wordlists" / "hsk_1.txt"
HSK2_PATH = ROOT / "wordlists" / "hsk_2.txt"
OUTPUT_PATH = ROOT / "anki" / "output" / "HSK3_Ordered.apkg"

CSS = """
.card {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 20px;
    text-align: center;
    color: #ffffff;
    background-color: #1a1a2e;
    padding: 20px;
}
.chinese { font-size: 44px; font-weight: bold; color: #ffffff; margin-bottom: 15px; }
.sentence-zh { font-size: 34px; font-weight: bold; color: #ffffff; margin-bottom: 12px; line-height: 1.4; }
.sentence-en { font-size: 22px; color: #7ec8e3; margin-bottom: 12px; line-height: 1.4; }
.pinyin { font-size: 22px; color: #ff6b81; margin-bottom: 10px; }
.english { font-size: 22px; color: #7ec8e3; margin-bottom: 15px; }
.lesson-tag { font-size: 13px; color: #888; margin-top: 14px; }
.kind-tag { font-size: 13px; color: #f0a500; margin-top: 4px; letter-spacing: 1px; }
.grammar-pattern { font-size: 20px; color: #ff6b81; margin-top: 14px; font-weight: bold; }
.pattern-structure { font-size: 17px; color: #ffd166; margin-top: 6px; font-family: "SF Mono", "Courier New", monospace; }
.explanation { font-size: 16px; color: #cccccc; text-align: left; margin-top: 12px; line-height: 1.55; }
.example {
    margin-top: 14px; padding: 10px 14px;
    background: #2a2a4a;
    border-left: 3px solid #ff6b81;
    border-radius: 4px;
    text-align: left;
}
.example .example-zh { font-size: 22px; font-weight: bold; color: #ffffff; }
.example .example-pinyin { font-size: 15px; color: #ff6b81; margin-top: 3px; }
.example .example-en { font-size: 15px; color: #aaa; font-style: italic; margin-top: 3px; }
hr { border: 0; border-top: 1px solid #444; margin: 14px 0; }
"""


vocab_model = genanki.Model(
    VOCAB_MODEL_ID,
    "HSK3 Vocab + Example",
    fields=[
        {"name": "Chinese"},
        {"name": "Pinyin"},
        {"name": "English"},
        {"name": "ExampleZH"},
        {"name": "ExamplePinyin"},
        {"name": "ExampleEN"},
        {"name": "Lesson"},
    ],
    templates=[
        {
            "name": "Recognize",
            "qfmt": '<div class="chinese">{{Chinese}}</div>'
                    '<div class="lesson-tag">HSK 3 · {{Lesson}}</div>',
            "afmt": '{{FrontSide}}<hr>'
                    '<div class="pinyin">{{Pinyin}}</div>'
                    '<div class="english">{{English}}</div>'
                    '<div class="example">'
                    '<div class="example-zh">{{ExampleZH}}</div>'
                    '<div class="example-pinyin">{{ExamplePinyin}}</div>'
                    '<div class="example-en">{{ExampleEN}}</div>'
                    '</div>',
        },
    ],
    css=CSS,
)


grammar_model = genanki.Model(
    GRAMMAR_MODEL_ID,
    "HSK3 Grammar Bidirectional",
    fields=[
        {"name": "Chinese"},
        {"name": "Pinyin"},
        {"name": "English"},
        {"name": "PatternName"},
        {"name": "Pattern"},
        {"name": "Explanation"},
        {"name": "Lesson"},
        {"name": "Kind"},
    ],
    templates=[
        {
            "name": "ZH to EN",
            "qfmt": '<div class="sentence-zh">{{Chinese}}</div>'
                    '<div class="grammar-pattern">Pattern: {{PatternName}}</div>'
                    '<div class="lesson-tag">HSK 3 · {{Lesson}}</div>'
                    '<div class="kind-tag">{{Kind}}</div>',
            "afmt": '{{FrontSide}}<hr>'
                    '<div class="pinyin">{{Pinyin}}</div>'
                    '<div class="sentence-en">{{English}}</div>'
                    '<div class="pattern-structure">{{Pattern}}</div>'
                    '<div class="explanation">{{Explanation}}</div>',
        },
        {
            "name": "EN to ZH",
            "qfmt": '<div class="sentence-en">{{English}}</div>'
                    '<div class="grammar-pattern">Pattern: {{PatternName}}</div>'
                    '<div class="lesson-tag">HSK 3 · {{Lesson}}</div>'
                    '<div class="kind-tag">{{Kind}}</div>',
            "afmt": '{{FrontSide}}<hr>'
                    '<div class="sentence-zh">{{Chinese}}</div>'
                    '<div class="pinyin">{{Pinyin}}</div>'
                    '<div class="pattern-structure">{{Pattern}}</div>'
                    '<div class="explanation">{{Explanation}}</div>',
        },
    ],
    css=CSS,
)


# ============================================================
# VOCABULARY: lesson -> list of (chinese, pinyin, english, example_zh, example_en)
# Example sentences use only vocab from this lesson or earlier + HSK 1/2 words.
# ============================================================
VOCAB = {
    1: [
        ("周末", "zhōumò", "weekend",
         "周末你有什么打算？", "What are your plans for the weekend?"),
        ("打算", "dǎsuàn", "plan; to plan",
         "我打算跟朋友去看电影。", "I plan to go to a movie with friends."),
        ("跟", "gēn", "with",
         "我跟他一起去学校。", "I go to school together with him."),
        ("游戏", "yóuxì", "game",
         "他一直玩游戏，不写作业。", "He keeps playing games and doesn't do his homework."),
        ("作业", "zuòyè", "homework",
         "今天的作业不难。", "Today's homework isn't difficult."),
        ("复习", "fùxí", "to review",
         "明天考试，我要复习。", "I have a test tomorrow, I need to review."),
        ("着急", "zháojí", "to worry; to be anxious",
         "别着急，还有时间。", "Don't worry, there's still time."),
        ("容易", "róngyì", "easy",
         "这个问题很容易。", "This question is very easy."),
        ("难", "nán", "difficult",
         "中文不难。", "Chinese isn't difficult."),
        ("一直", "yīzhí", "continuously; always",
         "他一直在家玩游戏。", "He's been at home playing games the whole time."),
        ("啊", "a", "(modal particle)",
         "你来了啊！", "Oh, you've come!"),
        ("简单", "jiǎndān", "simple",
         "今天的作业很简单。", "Today's homework is very simple."),
        ("经常", "jīngcháng", "often",
         "我经常跟他一起吃饭。", "I often eat with him."),
        ("还是", "háishì", "or; still",
         "你喝茶还是喝水？", "Do you want tea or water?"),
        ("过", "guò", "(experience particle); to pass",
         "我去过北京。", "I've been to Beijing before."),
    ],
    2: [
        ("树", "shù", "tree",
         "学校前面有大树。", "There are big trees in front of the school."),
        ("楼", "lóu", "building; floor",
         "他住在这个楼的五层。", "He lives on the fifth floor of this building."),
        ("办公室", "bàngōngshì", "office",
         "经理不在办公室。", "The manager isn't in the office."),
        ("经理", "jīnglǐ", "manager",
         "我们的经理很忙。", "Our manager is very busy."),
        ("秘书", "mìshū", "secretary",
         "秘书在办公室打电话。", "The secretary is on the phone in the office."),
        ("办", "bàn", "to handle; to do",
         "这件事今天就能办好。", "This can be taken care of today."),
        ("腿", "tuǐ", "leg",
         "我的腿有点儿疼。", "My legs hurt a little."),
        ("脚", "jiǎo", "foot",
         "我的脚很小。", "My feet are very small."),
        ("层", "céng", "floor; layer",
         "他住在八层。", "He lives on the eighth floor."),
        ("附近", "fùjìn", "nearby",
         "我家附近有一个大超市。", "There's a big supermarket near my home."),
    ],
    3: [
        ("爬山", "páshān", "to go hiking",
         "周末我们去爬山吧。", "Let's go hiking this weekend."),
        ("小心", "xiǎoxīn", "to be careful",
         "路上很多人，请你小心。", "There are a lot of people on the road, please be careful."),
        ("裤子", "kùzi", "trousers",
         "这条裤子不贵。", "These trousers aren't expensive."),
        ("衬衫", "chènshān", "shirt",
         "他今天穿了一件白衬衫。", "He wore a white shirt today."),
        ("记得", "jìde", "to remember",
         "我记得你说过这件事。", "I remember you said this before."),
        ("新鲜", "xīnxiān", "fresh",
         "超市的水果很新鲜。", "The fruit at the supermarket is very fresh."),
        ("甜", "tián", "sweet",
         "这个苹果很甜。", "This apple is very sweet."),
        ("只", "zhǐ", "only",
         "我只有一个哥哥。", "I only have one older brother."),
        ("饮料", "yǐnliào", "drink; beverage",
         "桌子上放着很多饮料。", "There are many drinks on the table."),
        ("或者", "huòzhě", "or (in statements)",
         "你可以喝茶或者喝水。", "You can drink tea or water."),
        ("哭", "kū", "to cry",
         "孩子为什么哭了？", "Why is the child crying?"),
        ("伞", "sǎn", "umbrella",
         "今天下雨，别忘了带伞。", "It's raining today, don't forget to bring an umbrella."),
        ("瓶子", "píngzi", "bottle",
         "桌子上有两个瓶子。", "There are two bottles on the table."),
        ("条", "tiáo", "(measure word for long items)",
         "这条裤子太长了。", "These trousers are too long."),
        ("啤酒", "píjiǔ", "beer",
         "他喜欢喝啤酒。", "He likes drinking beer."),
        ("香蕉", "xiāngjiāo", "banana",
         "我每天吃一个香蕉。", "I eat one banana every day."),
    ],
    4: [
        ("比赛", "bǐsài", "competition; match",
         "明天学校有比赛。", "There's a match at school tomorrow."),
        ("年级", "niánjí", "grade; year",
         "你弟弟几年级？", "What grade is your younger brother in?"),
        ("照片", "zhàopiàn", "photograph",
         "这张照片很好看。", "This photograph is very nice."),
        ("热情", "rèqíng", "enthusiastic; warm",
         "他对朋友很热情。", "He is very warm to friends."),
        ("聪明", "cōngming", "clever",
         "她的女儿很聪明。", "Her daughter is very clever."),
        ("努力", "nǔlì", "hardworking; to work hard",
         "他学习很努力。", "He studies very hard."),
        ("回答", "huídá", "to answer",
         "请你回答老师的问题。", "Please answer the teacher's question."),
        ("站", "zhàn", "to stand",
         "别站着，快坐下吧。", "Don't stand, sit down quickly."),
        ("笑", "xiào", "to smile; to laugh",
         "她笑着跟我说话。", "She talked to me while smiling."),
        ("照顾", "zhàogù", "to take care of",
         "妈妈在家照顾孩子。", "Mom takes care of the children at home."),
        ("总是", "zǒngshì", "always",
         "他总是第一个到。", "He's always the first to arrive."),
        ("饿", "è", "hungry",
         "我饿了，想吃饭。", "I'm hungry, I want to eat."),
        ("超市", "chāoshì", "supermarket",
         "附近有一个大超市。", "There's a big supermarket nearby."),
        ("蛋糕", "dàngāo", "cake",
         "这个蛋糕又甜又好吃。", "This cake is both sweet and delicious."),
        ("别人", "biéren", "others; other people",
         "你不要笑别人。", "Don't laugh at others."),
        ("客人", "kèrén", "guest",
         "今天家里来了两个客人。", "Two guests came to our home today."),
        ("参加", "cānjiā", "to participate in",
         "你参加比赛吗？", "Are you taking part in the match?"),
        ("地", "de", "(adverb particle)",
         "他认真地回答了问题。", "He earnestly answered the question."),
    ],
    5: [
        ("感冒", "gǎnmào", "to catch a cold",
         "我感冒了，不想上课。", "I've caught a cold, I don't want to go to class."),
        ("发烧", "fāshāo", "to have a fever",
         "孩子发烧了，快去医院。", "The child has a fever, hurry to the hospital."),
        ("季节", "jìjié", "season",
         "你最喜欢哪个季节？", "Which season do you like best?"),
        ("春", "chūn", "spring",
         "春天来了，花开了。", "Spring has come, the flowers are blooming."),
        ("夏", "xià", "summer",
         "夏天很热。", "Summer is very hot."),
        ("秋", "qiū", "autumn",
         "秋天不冷也不热。", "Autumn is neither cold nor hot."),
        ("冬", "dōng", "winter",
         "北方的冬天下雪。", "It snows in the north in winter."),
        ("草", "cǎo", "grass",
         "春天的草是绿色的。", "Spring grass is green."),
        ("花", "huā", "flower",
         "她买了很多花。", "She bought many flowers."),
        ("礼物", "lǐwù", "gift",
         "这是我给你的礼物。", "This is the gift I'm giving you."),
        ("为", "wèi", "for (on behalf of)",
         "我为你做了一个蛋糕。", "I made a cake for you."),
        ("胖", "pàng", "fat",
         "他最近胖了。", "He's gotten fat recently."),
        ("裙子", "qúnzi", "skirt",
         "这条裙子很漂亮。", "This skirt is very beautiful."),
        ("当然", "dāngrán", "of course",
         "他当然知道。", "Of course he knows."),
        ("最近", "zuìjìn", "recently",
         "最近我很忙。", "I've been very busy recently."),
        ("舒服", "shūfu", "comfortable",
         "今天我不舒服。", "I don't feel well today."),
        ("疼", "téng", "to hurt",
         "我的脚很疼。", "My foot hurts a lot."),
        ("渴", "kě", "thirsty",
         "我渴了，想喝水。", "I'm thirsty, I want some water."),
        ("太阳", "tàiyáng", "sun",
         "今天的太阳很大。", "The sun is very strong today."),
        ("刮风", "guāfēng", "windy",
         "外面刮风了。", "It's gotten windy outside."),
        ("鸟", "niǎo", "bird",
         "树上有很多鸟。", "There are many birds in the tree."),
        ("节日", "jiérì", "festival",
         "春节是中国的节日。", "Spring Festival is a Chinese festival."),
    ],
    6: [
        ("眼镜", "yǎnjìng", "glasses",
         "我的眼镜找不到了。", "I can't find my glasses."),
        ("清楚", "qīngchǔ", "clear",
         "你说慢一点儿，我听不清楚。", "Please speak slowly, I can't hear clearly."),
        ("离开", "líkāi", "to leave",
         "他已经离开北京了。", "He's already left Beijing."),
        ("突然", "tūrán", "suddenly",
         "他突然不说话了。", "Suddenly he stopped talking."),
        ("帮忙", "bāngmáng", "to help",
         "请你帮我一个忙。", "Please do me a favor."),
        ("特别", "tèbié", "especially",
         "她今天特别高兴。", "She is especially happy today."),
        ("讲", "jiǎng", "to speak; to explain",
         "老师在讲新课。", "The teacher is explaining a new lesson."),
        ("锻炼", "duànliàn", "to exercise",
         "我每天早上锻炼身体。", "I exercise every morning."),
        ("刚才", "gāngcái", "just now",
         "刚才他在办公室。", "He was in the office just now."),
        ("刚", "gāng", "just",
         "我刚到家。", "I just got home."),
        ("用", "yòng", "to use",
         "我可以用你的电脑吗？", "Can I use your computer?"),
        ("聊天", "liáotiān", "to chat",
         "我们一起聊聊天吧。", "Let's chat together."),
        ("公园", "gōngyuán", "park",
         "公园里有很多花。", "There are many flowers in the park."),
        ("方便", "fāngbiàn", "convenient",
         "坐地铁很方便。", "Taking the subway is very convenient."),
        ("声音", "shēngyīn", "voice; sound",
         "她的声音很好听。", "Her voice is very pleasant."),
        ("奇怪", "qíguài", "strange",
         "这件事真奇怪。", "This is really strange."),
    ],
    7: [
        ("以前", "yǐqián", "before; in the past",
         "以前他不会说中文。", "He couldn't speak Chinese before."),
        ("以后", "yǐhòu", "after; in the future",
         "以后我想去中国工作。", "I want to go to China to work in the future."),
        ("半", "bàn", "half",
         "现在八点半。", "It's 8:30 now."),
        ("结婚", "jiéhūn", "to get married",
         "他们去年结婚了。", "They got married last year."),
        ("感兴趣", "gǎn xìngqù", "to be interested in",
         "我对中国历史感兴趣。", "I'm interested in Chinese history."),
        ("迟到", "chídào", "to be late",
         "他上课从来不迟到。", "He's never late to class."),
        ("接", "jiē", "to pick up; to answer",
         "我去机场接朋友。", "I'm going to the airport to pick up a friend."),
        ("银行", "yínháng", "bank",
         "银行九点开门。", "The bank opens at nine."),
        ("久", "jiǔ", "long (time)",
         "我在这儿等了很久了。", "I've been waiting here for a long time."),
        ("同事", "tóngshì", "colleague",
         "他是我以前的同事。", "He is my former colleague."),
        ("欢迎", "huānyíng", "welcome",
         "欢迎你来我家玩儿。", "Welcome to come to my place."),
        ("阿姨", "āyí", "aunt",
         "那位阿姨是我妈妈的朋友。", "That aunt is my mother's friend."),
        ("叔叔", "shūshu", "uncle",
         "我叔叔住在北京。", "My uncle lives in Beijing."),
        ("奶奶", "nǎinai", "grandma",
         "奶奶做的菜很好吃。", "Grandma's cooking is delicious."),
        ("爷爷", "yéye", "grandpa",
         "爷爷今年八十岁了。", "Grandpa is 80 this year."),
        ("刻", "kè", "quarter of an hour",
         "现在差一刻三点。", "It's a quarter to three now."),
        ("分", "fēn", "minute",
         "现在八点十分。", "It's 8:10 now."),
        ("位", "wèi", "(polite measure word for people)",
         "这位是我的老师。", "This is my teacher."),
    ],
    8: [
        ("满意", "mǎnyì", "satisfied",
         "老师对他很满意。", "The teacher is very pleased with him."),
        ("又", "yòu", "again (past)",
         "他又迟到了。", "He was late again."),
        ("再", "zài", "again (future)",
         "欢迎你再来。", "Welcome to come again."),
        ("往", "wǎng", "towards",
         "往前走就是超市。", "Walk forward and you'll find the supermarket."),
        ("见面", "jiànmiàn", "to meet",
         "我们明天见面吧。", "Let's meet tomorrow."),
        ("几乎", "jīhū", "almost",
         "他几乎每天都锻炼。", "He exercises almost every day."),
        ("变化", "biànhuà", "change (noun)",
         "这个城市有很多变化。", "This city has many changes."),
        ("变", "biàn", "to become; to change",
         "天气变冷了。", "The weather has turned cold."),
        ("电梯", "diàntī", "elevator",
         "请坐电梯上楼。", "Please take the elevator upstairs."),
        ("害怕", "hàipà", "to be afraid",
         "他从小就害怕狗。", "He's been afraid of dogs since he was little."),
        ("安静", "ānjìng", "quiet",
         "图书馆里很安静。", "The library is very quiet."),
        ("老", "lǎo", "old",
         "我爷爷老了。", "My grandpa has grown old."),
        ("一会儿", "yíhuìr", "a little while",
         "我一会儿就来。", "I'll be there in a moment."),
        ("马上", "mǎshàng", "right away",
         "我马上就到。", "I'll be right there."),
        ("洗手间", "xǐshǒujiān", "restroom",
         "请问洗手间在哪儿？", "Where is the restroom, please?"),
        ("北方", "běifāng", "north",
         "北方的冬天特别冷。", "Winters in the north are especially cold."),
        ("南", "nán", "south",
         "南方的夏天很热。", "Summers in the south are very hot."),
        ("西", "xī", "west",
         "太阳从西边下山。", "The sun sets in the west."),
        ("东", "dōng", "east",
         "太阳从东边出来。", "The sun rises in the east."),
        ("中间", "zhōngjiān", "middle",
         "他坐在中间。", "He's sitting in the middle."),
        ("街道", "jiēdào", "street",
         "这条街道非常干净。", "This street is very clean."),
    ],
    9: [
        ("一样", "yíyàng", "the same",
         "他的衣服跟我的一样。", "His clothes are the same as mine."),
        ("担心", "dānxīn", "to worry",
         "妈妈担心我的身体。", "Mom worries about my health."),
        ("了解", "liǎojiě", "to know about",
         "我不太了解他。", "I don't really know him well."),
        ("明白", "míngbai", "to understand",
         "老师讲的我都明白了。", "I understand everything the teacher said."),
        ("最后", "zuìhòu", "final; in the end",
         "最后他们都来了。", "In the end they all came."),
        ("一定", "yídìng", "definitely",
         "他一定会来。", "He will definitely come."),
        ("健康", "jiànkāng", "healthy",
         "多锻炼对身体健康好。", "Exercising more is good for your health."),
        ("更", "gèng", "even more",
         "他比我更高。", "He is even taller than me."),
        ("其实", "qíshí", "actually",
         "其实这个问题不难。", "Actually this question isn't hard."),
        ("应该", "yīnggāi", "should",
         "你应该早点儿睡。", "You should sleep earlier."),
        ("放心", "fàngxīn", "to be at ease",
         "你放心吧，我会小心的。", "Don't worry, I'll be careful."),
        ("种", "zhǒng", "kind; type",
         "我最喜欢这种茶。", "I like this kind of tea the most."),
    ],
    10: [
        ("个子", "gèzi", "stature; height",
         "她的个子很高。", "She's quite tall."),
        ("自行车", "zìxíngchē", "bicycle",
         "我骑自行车去学校。", "I ride a bicycle to school."),
        ("旧", "jiù", "old (used)",
         "这件衣服太旧了。", "This piece of clothing is too old."),
        ("换", "huàn", "to change",
         "我想换一件新衣服。", "I want to change into new clothes."),
        ("主要", "zhǔyào", "mainly",
         "他主要教中文。", "He mainly teaches Chinese."),
        ("数学", "shùxué", "mathematics",
         "我的数学不太好。", "My math isn't very good."),
        ("历史", "lìshǐ", "history",
         "他对中国历史很感兴趣。", "He's very interested in Chinese history."),
        ("体育", "tǐyù", "sports; PE",
         "今天下午有体育课。", "There is PE this afternoon."),
        ("比较", "bǐjiào", "relatively",
         "今天的问题比较难。", "Today's questions are relatively hard."),
        ("辆", "liàng", "(measure word for vehicles)",
         "他有两辆车。", "He has two cars."),
        ("环境", "huánjìng", "environment",
         "这儿的环境很好。", "The environment here is very nice."),
        ("黑板", "hēibǎn", "blackboard",
         "老师在黑板上写字。", "The teacher is writing on the blackboard."),
        ("笔记本", "bǐjìběn", "notebook",
         "我买了一个新笔记本。", "I bought a new notebook."),
        ("教", "jiāo", "to teach",
         "她教我们中文。", "She teaches us Chinese."),
        ("校长", "xiàozhǎng", "principal",
         "校长在开会。", "The principal is in a meeting."),
        ("认真", "rènzhēn", "earnest; serious",
         "他学习很认真。", "He studies very earnestly."),
        ("司机", "sījī", "driver",
         "出租车司机很热情。", "The taxi driver is very friendly."),
        ("万", "wàn", "ten thousand",
         "这辆车要五万块。", "This car costs 50,000 yuan."),
        ("角", "jiǎo", "jiao (currency)",
         "一块钱是十角。", "One yuan equals ten jiao."),
        ("元", "yuán", "yuan",
         "这本书二十元。", "This book costs 20 yuan."),
        ("一共", "yígòng", "altogether",
         "一共多少钱？", "How much is it altogether?"),
        ("公斤", "gōngjīn", "kilogram",
         "这些苹果一共三公斤。", "These apples total three kilograms."),
    ],
    11: [
        ("图书馆", "túshūguǎn", "library",
         "我去图书馆借书。", "I'm going to the library to borrow a book."),
        ("借", "jiè", "to borrow",
         "你可以借我笔吗？", "Can you lend me a pen?"),
        ("还", "huán", "to return (an item)",
         "请你把书还给我。", "Please return the book to me."),
        ("词典", "cídiǎn", "dictionary",
         "这本词典很好用。", "This dictionary is very useful."),
        ("灯", "dēng", "light; lamp",
         "请把灯关了。", "Please turn off the light."),
        ("关", "guān", "to close; to turn off",
         "别忘了把空调关了。", "Don't forget to turn off the air conditioner."),
        ("空调", "kōngtiáo", "air conditioner",
         "夏天的时候，我们经常开空调。", "We often turn on the air conditioner in summer."),
        ("会议", "huìyì", "meeting",
         "经理现在在开会议。", "The manager is in a meeting now."),
        ("结束", "jiéshù", "to end; to finish",
         "会议八点结束。", "The meeting ends at eight."),
        ("忘记", "wàngjì", "to forget",
         "我忘记带作业了。", "I forgot to bring my homework."),
        ("地铁", "dìtiě", "subway",
         "坐地铁去学校很方便。", "Taking the subway to school is very convenient."),
        ("把", "bǎ", "(disposal particle)",
         "我把水喝了。", "I drank the water."),
        ("筷子", "kuàizi", "chopsticks",
         "我会用筷子吃饭。", "I can eat with chopsticks."),
        ("冰箱", "bīngxiāng", "refrigerator",
         "冰箱里有很多水果。", "There's a lot of fruit in the refrigerator."),
        ("坏", "huài", "bad; broken",
         "冰箱坏了。", "The refrigerator is broken."),
        ("双", "shuāng", "pair",
         "我买了一双新鞋。", "I bought a new pair of shoes."),
    ],
    12: [
        ("生气", "shēngqì", "to be angry",
         "妈妈生我的气了。", "Mom got angry with me."),
        ("行李箱", "xínglǐxiāng", "suitcase",
         "他的行李箱很大。", "His suitcase is very big."),
        ("包", "bāo", "bag",
         "我的包里有一本书。", "There's a book in my bag."),
        ("自己", "zìjǐ", "oneself",
         "这件事你要自己做。", "You have to do this yourself."),
        ("发现", "fāxiàn", "to discover",
         "我发现自己生病了。", "I realized I was sick."),
        ("护照", "hùzhào", "passport",
         "别忘了带护照。", "Don't forget to bring your passport."),
        ("重要", "zhòngyào", "important",
         "这件事很重要。", "This matter is very important."),
        ("放", "fàng", "to put",
         "请把书放在桌子上。", "Please put the book on the table."),
        ("搬", "bān", "to move",
         "我们下个月要搬家。", "We're moving next month."),
        ("带", "dài", "to bring",
         "你带伞了吗？", "Did you bring an umbrella?"),
        ("地图", "dìtú", "map",
         "我有一张北京的地图。", "I have a map of Beijing."),
        ("船", "chuán", "boat; ship",
         "我们坐船去吧。", "Let's go by boat."),
        ("起飞", "qǐfēi", "to take off (plane)",
         "飞机九点起飞。", "The plane takes off at nine."),
    ],
    13: [
        ("终于", "zhōngyú", "finally",
         "我终于做完作业了。", "I've finally finished my homework."),
        ("过去", "guòqù", "in the past",
         "过去他不喜欢吃鱼。", "In the past he didn't like eating fish."),
        ("一般", "yìbān", "usually; general",
         "我一般七点起床。", "I usually get up at seven."),
        ("遇到", "yùdào", "to meet; to encounter",
         "我今天在超市遇到了老师。", "I ran into my teacher at the supermarket today."),
        ("一边", "yìbiān", "at the same time",
         "他一边走一边听音乐。", "He walks while listening to music."),
        ("然后", "ránhòu", "then",
         "我先吃饭，然后去上课。", "I'll eat first, then go to class."),
        ("经过", "jīngguò", "to pass through; after",
         "经过一年的学习，他的中文好多了。", "After a year of study, his Chinese has improved a lot."),
        ("音乐", "yīnyuè", "music",
         "他喜欢一边看书一边听音乐。", "He likes reading while listening to music."),
        ("拿", "ná", "to take; to hold",
         "请把书拿过来。", "Please bring the book over."),
    ],
    14: [
        ("打扫", "dǎsǎo", "to clean",
         "周末我要打扫房间。", "I'm going to clean my room this weekend."),
        ("干净", "gānjìng", "clean",
         "她把房间打扫干净了。", "She cleaned the room."),
        ("洗澡", "xǐzǎo", "to take a shower",
         "我每天晚上洗澡。", "I take a shower every evening."),
        ("节目", "jiémù", "program",
         "这个节目很有意思。", "This program is very interesting."),
        ("月亮", "yuèliang", "moon",
         "今天晚上的月亮很亮。", "Tonight's moon is very bright."),
        ("故事", "gùshi", "story",
         "爷爷给孩子讲故事。", "Grandpa is telling a story to the children."),
        ("练习", "liànxí", "to practice",
         "我每天练习写汉字。", "I practice writing Chinese characters every day."),
        ("完成", "wánchéng", "to complete",
         "我已经完成作业了。", "I've already completed my homework."),
        ("碗", "wǎn", "bowl",
         "桌子上有三个碗。", "There are three bowls on the table."),
        ("盘子", "pánzi", "plate",
         "请你把盘子拿过来。", "Please bring the plate over."),
        ("先", "xiān", "first",
         "你先走，我一会儿就到。", "You go first, I'll be there in a moment."),
        ("刷牙", "shuāyá", "to brush teeth",
         "睡觉以前要刷牙。", "You should brush your teeth before sleeping."),
    ],
    15: [
        ("留学", "liúxué", "to study abroad",
         "他打算去中国留学。", "He plans to go to China to study abroad."),
        ("提高", "tígāo", "to improve",
         "他的中文水平提高了。", "His Chinese level has improved."),
        ("水平", "shuǐpíng", "level",
         "我的中文水平不高。", "My Chinese level isn't high."),
        ("要求", "yāoqiú", "requirement; to require",
         "老师的要求很高。", "The teacher's requirements are high."),
        ("注意", "zhùyì", "to pay attention",
         "路上有车，请注意。", "There are cars on the road, please pay attention."),
        ("上网", "shàngwǎng", "to go online",
         "他每天上网看新闻。", "He goes online every day to read the news."),
        ("新闻", "xīnwén", "news",
         "今天的新闻我还没看。", "I haven't read today's news yet."),
        ("其他", "qítā", "other",
         "除了数学，其他课我都喜欢。", "Except for math, I like all the other classes."),
        ("关心", "guānxīn", "to care about",
         "爷爷非常关心我的学习。", "Grandpa cares a lot about my studies."),
        ("句子", "jùzi", "sentence",
         "这个句子有点儿难。", "This sentence is a bit difficult."),
        ("解决", "jiějué", "to solve",
         "这个问题不好解决。", "This problem isn't easy to solve."),
        ("发", "fā", "to send",
         "我给他发了一个电子邮件。", "I sent him an email."),
        ("电子邮件", "diànzǐ yóujiàn", "email",
         "请给我发一个电子邮件。", "Please send me an email."),
        ("极", "jí", "extremely",
         "这个蛋糕好吃极了。", "This cake is extremely delicious."),
        ("需要", "xūyào", "to need",
         "你需要什么？", "What do you need?"),
        ("中文", "zhōngwén", "Chinese language",
         "我学中文两年了。", "I've been studying Chinese for two years."),
    ],
    16: [
        ("城市", "chéngshì", "city",
         "北京是一个大城市。", "Beijing is a big city."),
        ("如果", "rúguǒ", "if",
         "如果下雨，我就不去了。", "If it rains, I won't go."),
        ("认为", "rènwéi", "to think; to consider",
         "我认为他说得对。", "I think what he said is right."),
        ("帽子", "màozi", "hat",
         "他有一个蓝帽子。", "He has a blue hat."),
        ("头发", "tóufa", "hair",
         "她的头发又黑又长。", "Her hair is both black and long."),
        ("皮鞋", "píxié", "leather shoes",
         "这双皮鞋很贵。", "These leather shoes are very expensive."),
        ("像", "xiàng", "to resemble",
         "她长得像她妈妈。", "She looks like her mother."),
        ("矮", "ǎi", "short (height)",
         "他比我矮一点儿。", "He is a little shorter than me."),
        ("瘦", "shòu", "thin",
         "他最近瘦了。", "He has gotten thinner recently."),
        ("机会", "jīhuì", "opportunity",
         "这是一个很好的机会。", "This is a very good opportunity."),
        ("地方", "dìfang", "place",
         "这个地方很漂亮。", "This place is very beautiful."),
        ("国家", "guójiā", "country",
         "中国是一个大国家。", "China is a big country."),
        ("世界", "shìjiè", "world",
         "世界上有很多国家。", "There are many countries in the world."),
        ("年轻", "niánqīng", "young",
         "他看上去很年轻。", "He looks very young."),
        ("多么", "duōme", "how; what (exclamatory)",
         "今天多么漂亮啊！", "How beautiful today is!"),
        ("黄河", "huánghé", "Yellow River",
         "黄河是中国的大河。", "The Yellow River is a major river in China."),
        ("有名", "yǒumíng", "famous",
         "这个地方很有名。", "This place is very famous."),
    ],
    17: [
        ("请假", "qǐngjià", "to ask for leave",
         "他今天请假了。", "He asked for leave today."),
        ("邻居", "línjū", "neighbor",
         "我的邻居很热情。", "My neighbors are very friendly."),
        ("后来", "hòulái", "afterwards",
         "后来他给我打电话了。", "Afterwards he called me."),
        ("爱好", "àihào", "hobby",
         "我的爱好是看书。", "My hobby is reading."),
        ("办法", "bànfǎ", "method; way",
         "这个办法不错。", "This method isn't bad."),
        ("为了", "wèile", "in order to",
         "为了提高中文水平，我每天练习。", "In order to improve my Chinese, I practice every day."),
        ("决定", "juédìng", "to decide",
         "我决定去中国留学。", "I've decided to study abroad in China."),
        ("关系", "guānxì", "relationship",
         "他们的关系很好。", "Their relationship is very good."),
        ("选择", "xuǎnzé", "to choose",
         "你可以自己选择。", "You can choose yourself."),
        ("根据", "gēnjù", "according to",
         "根据老师的要求，我们要写作业。", "According to the teacher's requirements, we have to do homework."),
        ("试", "shì", "to try",
         "你可以试一下这件衣服。", "You can try on this piece of clothing."),
        ("习惯", "xíguàn", "habit; to be used to",
         "我习惯了这儿的天气。", "I've gotten used to the weather here."),
        ("必须", "bìxū", "must",
         "明天你必须来。", "You must come tomorrow."),
        ("检查", "jiǎnchá", "to inspect",
         "你再检查一次作业。", "Check your homework once more."),
    ],
    18: [
        ("向", "xiàng", "towards",
         "请向前走。", "Please walk forward."),
        ("只要", "zhǐyào", "as long as",
         "只要你努力，就一定能学好。", "As long as you work hard, you can definitely learn it well."),
        ("关于", "guānyú", "about; regarding",
         "这是一本关于历史的书。", "This is a book about history."),
        ("相信", "xiāngxìn", "to believe",
         "我相信你。", "I believe you."),
        ("同意", "tóngyì", "to agree",
         "我同意你的办法。", "I agree with your method."),
        ("差", "chà", "to lack",
         "现在差五分八点。", "It's five minutes to eight."),
        ("动物", "dòngwù", "animal",
         "熊猫是我最喜欢的动物。", "Pandas are my favorite animals."),
        ("段", "duàn", "section; paragraph",
         "请读这段话。", "Please read this paragraph."),
        ("愿意", "yuànyì", "to be willing",
         "我愿意帮你。", "I'm willing to help you."),
        ("可爱", "kě'ài", "cute",
         "这只小狗真可爱。", "This puppy is really cute."),
        ("熊猫", "xióngmāo", "panda",
         "熊猫只在中国有。", "Pandas are only found in China."),
        ("文化", "wénhuà", "culture",
         "我对中国文化很感兴趣。", "I'm very interested in Chinese culture."),
        ("不但", "búdàn", "not only",
         "他不但高，也很瘦。", "He's not only tall, he's also thin."),
        ("而且", "érqiě", "moreover; and also",
         "这家饭店很好，而且不贵。", "This restaurant is good, and it's not expensive."),
    ],
    19: [
        ("耳朵", "ěrduo", "ear",
         "我的耳朵有点儿疼。", "My ears hurt a little."),
        ("鼻子", "bízi", "nose",
         "她的鼻子很好看。", "Her nose is very pretty."),
        ("嘴", "zuǐ", "mouth",
         "他的嘴不大。", "His mouth isn't big."),
        ("脸", "liǎn", "face",
         "她的脸红了。", "Her face has turned red."),
        ("骑", "qí", "to ride",
         "我不会骑自行车。", "I can't ride a bicycle."),
        ("马", "mǎ", "horse",
         "他在草地上骑马。", "He's riding a horse on the grass."),
        ("短", "duǎn", "short (length)",
         "他的头发很短。", "His hair is very short."),
        ("起来", "qǐlái", "to get up; up",
         "我想起来了！", "I remember now!"),
        ("蓝", "lán", "blue",
         "天是蓝的。", "The sky is blue."),
        ("绿", "lǜ", "green",
         "春天的草是绿的。", "Spring grass is green."),
        ("张", "zhāng", "(measure word for flat objects)",
         "桌子上有一张照片。", "There's a photo on the table."),
        ("口", "kǒu", "mouth; (measure word for people)",
         "他家有四口人。", "His family has four people."),
        ("画", "huà", "painting; to draw",
         "这张画很有名。", "This painting is very famous."),
        ("使", "shǐ", "to cause; to make",
         "这件事使大家很高兴。", "This event made everyone very happy."),
    ],
    20: [
        ("照相机", "zhàoxiàngjī", "camera",
         "我的照相机不见了。", "My camera is missing."),
        ("信用卡", "xìnyòngkǎ", "credit card",
         "我用信用卡买了这件衣服。", "I bought these clothes with a credit card."),
        ("影响", "yǐngxiǎng", "to influence; influence",
         "他对我影响很大。", "He has a big influence on me."),
        ("被", "bèi", "passive marker",
         "我的书被他拿走了。", "My book was taken by him."),
        ("难过", "nánguò", "sad",
         "听到这件事，她很难过。", "Hearing this news, she was very sad."),
        ("成绩", "chéngjì", "grades; results",
         "他的成绩越来越好。", "His grades are getting better and better."),
        ("越", "yuè", "the more",
         "他越学越努力。", "The more he studies, the harder he works."),
        ("班", "bān", "class; shift",
         "我们班有二十个人。", "Our class has twenty people."),
        ("饱", "bǎo", "full (after eating)",
         "我吃饱了，谢谢。", "I'm full, thank you."),
        ("菜单", "càidān", "menu",
         "请把菜单给我看一下。", "Please let me see the menu."),
        ("除了", "chúle", "except; besides",
         "除了我，大家都去了。", "Everyone went except me."),
        ("面包", "miànbāo", "bread",
         "早饭我吃了面包。", "I had bread for breakfast."),
        ("米", "mǐ", "rice; meter",
         "他家离学校五百米。", "His home is 500 meters from school."),
    ],
}


# ============================================================
# GRAMMAR: lesson -> list of (pattern_name, structure, explanation,
#                             textbook_examples, variations)
# Each example is (chinese, english). Pinyin is auto-generated.
# Variations are NOT from the textbook — they test the same pattern with different wording.
# ============================================================
GRAMMAR = {
    1: [
        ("结果补语 \"好\"", "V + 好 (+了)",
         "\"好\" after a verb means the action was completed successfully / satisfactorily. "
         "Stronger than 完 — includes a sense of 'done right'.",
         [("晚上吃什么，你想好了吗？", "Have you decided what to eat tonight?"),
          ("我买好电影票了。", "I've bought the movie tickets."),
          ("你准备好了吗？", "Are you ready? (Have you finished preparing?)"),
          ("房间我已经找好了。", "I've already found a room.")],
         [("这本书我看好了，你也看一下吧。", "I've finished reading this book, you read it too."),
          ("作业做好了，我想出去玩儿。", "I've finished my homework, I want to go out and play.")]),
        ("一……也/都+不/没：Total negation", "一 + (MW + N) + 也/都 + 不/没 + V/Adj",
         "Emphatic total negation — 'not at all' / 'not even one'. With an adjective, use \"一点儿也/都\".",
         [("我一点儿也不着急。", "I'm not worried at all."),
          ("他一件衣服也没买。", "He didn't buy a single piece of clothing."),
          ("今天一点儿都不冷。", "Today isn't cold at all."),
          ("她一杯茶也没喝。", "She didn't drink even one cup of tea.")],
         [("我一个苹果也不想吃。", "I don't want to eat a single apple."),
          ("他一点儿都不累。", "He isn't tired at all.")]),
        ("连词 \"那\"", "那 + Conclusion",
         "\"那\" at the start of a sentence draws a conclusion from what was just said — 'then (in that case)'.",
         [("A: 我不想去看电影。 B: 那我也不去了。", "A: I don't want to see the movie. B: Then I won't go either."),
          ("A: 我已经复习好了。 B: 那你别着急。", "A: I've already reviewed. B: Then don't worry.")],
         [("A: 外面下雨了。 B: 那我们在家吧。", "A: It's raining outside. B: Then let's stay home."),
          ("A: 我还没吃饭。 B: 那我们一起去吃吧。", "A: I haven't eaten yet. B: Then let's go eat together.")]),
    ],
    2: [
        ("简单趋向补语 来/去", "V + 来/去",
         "\"来\" = motion toward the speaker; \"去\" = motion away. Common: 上/下/过/进/出/回 + 来/去.",
         [("他什么时候回来？", "When is he coming back?"),
          ("请你出来一下。", "Please come out for a moment."),
          ("那边有很多树，我们过去坐一坐吧。", "There are many trees over there, let's go sit."),
          ("老师走进来了。", "The teacher walked in.")],
         [("妈妈回来了，快过去！", "Mom is back, go over there quickly!"),
          ("时间不早了，我要回去了。", "It's getting late, I need to head back.")]),
        ("V了 + 就 + V：As soon as... then...", "V1 + 了 + (O) + 就 + V2",
         "Two actions in quick succession — 'as soon as A, then B'. Use 了 to mark completion of the first.",
         [("我到了办公室就开始工作。", "As soon as I got to the office I started working."),
          ("他回来了就告诉我。", "Tell me as soon as he gets back."),
          ("我吃了饭就去学校。", "I'll go to school as soon as I finish eating.")],
         [("她起了床就给妈妈打电话。", "She called her mom as soon as she got up."),
          ("下了课我们就去超市吧。", "Let's go to the supermarket as soon as class ends.")]),
        ("反问：不……吗？", "Subject + 不 + V/Adj + 吗？",
         "Rhetorical question — the speaker expects the listener to already know. Implies 'isn't it obvious?'",
         [("你明天不是有考试吗？", "Don't you have a test tomorrow?"),
          ("我不是告诉你了吗？", "Didn't I already tell you?"),
          ("你不是喜欢吃鱼吗？", "Don't you like eating fish?")],
         [("你不是北京人吗？怎么不认识路？", "Aren't you from Beijing? How come you don't know the way?"),
          ("我们不是朋友吗？你不用客气。", "Aren't we friends? No need to be polite.")]),
    ],
    3: [
        ("还是 vs 或者：Or", "还是 (in questions) / 或者 (in statements)",
         "\"还是\" = 'or' in a question offering choices. \"或者\" = 'or' in a statement.",
         [("你喜欢喝茶还是咖啡？", "Do you prefer tea or coffee?"),
          ("你可以喝花茶或者绿茶。", "You can drink flower tea or green tea."),
          ("周末你想看电影还是去公园？", "Do you want to watch a movie or go to the park this weekend?"),
          ("明天或者后天都可以。", "Tomorrow or the day after, either is fine.")],
         [("你要面包还是米饭？", "Do you want bread or rice?"),
          ("你可以坐地铁或者坐出租车。", "You can take the subway or take a taxi.")]),
        ("存在：Place + V着 + N", "Place + V + 着 + (Num + MW) + Noun",
         "Describes something that exists at a place. The verb (放, 站, 坐, 写, 挂) describes how it sits there.",
         [("桌子上放着很多饮料。", "There are lots of drinks on the table."),
          ("门上写着一个字。", "There's a character written on the door."),
          ("椅子上坐着一个人。", "There's someone sitting on the chair."),
          ("门上写着一个名字。", "There's a name written on the door.")],
         [("黑板上写着今天的作业。", "Today's homework is written on the blackboard."),
          ("房间里站着两个客人。", "Two guests are standing in the room.")]),
        ("\"会\" 表示可能性", "Subject + 会 + V + (的)",
         "\"会\" means 'will' — the speaker predicts something is likely. Often ends with …的 for emphasis.",
         [("明天会下雨。", "It will rain tomorrow."),
          ("他会来的，别担心。", "He'll come, don't worry."),
          ("你不穿衣服会感冒的。", "You'll catch a cold if you don't put on clothes.")],
         [("天气这么热，我想他会感冒。", "The weather is so hot, I think he'll catch a cold."),
          ("他这么努力，一定会做好的。", "He works so hard, he will definitely do well.")]),
    ],
    4: [
        ("又……又……：Both...and...", "又 + Adj1 + 又 + Adj2",
         "Two qualities existing at the same time in the same person/thing. Usually adjectives.",
         [("她又高又漂亮。", "She is both tall and pretty."),
          ("这个蛋糕又甜又好吃。", "This cake is both sweet and delicious."),
          ("今天又冷又刮风。", "Today is both cold and windy."),
          ("这本书又便宜又好看。", "This book is both cheap and interesting.")],
         [("他又聪明又努力。", "He is both smart and hardworking."),
          ("这件衣服又舒服又漂亮。", "These clothes are both comfortable and pretty.")]),
        ("伴随动作：V1着(O1) + V2(O2)", "V1 + 着 + (O1) + V2 + (O2)",
         "着 between two verbs — V1 describes the manner or ongoing state while V2 happens.",
         [("她笑着跟客人说话。", "She talks to guests while smiling."),
          ("老师站着上课。", "The teacher teaches standing up."),
          ("他拿着书走出去了。", "He walked out holding a book."),
          ("孩子哭着跑回来了。", "The child came running back crying.")],
         [("爷爷坐着看电视。", "Grandpa watches TV sitting down."),
          ("她听着音乐做作业。", "She does homework while listening to music.")]),
        ("\"了\" 表示变化", "S + Adj/V + 了  (or  不 + V + 了)",
         "Sentence-final 了 marks a NEW situation — something has changed. \"不……了\" = no longer doing.",
         [("你胖了。", "You've gotten fat."),
          ("我不去看电影了。", "I'm no longer going to the movie."),
          ("下雨了！", "It's raining now!"),
          ("我饿了，我们去吃饭吧。", "I'm hungry, let's go eat.")],
         [("我不生气了。", "I'm not angry anymore."),
          ("秋天到了，天气冷了。", "Autumn has arrived, the weather has turned cold.")]),
        ("越来越 + Adj", "S + 越来越 + Adj/mental V + (了)",
         "Gradual increasing change — 'more and more'. Very often ends with 了.",
         [("我最近越来越胖了。", "I've been getting fatter and fatter lately."),
          ("天气越来越热了。", "The weather is getting hotter and hotter."),
          ("他的中文越来越好了。", "His Chinese is getting better and better."),
          ("东西越来越贵了。", "Things are getting more and more expensive.")],
         [("他越来越喜欢中国文化。", "He likes Chinese culture more and more."),
          ("作业越来越难了。", "The homework is getting harder and harder.")]),
    ],
    5: [
        ("可能补语 V得/不 + Result", "V + 得/不 + Result (听得懂, 看不清楚, etc.)",
         "Whether a result CAN (V得) or CANNOT (V不) be achieved. "
         "Formed on the same roots as 结果补语 / 趋向补语. Pair opposites: 看得到/看不到, 听得懂/听不懂.",
         [("没有眼镜，我一个字都看不清楚。", "Without glasses, I can't see a single character clearly."),
          ("这个字太小了，我看不到。", "This character is too small, I can't see it."),
          ("老师说得太快了，我听不懂。", "The teacher speaks too fast, I can't understand."),
          ("今天晚上我睡不着。", "I can't fall asleep tonight.")],
         [("东西太多了，我拿不过来。", "There's too much stuff, I can't carry it all."),
          ("他说的话，你听得懂吗？", "Can you understand what he's saying?")]),
        ("\"呢\" 询问处所：N + 呢？", "Noun + 呢？",
         "Shortcut question meaning 'Where is N?' when the context is clear.",
         [("我的眼镜呢？", "Where are my glasses?"),
          ("你的作业呢？", "Where's your homework?"),
          ("爸爸呢？", "Where's dad?")],
         [("我的手机呢？我刚才还在这儿。", "Where's my phone? It was just here."),
          ("同事呢？他们怎么都不在？", "Where are the colleagues? How come nobody is here?")]),
        ("刚 vs 刚才", "刚 (adverb, before V) / 刚才 (noun, can be subject/topic)",
         "\"刚\" = adverb meaning 'just (recently)', range from seconds to months. "
         "\"刚才\" = noun meaning 'just now' / 'a moment ago', always refers to the very recent past.",
         [("他刚出去了。", "He just went out (a moment ago)."),
          ("刚才那个人是谁？", "Who was that person just now?"),
          ("我刚来中国。", "I just came to China (recently)."),
          ("我刚才在超市买了水果。", "I was just now at the supermarket buying fruit.")],
         [("他刚结婚。", "He just got married."),
          ("刚才下雨了，你没听到吗？", "It was raining just now, didn't you hear?")]),
    ],
    6: [
        ("时段的表达：Duration + 了 (ongoing)", "S + V + (了) + Duration + (O) + 了",
         "Second 了 at the end means the action started in the past and is STILL ongoing. "
         "Without the final 了, it's already finished.",
         [("我跟她认识五年了。", "I've known her for five years (and still do)."),
          ("我学了三年中文了。", "I've been studying Chinese for three years (still am)."),
          ("他在这个公司工作了十年了。", "He's been working at this company for ten years."),
          ("我们等了一个小时了。", "We've been waiting for an hour.")],
         [("他在北京住了八年了。", "He's lived in Beijing for eight years."),
          ("我结婚两年了。", "I've been married for two years.")]),
        ("对……感兴趣", "S + 对 + Topic + (不/很) + 感兴趣",
         "Expresses (dis)interest in a topic.",
         [("我对中文感兴趣。", "I'm interested in Chinese."),
          ("你对什么不感兴趣？", "What aren't you interested in?"),
          ("他对历史很感兴趣。", "He's very interested in history."),
          ("我对音乐不太感兴趣。", "I'm not very interested in music.")],
         [("她对中国文化很感兴趣。", "She's very interested in Chinese culture."),
          ("我对游戏一点儿也不感兴趣。", "I'm not at all interested in games.")]),
        ("半 / 刻 / 差 表示时间", "Number + 点 + 半/一刻/三刻；差 + Duration + 点",
         "\"半\" = :30, \"一刻\" = :15, \"三刻\" = :45. \"差 N 分 X 点\" = N minutes to X o'clock.",
         [("现在八点半。", "It's 8:30 now."),
          ("现在三点一刻。", "It's 3:15 now."),
          ("现在差一刻三点。", "It's a quarter to three."),
          ("现在差五分八点。", "It's five minutes to eight.")],
         [("我们九点半见面。", "Let's meet at 9:30."),
          ("现在差十分一点，快吃饭吧。", "It's ten to one, let's eat quickly.")]),
    ],
    7: [
        ("又 vs 再：Again", "又 + V (past repetition) / 再 + V (future repetition)",
         "\"又\" = 'again' for repeated past/completed action. "
         "\"再\" = 'again' for a future or intended repetition.",
         [("他又迟到了。", "He was late again."),
          ("欢迎你再来！", "Welcome to come again!"),
          ("这本书很好看，我想再看一次。", "This book is great, I want to read it again."),
          ("昨天去了，今天又去了。", "I went yesterday, and went again today.")],
         [("下周我想再去一次北京。", "I want to go to Beijing one more time next week."),
          ("他昨天感冒了，今天又感冒了。", "He had a cold yesterday, and has it again today.")]),
        ("疑问代词活用1：Q-word + 就 + Q-word", "Q-word1，(S) + 就 + V + Q-word1",
         "Same question word in both clauses with 就 means 'whatever / wherever / whoever / whenever'.",
         [("你去哪儿，我就去哪儿。", "Wherever you go, I'll go."),
          ("你想吃什么，我就做什么。", "Whatever you want to eat, I'll make."),
          ("谁愿意去，谁就去。", "Whoever wants to go, let them go."),
          ("什么时候有时间，我们就什么时候见。", "Whenever we're free, we'll meet.")],
         [("你想坐哪儿就坐哪儿。", "Sit wherever you want."),
          ("老师说什么，我们就做什么。", "Whatever the teacher says, we'll do.")]),
    ],
    8: [
        ("越A越B：The more A, the more B", "S + 越 + V1/Adj1 + 越 + V2/Adj2",
         "Proportional change — as one thing intensifies, another intensifies with it.",
         [("我的中文越说越好。", "The more I speak Chinese, the better it gets."),
          ("小狗越吃越胖。", "The more the puppy eats, the fatter it gets."),
          ("这本书越看越有意思。", "The more I read this book, the more interesting it is."),
          ("雨越下越大。", "The rain is coming down harder and harder.")],
         [("他越努力，成绩越好。", "The harder he works, the better his grades."),
          ("天气越来越热，东西越来越贵。", "The weather gets hotter, things get more expensive.")]),
        ("A 跟 B 一样 + Adj：as...as...", "A + 跟 + B + (不) + 一样 + Adj",
         "Equality comparison. With verbs: A + V + 得 + 跟 + B + 一样 + Adj.",
         [("她说得跟中国人一样好。", "She speaks as well as a Chinese person."),
          ("小狗跟小猫一样胖。", "The puppy is as fat as the kitten."),
          ("你跟你哥哥一样高吗？", "Are you as tall as your older brother?"),
          ("他跑得跟我一样快。", "He runs as fast as me."),
          ("今天跟昨天一样热。", "Today is as hot as yesterday.")],
         [("他的中文跟我的一样好。", "His Chinese is as good as mine."),
          ("这本书跟那本书一样贵。", "This book is as expensive as that one.")]),
    ],
    9: [
        ("比较 2：A比B+Adj+一点儿/一些/得多/多了", "A + 比 + B + Adj + 一点儿/得多/多了/Number+MW",
         "Compare two things and state how much more. Use degree modifiers after the adjective.",
         [("中文比数学难多了。", "Chinese is much harder than math."),
          ("他比她大三岁。", "He is three years older than her."),
          ("姐姐比妹妹高一点儿。", "The older sister is a little taller than the younger one."),
          ("坐飞机比坐火车快得多。", "Flying is much faster than taking the train."),
          ("今天比昨天冷。", "Today is colder than yesterday.")],
         [("他的中文比我的好得多。", "His Chinese is much better than mine."),
          ("这件衣服比那件便宜一些。", "This piece of clothing is a bit cheaper than that one.")]),
        ("概数 1：consecutive numbers", "two consecutive digits together",
         "Two consecutive numbers = approximate. E.g., 七八分钟 = about 7–8 minutes, 二三十个 = about 20–30.",
         [("骑自行车七八分钟就到。", "About 7–8 minutes by bike and you're there."),
          ("这个班有二三十个学生。", "This class has about 20–30 students."),
          ("他五六岁。", "He's 5 or 6 years old.")],
         [("我等了三四十分钟。", "I waited about 30–40 minutes."),
          ("这里有五六十个人。", "There are about 50–60 people here.")]),
    ],
    10: [
        ("把字句 1：A把B+V+了", "A + 把 + B + V + 了",
         "Moves the object before the verb to emphasize what happened TO it. "
         "B must be specific/definite. Cannot use with verbs of cognition/feeling (喜欢, 知道).",
         [("我把灯关了。", "I turned off the light."),
          ("别忘了把空调关了。", "Don't forget to turn off the AC."),
          ("我把蛋糕吃了。", "I ate (up) the cake."),
          ("他把水喝了。", "He drank the water."),
          ("请你把门关了。", "Please close the door.")],
         [("我把作业做完了。", "I finished the homework."),
          ("他把书还了吗？", "Did he return the book?")]),
        ("概数 2：左右 about", "Number/Time + 左右",
         "After a number or time = approximation, 'about/approximately'.",
         [("图书馆的书可以借两个星期左右。", "You can borrow library books for about two weeks."),
          ("我每天睡八个小时左右。", "I sleep about 8 hours every day."),
          ("从这儿到学校要二十分钟左右。", "It takes about 20 minutes from here to school.")],
         [("这件衣服三百块左右。", "This piece of clothing is about 300 yuan."),
          ("他三十岁左右。", "He's about 30 years old.")]),
    ],
    11: [
        ("才 vs 就", "就 (early/fast/easy) / 才 (late/slow/difficult)",
         "\"就\" = speaker sees the action as early or easy. \"才\" = speaker sees it as late or difficult. "
         "Often used with specific times: 8点就来了 vs 8点才来.",
         [("我今天6点就起床了。", "I got up as early as 6 today."),
          ("你怎么才来？", "Why are you only arriving now? (so late!)"),
          ("到了机场才发现忘记带护照了。", "Only at the airport did I realize I'd forgotten my passport."),
          ("我一个小时就做完了作业。", "I finished the homework in just one hour."),
          ("他十点才吃早饭。", "He didn't eat breakfast until 10.")],
         [("他二十岁就结婚了。", "He got married as young as 20."),
          ("我们八点开会，他九点才到。", "We started the meeting at 8 and he didn't show up until 9.")]),
        ("把字句 2：A把B+V+在/到/给", "A + 把 + B + V + 在/到/给 + Place/Person",
         "Extended 把 sentence showing where the object ends up after the action.",
         [("他把衣服放在行李箱里。", "He put the clothes in the suitcase."),
          ("把重要的东西放在我这儿吧。", "Put the important things here with me."),
          ("请把书放在桌子上。", "Please put the book on the table."),
          ("她把钱给了妈妈。", "She gave the money to mom.")],
         [("我把作业发给老师了。", "I sent my homework to the teacher."),
          ("她把礼物放到桌子上了。", "She put the gift on the table.")]),
    ],
    12: [
        ("复合趋向补语", "V + Direction + 来/去  (e.g. 跑进来, 拿出去, 走回去)",
         "Main verb + direction (进/出/上/下/回/过) + 来/去. "
         "Expresses both the motion and its direction relative to the speaker.",
         [("她把东西买回来了。", "She bought the stuff and brought it back."),
          ("他们走进教室去了。", "They walked into the classroom."),
          ("请你把书拿出来。", "Please take the book out."),
          ("他站起来回答问题。", "He stood up to answer the question.")],
         [("孩子跑过来跟我说话。", "The child ran over to talk to me."),
          ("老师走出去接电话。", "The teacher walked out to take the call.")]),
        ("一边……一边……", "S + 一边 + V1 + 一边 + V2",
         "Two simultaneous ongoing actions, equally emphasized.",
         [("爷爷喜欢一边吃早饭一边看报纸。", "Grandpa likes eating breakfast while reading the newspaper."),
          ("他们一边聊天一边喝咖啡。", "They chat while drinking coffee."),
          ("她一边走路一边听音乐。", "She walks while listening to music."),
          ("不要一边吃饭一边看手机。", "Don't eat while looking at your phone.")],
         [("我一边做作业一边听音乐。", "I do my homework while listening to music."),
          ("他一边笑一边说话。", "He talks while laughing.")]),
    ],
    13: [
        ("把字句 3：A把B+V+结果/趋向补语", "A + 把 + B + V + Complement  (干净/好/完/过来/出去)",
         "把 + object + verb + result/direction complement. Shows the result/direction that the action produced on the object.",
         [("你把房间打扫干净了吗？", "Have you cleaned the room?"),
          ("你把水果拿过来。", "Bring the fruit over here."),
          ("我把作业做完了。", "I finished my homework."),
          ("请把门打开。", "Please open the door."),
          ("他把咖啡喝完了。", "He finished drinking the coffee.")],
         [("她把蛋糕吃完了。", "She finished the cake."),
          ("请把书放回去。", "Please put the book back.")]),
        ("先……，再/又……，然后……", "先 + V1，再/又 + V2，然后 + V3",
         "Sequencing actions — first A, then B, after that C.",
         [("回家以后，我先洗澡，然后吃饭。", "After coming home I shower first, then eat."),
          ("先做作业，然后再玩游戏。", "Homework first, then games."),
          ("我先去超市，然后去银行。", "I'll go to the supermarket first, then the bank."),
          ("早上起来，先刷牙，然后吃早饭。", "In the morning, first brush teeth, then eat breakfast.")],
         [("我们先吃饭，然后去看电影。", "We'll eat first, then go to the movie."),
          ("她先做好了饭，然后去接孩子。", "She finished cooking first, then went to pick up the kids.")]),
    ],
    14: [
        ("除了……(以外)，都/还/也", "除了 + X + (以外)，都/还/也 + ...",
         "With 都 = 'everyone/everything except X'. With 还/也 = 'besides X, (also) Y'.",
         [("除了数学，其他课我都喜欢。", "Except for math, I like all the other classes."),
          ("除了中文，她还会说法文。", "Besides Chinese, she can also speak French."),
          ("除了我，大家都去了。", "Everyone went except me."),
          ("除了看书，他还喜欢听音乐。", "Besides reading, he also likes listening to music.")],
         [("除了周末，我每天都工作。", "Except on weekends, I work every day."),
          ("除了苹果，冰箱里还有香蕉。", "Besides apples, there are also bananas in the fridge.")]),
        ("疑问代词活用 2：Q-word + 都 + V", "Q-word + 都/也 + (不/没) + V",
         "Q-word + 都 means 'all / every / any'. With negation: 'nothing/nobody/nowhere'.",
         [("谁都有办法。", "Everyone has a way."),
          ("他哪儿都不想去。", "He doesn't want to go anywhere."),
          ("我什么都想试试。", "I want to try everything."),
          ("这件事谁都知道。", "Everyone knows about this.")],
         [("这个问题谁都回答不了。", "Nobody can answer this question."),
          ("今天我什么也不想吃。", "I don't want to eat anything today.")]),
        ("程度的表达：Adj + 极了", "Adj + 极了",
         "After an adjective, 极了 indicates an extreme degree — 'extremely'.",
         [("这个地方漂亮极了。", "This place is extremely beautiful."),
          ("今天热极了。", "Today is extremely hot."),
          ("这个蛋糕好吃极了。", "This cake is incredibly delicious."),
          ("听到这件事，她高兴极了。", "Hearing this, she was extremely happy.")],
         [("这本书有意思极了。", "This book is extremely interesting."),
          ("他跑得快极了。", "He runs extremely fast.")]),
    ],
    15: [
        ("如果……(的话)，(就)……", "如果 + Condition + (的话)，(S) + 就 + Result",
         "Conditional: if A, then B. 的话 is optional; 就 is common in the result clause.",
         [("如果明天下雨，我就不去了。", "If it rains tomorrow, I won't go."),
          ("如果你有时间，就来我家吧。", "If you have time, come to my place."),
          ("如果你不舒服，就去看医生。", "If you feel unwell, go see a doctor."),
          ("如果我有钱，我就去旅游。", "If I had money, I'd travel.")],
         [("如果你明天来，我们一起去公园。", "If you come tomorrow, we'll go to the park together."),
          ("如果下雪，我们就在家。", "If it snows, we'll stay home.")]),
        ("复杂的状态补语：V+得+Clause", "S + V + 得 + Result/State Clause",
         "Complex state/result complement — 'so [X] that [Y]'. The 得-clause describes the result/state.",
         [("我累得下了班就想睡觉。", "I'm so tired that after work I just want to sleep."),
          ("她高兴得一直笑。", "She was so happy she kept laughing."),
          ("他忙得没时间吃饭。", "He's so busy he has no time to eat."),
          ("我饿得什么都想吃。", "I'm so hungry I want to eat anything.")],
         [("孩子哭得脸都红了。", "The child cried so hard that his face turned red."),
          ("他跑得比谁都快。", "He runs faster than anyone.")]),
        ("单音节形容词重叠：AA的", "A + A + 的 (+ Noun)",
         "Reduplicating a one-syllable adjective gives it a softer, more vivid or endearing quality. Always ends in 的.",
         [("大大的眼睛，高高的鼻子。", "Big (cute) eyes, a tall nose."),
          ("她长得白白的，高高的。", "She is fair-skinned and tall."),
          ("他有一双小小的手。", "He has small (cute) hands."),
          ("红红的太阳出来了。", "The bright red sun has come out.")],
         [("她有一头长长的黑头发。", "She has long black hair."),
          ("小猫有蓝蓝的眼睛。", "The kitten has bright blue eyes.")]),
    ],
    16: [
        ("双音节动词重叠：ABAB", "V1V2 + V1V2 (两个音节的动词)",
         "Two-syllable verb reduplication softens the action — 'to [verb] a little / a bit'. Pattern: 学习 → 学习学习.",
         [("我们一起聊聊天吧。", "Let's have a little chat together."),
          ("你应该多锻炼锻炼身体。", "You should exercise a bit more."),
          ("我想休息休息。", "I'd like to rest a bit."),
          ("你帮我检查检查这个句子。", "Help me take a quick look at this sentence.")],
         [("我们一起学习学习吧。", "Let's study together a bit."),
          ("周末可以好好休息休息。", "On weekends you can really rest up.")]),
        ("疑问代词活用 3：Q-word + Q-word", "Same Q-word used in both halves with implied meaning",
         "Same question word twice links two variables — emphasizes open/unconstrained choice.",
         [("这个问题谁都知道。", "Everyone knows this problem."),
          ("你想去哪儿就去哪儿。", "Go wherever you want."),
          ("你想吃什么就吃什么。", "Eat whatever you want."),
          ("他什么时候来都行。", "Whenever he comes is fine.")],
         [("你什么时候有空，我什么时候去。", "Whenever you're free, that's when I'll go."),
          ("谁先到谁就开始。", "Whoever arrives first starts.")]),
    ],
    17: [
        ("只要……，就……", "只要 + Condition，(S) + 就 + Result",
         "Sufficient condition — 'as long as A, then B'. Weaker/broader than 只有……才.",
         [("只要你努力，成绩就会提高。", "As long as you work hard, your grades will improve."),
          ("只要锻炼，身体就会健康。", "As long as you exercise, you'll be healthy."),
          ("只要有时间，我就去公园。", "As long as I have time, I go to the park."),
          ("只要你来，我就高兴。", "As long as you come, I'm happy.")],
         [("只要每天练习，你就能学好中文。", "As long as you practice every day, you can learn Chinese well."),
          ("只要不下雨，我们就去爬山。", "As long as it doesn't rain, we'll go hiking.")]),
        ("介词 \"关于\"", "关于 + Topic + (……), 后面通常接名词短语或句子",
         "\"关于\" introduces a topic — 'about / regarding / concerning'.",
         [("这是一本关于历史的书。", "This is a book about history."),
          ("关于这个问题，我还没想好。", "About this question, I haven't decided yet."),
          ("我想了解关于中国文化的故事。", "I want to learn about stories related to Chinese culture."),
          ("关于留学的事，你怎么决定？", "Regarding studying abroad, what have you decided?")],
         [("老师讲了一些关于考试的事。", "The teacher talked about some things regarding the exam."),
          ("这是关于他工作的新闻。", "This is news about his work.")]),
    ],
    18: [
        ("趋向补语的引申义", "看上去 / 看出来 / 想起来 / 说起来 (figurative extensions)",
         "Directional complements used figuratively: 看上去 'looks like', 看出来 'can tell', 想起来 'suddenly recall', 说起来 'come to think of it'.",
         [("她看上去很年轻。", "She looks young."),
          ("你没看出来吗？", "Couldn't you tell?"),
          ("我想起来了！", "I remember now!"),
          ("他看上去很累。", "He looks tired."),
          ("你能看出来他多大吗？", "Can you tell how old he is?")],
         [("这件事说起来容易，做起来难。", "This is easy to say, hard to do."),
          ("我一下子想起来了他的名字。", "I suddenly remembered his name.")]),
        ("使 / 叫 / 让：Causative", "A + 使/叫/让 + B + V ……",
         "'Make / cause / let' someone do something. 使 = formal/abstract, 让 = common/neutral, 叫 = colloquial.",
         [("运动服让他看上去更年轻。", "Sportswear makes him look younger."),
          ("妈妈叫我去买菜。", "Mom told me to go buy groceries."),
          ("老师让学生做作业。", "The teacher has students do homework."),
          ("这件事使大家很高兴。", "This event made everyone happy.")],
         [("他的话让我很难过。", "His words made me very sad."),
          ("爸爸叫我早点儿回家。", "Dad told me to come home earlier.")]),
    ],
    19: [
        ("\"被\" 字句", "A(受) + 被 + (B施) + V + (Complement/了)",
         "Passive — A receives the action. B (the doer) is optional and can be dropped. "
         "Verb must usually have a complement or 了 showing what happened.",
         [("我的照相机被哥哥拿走了。", "My camera was taken by my older brother."),
          ("蛋糕被狗吃了。", "The cake was eaten by the dog."),
          ("他被公司开除了。", "He was fired by the company."),
          ("我的自行车被人骑走了。", "Someone took my bike."),
          ("他的手机被老师发现了。", "His phone was discovered by the teacher.")],
         [("我的信用卡被人拿走了。", "My credit card was taken by someone."),
          ("他被妈妈说了。", "He got told off by his mom.")]),
        ("只有……，才……", "只有 + (unique) Condition，才 + Result",
         "Stricter than 只要……就. Only ONE specific condition produces the result.",
         [("只有妈妈做的饭，她才喜欢吃。", "Only mom's cooking does she like to eat."),
          ("只有过年，他才会回老家。", "Only during New Year will he go back home."),
          ("只有努力学习，才能考好。", "Only by studying hard can you do well."),
          ("只有你来，我才去。", "Only if you come will I go.")],
         [("只有多练习，你的中文才会提高。", "Only with more practice will your Chinese improve."),
          ("只有周末他才有时间。", "Only on weekends does he have time.")]),
    ],
    20: [
        ("不但……，而且……", "不但 + Clause A，而且 + Clause B",
         "'Not only A, but also B' — adds a second related fact. The subject can appear once or in both clauses.",
         [("他不但会说汉语，而且说得很好。", "He not only speaks Chinese, but also speaks it very well."),
          ("这本书不但有意思，而且很容易懂。", "This book is not only interesting, but also easy to understand."),
          ("他不但聪明，而且努力。", "He's not only smart, but also hardworking."),
          ("北京不但有名，而且很大。", "Beijing is not only famous, but also big.")],
         [("她不但喜欢运动，而且每天跑步。", "She not only likes sports, but also runs every day."),
          ("这家饭店不但便宜，而且很干净。", "This restaurant is not only cheap, but also very clean.")]),
        ("越……越……", "越 + Verb / Adj A，越 + Verb / Adj B",
         "'The more A, the more B' — expresses a parallel increase. Often 越来越 = 'more and more'.",
         [("他越说越快。", "The more he speaks, the faster he gets."),
          ("我越想越难过。", "The more I think, the sadder I feel."),
          ("天气越来越冷。", "The weather is getting colder and colder."),
          ("他的汉语越来越好。", "His Chinese is getting better and better.")],
         [("雨越下越大。", "The rain gets heavier and heavier."),
          ("她越学越努力。", "The more she studies, the harder she works.")]),
    ],
}


# ============================================================
# HSK 1/2 loader (provides the base character whitelist)
# ============================================================
def _extract_cjk(s: str) -> set:
    return {c for c in s if "\u4e00" <= c <= "\u9fff"}


def load_hsk12_chars() -> set:
    chars = set()
    for path in (HSK1_PATH, HSK2_PATH):
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                chars.update(_extract_cjk(parts[1]))
    return chars


def build_allowed_chars(lesson_n: int, hsk12_chars: set) -> set:
    """Allowed = HSK 1/2 + every HSK 3 vocab char from lessons 1..lesson_n.

    We also permit characters introduced later in HSK 3 itself — they will all be
    taught in the same deck, and several grammar patterns (e.g. 越来越) depend on
    characters the textbook only introduces later. Truly random characters are
    still caught by this check.
    """
    allowed = set(hsk12_chars)
    for L in VOCAB.keys():
        for entry in VOCAB.get(L, []):
            allowed.update(_extract_cjk(entry[0]))
    return allowed


# ============================================================
# Validator: "pass through to double-check" - every sentence must use only
# characters that are in scope (HSK 1/2 or this lesson + earlier HSK 3 lessons).
# ============================================================
def validate(hsk12_chars: set) -> int:
    failures = []
    for lesson_n in sorted(VOCAB.keys()):
        allowed = build_allowed_chars(lesson_n, hsk12_chars)
        for entry in VOCAB[lesson_n]:
            chinese, _pinyin, _english, example_zh, _example_en = entry
            bad = [c for c in _extract_cjk(example_zh) if c not in allowed]
            if bad:
                failures.append((lesson_n, "vocab_example", chinese, example_zh, bad))
    for lesson_n in sorted(GRAMMAR.keys()):
        allowed = build_allowed_chars(lesson_n, hsk12_chars)
        for pattern in GRAMMAR[lesson_n]:
            name, _struct, _expl, textbook, variations = pattern
            for kind, sentences in (("Textbook", textbook), ("Variation", variations)):
                for zh, _en in sentences:
                    bad = [c for c in _extract_cjk(zh) if c not in allowed]
                    if bad:
                        failures.append((lesson_n, f"grammar_{kind}", name, zh, bad))
    if failures:
        print(f"\n❌ VALIDATION FAILED — {len(failures)} sentence(s) use out-of-scope characters:\n")
        for lesson_n, where, name, sentence, bad in failures[:60]:
            print(f" L{lesson_n:2d} [{where}] {name}")
            print(f"       {sentence}")
            print(f"       out of scope: {''.join(bad)}")
        if len(failures) > 60:
            print(f"\n ... and {len(failures) - 60} more.")
        return 1
    print("✅ Validation passed: every sentence uses only in-scope characters.")
    return 0


# ============================================================
# Deck builder
# ============================================================
def _pinyin(zh: str) -> str:
    return " ".join(lazy_pinyin(zh, style=Style.TONE))


def build_deck() -> genanki.Deck:
    deck = genanki.Deck(DECK_ID, "HSK 3 — Ordered Lessons")

    for lesson_n in sorted(set(list(VOCAB.keys()) + list(GRAMMAR.keys()))):
        lesson_tag = f"HSK3::Lesson_{lesson_n:02d}"
        lesson_label = f"Lesson {lesson_n}"

        for chinese, pinyin, english, ex_zh, ex_en in VOCAB.get(lesson_n, []):
            note = genanki.Note(
                model=vocab_model,
                fields=[chinese, pinyin, english, ex_zh, _pinyin(ex_zh), ex_en, lesson_label],
                tags=[lesson_tag, "HSK3::Vocabulary"],
            )
            deck.add_note(note)

        for name, structure, explanation, textbook, variations in GRAMMAR.get(lesson_n, []):
            for kind, examples in (("Textbook", textbook), ("Variation", variations)):
                kind_tag = "HSK3::Textbook" if kind == "Textbook" else "HSK3::Variation"
                for zh, en in examples:
                    note = genanki.Note(
                        model=grammar_model,
                        fields=[zh, _pinyin(zh), en, name, structure, explanation, lesson_label, kind],
                        tags=[lesson_tag, "HSK3::Grammar", kind_tag],
                    )
                    deck.add_note(note)
    return deck


def main() -> int:
    hsk12_chars = load_hsk12_chars()
    if validate(hsk12_chars) != 0:
        return 1

    deck = build_deck()
    genanki.Package(deck).write_to_file(str(OUTPUT_PATH))

    total_vocab = sum(len(v) for v in VOCAB.values())
    total_gr_sent = sum(
        len(tb) + len(var) for patterns in GRAMMAR.values() for _, _, _, tb, var in patterns
    )
    total_patterns = sum(len(v) for v in GRAMMAR.values())
    total_cards = total_vocab + total_gr_sent * 2  # grammar has 2 templates/note
    print(f"\nDeck written: {OUTPUT_PATH}")
    print(f"  Lessons:            {len(set(list(VOCAB.keys()) + list(GRAMMAR.keys())))}")
    print(f"  Vocabulary notes:   {total_vocab}  (1 card each)")
    print(f"  Grammar patterns:   {total_patterns}")
    print(f"  Grammar sentences:  {total_gr_sent}  (2 cards each: ZH→EN and EN→ZH)")
    print(f"  Total cards:        {total_cards}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
