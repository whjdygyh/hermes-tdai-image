#!/usr/bin/env python3
"""
song_crafter.py — 一键出歌引擎

从songwriting_knowledge_base.json读取专业知识，
根据用户输入（流派/情绪/主题/时长/语言/唱法）生成专业歌词+tags，
并自动调用HeartMuLa生成歌曲。

用法:
  python song_crafter.py --genre "pop" --mood "happy" --theme "summer" --duration 60 --language "cn"
  python song_crafter.py --genre "rock" --mood "angry" --theme "rebellion" --duration 90 --language "cn" --auto
"""

import json
import os
import sys
import random
import argparse
from pathlib import Path
from typing import Optional

# ─── 路径 ────────────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent.resolve()
REF_DIR = SKILL_DIR / "references"
HEARTLIB_DIR = SKILL_DIR.parent.parent.parent / "home" / "heartlib"
ASSETS_DIR = HEARTLIB_DIR / "assets"

# ─── 加载知识库 ──────────────────────────────────────────────────
with open(REF_DIR / "songwriting_knowledge_base.json", encoding="utf-8") as f:
    KB = json.load(f)

GENRES = KB["global_music_genres"]["genres"]
STRUCTURES = KB["song_structure_templates"]
VOCAL_TECHNIQUES = KB["vocal_techniques"]
INSTRUMENTS = KB["instruments_and_timbres"]
MULTILINGUAL = KB["multilingual_lyric_writing"]
ETHNIC = KB["ethnic_music_characteristics"]


# ─── 工具函数 ────────────────────────────────────────────────────
def pick_subgenre(genre_key: str) -> dict:
    """从流派中随机选一个子流派"""
    genre = GENRES[genre_key]
    sub_key = random.choice(list(genre["subgenres"].keys()))
    return genre["subgenres"][sub_key], sub_key


def calculate_lines_for_duration(duration_sec: int) -> int:
    """根据目标时长计算需要的歌词行数"""
    mapping = {15: (4, 6), 30: (12, 16), 45: (18, 22), 60: (24, 30), 90: (36, 45)}
    best = min(mapping.keys(), key=lambda k: abs(k - duration_sec))
    lo, hi = mapping[best]
    return random.randint(lo, hi)


def syllable_weight(word: str) -> int:
    """粗略估算中文字的音节权重（中文每个字≈0.5秒）"""
    return len(word) * 50  # ms


def get_structure_for_duration_mood(duration_sec: int, mood: str, genre_key: str) -> list:
    """根据时长和情绪获取曲式结构"""
    if genre_key == "electronic":
        return ["[Build Up]", "[Drop]", "[Breakdown]", "[Drop]", "[Outro]"]
    
    if duration_sec <= 20:
        return ["[Verse]", "[Outro]"]
    elif duration_sec <= 35:
        return ["[Verse 1]", "[Chorus]", "[Outro]"]
    elif duration_sec <= 50:
        return ["[Verse 1]", "[Chorus]", "[Verse 2]", "[Chorus]", "[Outro]"]
    elif duration_sec <= 75:
        return ["[Verse 1]", "[Chorus]", "[Verse 2]", "[Chorus]", "[Bridge]", "[Chorus]", "[Outro]"]
    else:
        return ["[Intro]", "[Verse 1]", "[Chorus]", "[Verse 2]", "[Chorus]", "[Bridge]", "[Chorus]", "[Outro]"]


# ─── 歌词生成引擎 ────────────────────────────────────────────────
RHYME_SCHEMES = ["AABB", "ABAB", "ABCB", "internal_rhyme"]
NARRATIVE_STRUCTURES = ["linear", "imagery_cluster", "scene_dialogue", "起承转合", "stream_of_consciousness"]

OPENING_KICKERS = {
    "happy": ["太阳出来了", "心跳在加速", "风都是甜的", "今天不一样", "笑容藏不住"],
    "sad": ["雨下了整夜", "空房间很冷", "影子拉得很长", "窗台上的灰", "最后那班车"],
    "angry": ["我真的受够了", "把墙砸个洞", "烧掉这些照片", "你听不见吗", "最后一根稻草"],
    "nostalgic": ["翻开旧照片", "那年的夏天", "老唱片在转", "巷子口的树", "你还记得吗"],
    "romantic": ["你的眼睛里有星星", "第一次牵你的手", "月光洒在肩上", "全世界只剩你", "在最深的夜里"],
    "energetic": ["准备好出发吧", "油门踩到底", "没有什么能阻挡", "燃烧吧今晚", "冲向地平线"],
    "dreamy": ["在云朵上跳舞", "星星在说话", "梦里的颜色", "黑暗中发光", "悬浮在半空"],
    "melancholic": ["落葉鋪成路", "晚風吹過肩", "城市的燈火", "一個人走著", "時間停下了"],
    "rebellious": ["規則是拿來打破的", "我不在乎你怎麼說", "自己的路自己走", "把我逼到極限了", "寧可燒光也不回頭"],
    "peaceful": ["清晨的第一道光", "湖面沒有波紋", "鳥鳴代替了鬧鐘", "慢慢呼吸就好", "一切都剛剛好"],
}

VERSE_STARTERS = {
    "cn": [
        "在/无人的街道/我/独自/走著",
        "窗外的/霓虹/閃爍/不停",
        "收音機/傳來/一段/熟悉/旋律",
        "時間/像/流沙/從/指縫/溜走",
        "夢/醒了/之後/剩下/什麼",
        "這城市/太吵/我/聽不到/心跳",
        "月光/灑在/老舊的/站牌上",
        "把/回憶/裝進/空的/瓶子裡",
        "雲/不知道/自己要/飄去/哪裡",
        "你說/明天/會是/嶄新的/一天",
    ],
    "en": [
        "I woke up to the sound of rain",
        "The city lights are burning bright tonight",
        "Lost in a maze of memories",
        "Every step feels like a thousand miles",
        "The clock keeps ticking but I'm standing still",
        "We were born to run, born to chase the sun",
        "Nothing's gonna bring us down tonight",
        "I've been waiting for a sign from above",
        "The world's on fire but we're dancing in the rain",
        "Just another day in paradise",
    ],
    "jp": [
        "朝の光が窓を叩く",
        "記憶の中をさまよう",
        "星が消える前に伝えたい",
        "風に乗せて歌を届ける",
        "明日はきっと素敵な日",
    ],
}

CHORUS_HOOKS = {
    "cn": [
        "就讓/我/飛/吧 /不/回頭/的/飛",
        "這是/我們的/時代 /誰也/不能/阻擋",
        "你/是/我的/光 /在/最/黑/的/夜/裡",
        "別/說/再見 /我們/會/再/相遇",
        "燃燒/吧 /像/從來/沒有/受傷/過",
        "一直/走 /走到/世界/的/盡頭",
        "不管/明天/會/怎樣 /我/都要/大聲/唱",
        "你/聽見/了嗎 /這/是/我的/回答",
        "讓/風/帶走/所有/悲傷 /我/只要/向前",
        "在/最/深/的/夜/裡 /我們/擁有/彼此",
    ],
    "en": [
    "We'll fly so high, touch the sky, never say goodbye",
    "This is our time, watch us shine, we'll be alright",
    "You are the light, in the night, burning so bright",
    "We don't need a reason, just the feeling of the season",
    "Run away, far away, to a place where we can stay",
    "Heartbeat racing, never pacing, we keep chasing",
    "I won't break, I won't bend, this is not the end",
    "We were made for the fire, fueled by desire",
    "Take my hand, understand, we're in a promised land",
    "Lost in the sound, spinning around, never coming down",
    ],
    "jp": [
        "飛び出そう どこまでも 行ける",
        "この瞬間を 忘れない 永遠に",
        "夢を追いかけて 諦めない",
    ],
}


def pick_rhyme_scheme() -> str:
    return random.choice(RHYME_SCHEMES)


def pick_narrative() -> str:
    return random.choice(NARRATIVE_STRUCTURES)


def generate_verse_line(verse_num: int, theme: str, mood: str, language: str, rhyme_word: str = "") -> str:
    """生成一句verse歌词"""
    starters = VERSE_STARTERS.get(language, VERSE_STARTERS["cn"])
    base = random.choice(starters)
    
    if theme:
        theme_words_map = {
            "summer": ["蝉鸣", "烈日", "海滩", "冰棍", "浪花"],
            "rain": ["雨滴", "潮湿", "雨伞", "水洼", "阴天"],
            "night": ["星光", "深夜", "路灯", "失眠", "黑暗"],
            "journey": ["地图", "远方", "公路", "背包", "方向"],
            "love": ["拥抱", "亲吻", "掌心", "心跳", "温柔"],
            "friendship": ["朋友", "一起", "干杯", "笑聲", "約定"],
            "freedom": ["翅膀", "籠子", "解脫", "天空", "奔跑"],
            "rebellion": ["打破", "规则", "自由", "反抗", "挣脱"],
            "hope": ["黎明", "种子", "春天", "光", "明天"],
            "loneliness": ["一個人", "影子", "空", "孤單", "沉默"],
            "dream": ["夢", "幻覺", "想像", "飛翔", "星"],
            "nature": ["山", "河流", "森林", "風", "大地"],
            "war": ["戰火", "傷疤", "英雄", "和平", "家園"],
            "nostalgia": ["回憶", "舊時光", "童年", "老地方", "那時"],
            "cyberpunk": ["霓虹", "晶片", "網路", "代碼", "機械"],
        }
        if theme in theme_words_map:
            words = theme_words_map[theme]
            base = base + " " + random.choice(words)
    
    return base


def generate_chorus_line(hook_theme: str, language: str) -> str:
    """生成一句chorus歌词（hook）"""
    hooks = CHORUS_HOOKS.get(language, CHORUS_HOOKS["cn"])
    return random.choice(hooks)


def generate_bridge(mood: str, language: str) -> str:
    """生成桥段歌词"""
    bridge_templates_cn = [
        "可是/我/知道 /一切/都/會/過去",
        "當/黎明/來臨 /我/會/記得/此刻",
        "也許/有一天 /你會/明白/我的/心情",
        "把/所有的/眼淚 /都/交給/風",
        "在/最深的/夜裡 /我/聽到/自己的/心跳",
    ]
    bridge_templates_en = [
        "But I know that nothing lasts forever",
        "When the morning comes, we'll face the light",
        "Maybe someday you will understand",
        "All these tears will wash away the pain",
        "In the silence, I found my voice again",
    ]
    
    if language == "cn":
        return random.choice(bridge_templates_cn)
    else:
        return random.choice(bridge_templates_en)


def generate_intro_outro(duration: int) -> str:
    """生成长度合适的intro/outro"""
    if duration <= 15:
        return ""
    return ""


# ─── 主生成函数 ──────────────────────────────────────────────────
def compose_song(
    genre_key: str = "pop",
    mood: str = "happy",
    theme: str = "",
    duration_sec: int = 60,
    language: str = "cn",
    specific_subgenre: str = "",
    custom_tags: str = "",
) -> dict:
    """
    一键出歌主函数
    返回: {"lyrics": "...", "tags": "...", "info": {...}}
    """
    # 1. 确定子流派
    if specific_subgenre and specific_subgenre in GENRES.get(genre_key, {}).get("subgenres", {}):
        subgenre_name = specific_subgenre
        subgenre = GENRES[genre_key]["subgenres"][subgenre_name]
    else:
        subgenre, subgenre_name = pick_subgenre(genre_key)
    
    # 2. 计算行数
    total_lines = calculate_lines_for_duration(duration_sec)
    
    # 3. 确定结构
    structure = get_structure_for_duration_mood(duration_sec, mood, genre_key)
    
    # 4. 生成歌词
    rhyme_scheme = pick_rhyme_scheme()
    narrative = pick_narrative()
    
    lyrics_parts = []
    
    for section in structure:
        lyrics_parts.append(f"\n{section}\n")
        
        if section == "[Intro]":
            if language == "cn":
                intro_lines = [
                    f"（{mood_map_to_cn(mood)}的旋律緩緩升起）",
                    random.choice(VERSE_STARTERS["cn"]).replace("/", ""),
                ]
            else:
                intro_lines = [
                    f"(A {mood} melody slowly rises)",
                    random.choice(VERSE_STARTERS["en"]),
                ]
            # Only first line for short songs
            if duration_sec > 45:
                for l in intro_lines:
                    lyrics_parts.append(l)
            continue
            
        elif section == "[Outro]":
            if language == "cn":
                outro = f"{random.choice(['聲音漸漸遠去', '慢慢消失在夜色中', '最後一句話留在風裡', '一切都靜止了'])}"
            else:
                outro = f"{random.choice(['Fading away into the night', 'The echo lingers on', 'One last breath before the silence'])}"
            lyrics_parts.append(outro)
            if duration_sec > 45:
                lyrics_parts.append(random.choice(VERSE_STARTERS[language]).split("/")[0] + "...")
            continue
            
        elif "[Verse" in section:
            verse_num = int(section.split(" ")[1].strip("]"))
            num_lines = max(2, total_lines // 8)
            for i in range(num_lines):
                line = generate_verse_line(verse_num, theme, mood, language)
                # Remove slashes for output
                lyrics_parts.append(line.replace("/", " "))
                
        elif "[Chorus]" in section:
            num_lines = max(2, total_lines // 6)
            for i in range(num_lines):
                line = generate_chorus_line(theme, language)
                lyrics_parts.append(line.replace("/", " "))
                
        elif "[Bridge]" in section:
            lyrics_parts.append(generate_bridge(mood, language))
            
        elif "[Build Up]" in section:
            lyrics_parts.append("（節奏漸強）")
            lyrics_parts.append(random.choice(VERSE_STARTERS[language]).replace("/", " "))
            
        elif "[Drop]" in section:
            lyrics_parts.append(generate_chorus_line(theme, language).replace("/", " "))
            
        elif "[Breakdown]" in section:
            lyrics_parts.append(generate_bridge(mood, language))
    
    lyrics_text = "\n".join(lyrics_parts)
    
    # 5. 生成tags
    base_tags = []
    
    # 流派标签
    base_tags.extend(subgenre.get("typical_tags", []))
    base_tags.append(genre_key)
    
    # 情绪标签
    mood_tags = {
        "happy": ["joyful", "uplifting", "bright", "cheerful"],
        "sad": ["melancholic", "emotional", "sad", "heartbreaking"],
        "angry": ["angry", "aggressive", "intense", "fierce"],
        "nostalgic": ["nostalgic", "yearning", "wistful", "sentimental"],
        "romantic": ["romantic", "tender", "love-song", "passionate"],
        "energetic": ["energetic", "high-energy", "pumping", "dynamic"],
        "dreamy": ["dreamy", "ethereal", "atmospheric", "ambient"],
        "melancholic": ["melancholic", "bittersweet", "pensive", "sorrowful"],
        "rebellious": ["rebellious", "defiant", "rebel", "anti-establishment"],
        "peaceful": ["peaceful", "calm", "gentle", "soothing"],
    }
    base_tags.extend(mood_tags.get(mood, ["uplifting"]))
    
    # 乐器标签（从子流派取）
    instruments_tag = subgenre.get("typical_instruments", [])[:3]
    base_tags.extend([inst.split("(")[0].strip() for inst in instruments_tag])
    
    # 声乐标签
    if genre_key in VOCAL_TECHNIQUES["by_genre"]:
        techniques = VOCAL_TECHNIQUES["by_genre"][genre_key]
        base_tags.append(techniques[0]["name_en"])
    
    # 语言标签
    lang_tag_map = {"cn": "chinese-vocals", "en": "english-vocals", "jp": "japanese-vocals", "kr": "korean-vocals"}
    if language in lang_tag_map:
        base_tags.append(lang_tag_map[language])
    
    # 时长适配
    if duration_sec <= 30:
        base_tags.append("short")
    elif duration_sec <= 60:
        base_tags.append("medium-length")
    else:
        base_tags.append("long")
    
    # 自定义标签
    if custom_tags:
        base_tags.extend(custom_tags.split(","))
    
    # 去重
    seen = set()
    unique_tags = []
    for t in base_tags:
        t_clean = t.strip().lower()
        if t_clean and t_clean not in seen:
            seen.add(t_clean)
            unique_tags.append(t_clean)
    
    tags_text = ",".join(unique_tags)
    
    # 6. 信息汇总
    info = {
        "genre": genre_key,
        "subgenre": subgenre_name,
        "mood": mood,
        "theme": theme,
        "duration_sec": duration_sec,
        "language": language,
        "total_lines": total_lines,
        "structure": structure,
        "rhyme_scheme": rhyme_scheme,
        "narrative": narrative,
        "estimated_vram_gb": 6.2,
        "estimated_generation_min": max(3, duration_sec * 0.12),
    }
    
    return {"lyrics": lyrics_text, "tags": tags_text, "info": info}


def mood_map_to_cn(mood: str) -> str:
    m = {
        "happy": "欢快", "sad": "忧伤", "angry": "愤怒", "nostalgic": "懷舊",
        "romantic": "浪漫", "energetic": "充滿能量", "dreamy": "夢幻",
        "melancholic": "憂鬱", "rebellious": "叛逆", "peaceful": "寧靜",
    }
    return m.get(mood, mood)


def save_and_generate(song: dict, auto: bool = False) -> str:
    """保存到heartlib并可选自动生成"""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    lyrics_path = ASSETS_DIR / "song_crafted_lyrics.txt"
    tags_path = ASSETS_DIR / "song_crafted_tags.txt"
    output_path = ASSETS_DIR / "song_crafted.wav"
    
    with open(lyrics_path, "w", encoding="utf-8") as f:
        f.write(song["lyrics"])
    
    with open(tags_path, "w", encoding="utf-8") as f:
        f.write(song["tags"])
    
    print(f"✅ 歌词保存到: {lyrics_path}")
    print(f"✅ 标签保存到: {tags_path}")
    
    if auto:
        import subprocess
        cmd = [
            str(HEARTLIB_DIR / ".venv" / "bin" / "python"), "-c",
            f"""
import sys, torch
sys.path.insert(0, '{HEARTLIB_DIR}/src')
from heartlib import HeartMuLaGenPipeline
pipe = HeartMuLaGenPipeline.from_pretrained(
    '{HEARTLIB_DIR}/ckpt/HeartMuLa-RL-oss-3B-20260123',
    device={{'mula': torch.device('cuda'), 'codec': torch.device('cuda')}},
    dtype={{'mula': torch.bfloat16, 'codec': torch.float32}},
    version='3B',
    lazy_load=True,
)
with torch.no_grad():
    pipe(
        {{'lyrics': '{lyrics_path}', 'tags': '{tags_path}'}},
        max_audio_length_ms={song['info']['duration_sec'] * 1000},
        save_path='{output_path}',
        topk=250,
        temperature=0.8,
        cfg_scale=2.0,
    )
print('🎵 歌曲生成完成!')
"""
        ]
        print("🎬 正在调用HeartMuLa生成歌曲...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[:500])
        return str(output_path)
    
    return str(lyrics_path)


# ─── CLI ─────────────────────────────────────────────────────────
def list_genres():
    print("可用流派:")
    for gkey, gdata in GENRES.items():
        subs = list(gdata["subgenres"].keys())
        print(f"  {gkey}: {', '.join(subs[:5])}{'...' if len(subs) > 5 else ''}")


def list_moods():
    print("可用情绪: happy, sad, angry, nostalgic, romantic, energetic, dreamy, melancholic, rebellious, peaceful")
    
    print("可用主题: summer, rain, night, journey, love, friendship, freedom, rebellion, hope, loneliness, dream, nature, nostalgia, cyberpunk")
    
    print("可用语言: cn (中文), en (English), jp (日本語)")


def main():
    parser = argparse.ArgumentParser(description="🎵 一键出歌引擎")
    parser.add_argument("--genre", default="pop", help="音乐流派")
    parser.add_argument("--mood", default="happy", help="情绪")
    parser.add_argument("--theme", default="", help="主题")
    parser.add_argument("--duration", type=int, default=60, help="目标时长(秒)")
    parser.add_argument("--language", default="cn", help="语言: cn/en/jp")
    parser.add_argument("--subgenre", default="", help="指定子流派")
    parser.add_argument("--tags", default="", help="附加标签")
    parser.add_argument("--auto", action="store_true", help="自动生成(调用HeartMuLa)")
    parser.add_argument("--list-genres", action="store_true", help="列出可用流派")
    parser.add_argument("--list-moods", action="store_true", help="列出可用情绪/主题")
    parser.add_argument("--show-kb", action="store_true", help="查看知识库结构")
    
    args = parser.parse_args()
    
    if args.list_genres:
        list_genres()
        return
    
    if args.list_moods:
        list_moods()
        return
    
    if args.show_kb:
        print(f"知识库: {REF_DIR / 'songwriting_knowledge_base.json'}")
        print(f"  流派: {len(GENRES)} 个主类别")
        total_subs = sum(len(g['subgenres']) for g in GENRES.values())
        print(f"  子流派: {total_subs} 个")
        print(f"  结构模板: {len(STRUCTURES)} 个")
        print(f"  声乐技法: {sum(len(v) for v in VOCAL_TECHNIQUES['by_genre'].values())} 种")
        print(f"  民族音乐: {sum(1 for k in ETHNIC if k != 'description')} 个体系")
        return
    
    song = compose_song(
        genre_key=args.genre,
        mood=args.mood,
        theme=args.theme,
        duration_sec=args.duration,
        language=args.language,
        specific_subgenre=args.subgenre,
        custom_tags=args.tags,
    )
    
    print("=" * 60)
    print(f"🎵 【{song['info']['subgenre'].replace('_', ' ').title()}】 - {args.theme or mood_map_to_cn(args.mood)}")
    print(f"   时长: {args.duration}s | 语言: {args.language} | 情绪: {args.mood}")
    print(f"   结构: {' → '.join(song['info']['structure'])}")
    print(f"   押韵: {song['info']['rhyme_scheme']} | 叙事: {song['info']['narrative']}")
    print(f"   预计生成: ~{song['info']['estimated_generation_min']:.0f}分钟")
    print("=" * 60)
    print("\n📝 歌词:\n")
    print(song["lyrics"])
    print("\n" + "=" * 60)
    print(f"\n🏷️  标签:\n{song['tags']}")
    print("=" * 60)
    
    result = save_and_generate(song, auto=args.auto)
    print(f"\n📁 已保存: {result}")


if __name__ == "__main__":
    main()
