#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英文单词背诵脚本
数据源: words_translated.csv
"""

import csv
import random
import sys
from typing import List, Dict, Tuple

# === 全局配置（用户可手动修改）===
DAILY_TOTAL = 100  # 每日单词总数（如果命令行未提供，用此默认值）

# 分层阈值
HIGH_THRESHOLD = 1000  # 大于等于此值为高频
LOW_THRESHOLD = 100    # 小于此值为低频，大于等于此值为中频

# 各层抽取比例（总和应为1.0）
HIGH_RATIO = 0.1    # 高频词比例 10%
MID_RATIO = 0.4     # 中频词比例 40%
LOW_RATIO = 0.5     # 低频词比例 50%

# 可选：最小抽取数量（确保每层至少有1个词）
MIN_PER_LEVEL = 1

CSV_FILE = "words_translated.csv"


class WordItem:
    """单词数据项"""
    def __init__(self, word: str, count: int, translate: str):
        self.word = word
        self.count = count
        self.translate = translate

    def __repr__(self):
        return f"WordItem({self.word}, {self.count})"


def read_words(csv_file: str) -> List[WordItem]:
    """读取CSV文件，返回单词列表"""
    words = []

    # 尝试多种编码方式
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'cp936']

    for encoding in encodings:
        try:
            with open(csv_file, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row['word'].strip()
                    count = int(row['count'].strip())
                    translate = row['translate'].strip()
                    words.append(WordItem(word, count, translate))
            print(f"成功读取 {len(words)} 个单词（使用 {encoding} 编码）")
            return words
        except UnicodeDecodeError:
            # 如果当前编码失败，尝试下一个
            words = []  # 重置列表
            continue
        except FileNotFoundError:
            print(f"错误：找不到文件 {csv_file}")
            sys.exit(1)
        except Exception as e:
            # 如果是其他错误（非编码问题），直接报错退出
            if words or encoding == encodings[-1]:
                print(f"读取文件时出错：{e}")
                sys.exit(1)

    # 如果所有编码都失败
    print(f"错误：无法用任何支持的编码读取文件 {csv_file}")
    sys.exit(1)


def classify_words(words: List[WordItem]) -> Tuple[List[WordItem], List[WordItem], List[WordItem]]:
    """根据阈值将单词分为高、中、低三层"""
    high_freq = []  # count >= HIGH_THRESHOLD
    mid_freq = []   # LOW_THRESHOLD <= count < HIGH_THRESHOLD
    low_freq = []   # count < LOW_THRESHOLD

    for word in words:
        if word.count >= HIGH_THRESHOLD:
            high_freq.append(word)
        elif word.count >= LOW_THRESHOLD:
            mid_freq.append(word)
        else:
            low_freq.append(word)

    return high_freq, mid_freq, low_freq


def calculate_sample_sizes(total: int, high_count: int, mid_count: int, low_count: int) -> Tuple[int, int, int]:
    """计算各层应抽取数量，处理单词不足的情况"""
    # 计算理想数量
    high_num = round(total * HIGH_RATIO)
    mid_num = round(total * MID_RATIO)
    low_num = total - high_num - mid_num

    # 定义层级配置（顺序：高频 -> 中频 -> 低频）
    levels = [
        {"name": "high", "label": "高频", "count": high_count, "num": high_num, "next": "mid"},
        {"name": "mid", "label": "中频", "count": mid_count, "num": mid_num, "next": "low"},
    ]

    # 调整：将多余的配额分配到下一层
    for level in levels:
        if level["num"] > level["count"]:
            excess = level["num"] - level["count"]
            print(f"警告：{level['label']}词不足（需要{level['num']}，实际{level['count']}），调整为{level['count']}")
            level["num"] = level["count"]
            # 找到下一层并增加配额
            for next_level in levels:
                if next_level["name"] == level["next"]:
                    next_level["num"] += excess
                    break

    # 处理低频层（没有下一层）
    if low_num > low_count:
        print(f"警告：低频词不足（需要{low_num}，实际{low_count}），调整为{low_count}")
        low_num = low_count

    # 从字典中获取最终值
    high_num = levels[0]["num"]
    mid_num = levels[1]["num"]

    # 确保每层至少有MIN_PER_LEVEL个（如果有单词的话）
    if high_count > 0 and high_num < MIN_PER_LEVEL:
        high_num = min(MIN_PER_LEVEL, high_count)
    if mid_count > 0 and mid_num < MIN_PER_LEVEL:
        mid_num = min(MIN_PER_LEVEL, mid_count)
    if low_count > 0 and low_num < MIN_PER_LEVEL:
        low_num = min(MIN_PER_LEVEL, low_count)

    return high_num, mid_num, low_num


def sample_words(high_freq: List[WordItem], mid_freq: List[WordItem],
                low_freq: List[WordItem], high_num: int, mid_num: int,
                low_num: int) -> List[WordItem]:
    """从各层随机抽取指定数量的单词"""
    sampled = []

    if high_num > 0:
        sampled.extend(random.sample(high_freq, high_num))
    if mid_num > 0:
        sampled.extend(random.sample(mid_freq, mid_num))
    if low_num > 0:
        sampled.extend(random.sample(low_freq, low_num))

    # 打乱顺序
    random.shuffle(sampled)

    return sampled


def generate_options(correct_word: WordItem, all_words: List[WordItem], num_options: int = 4) -> List[str]:
    """生成选项：1个正确答案 + 3个干扰项"""
    # 获取正确答案
    correct_answer = correct_word.translate

    # 随机选择干扰项（排除正确答案）
    other_words = [w for w in all_words if w.word != correct_word.word]
    distractors = random.sample(other_words, num_options - 1)

    # 组合所有选项
    options = [correct_answer] + [w.translate for w in distractors]

    # 打乱选项顺序
    random.shuffle(options)

    return options


def run_quiz(sampled_words: List[WordItem], all_words: List[WordItem]) -> Tuple[int, int]:
    """运行测验，返回正确数和总数"""
    total = len(sampled_words)
    correct_count = 0

    for i, word_item in enumerate(sampled_words, 1):
        print(f"\n[{i}/{total}] 单词: {word_item.word}")

        # 生成选项
        options = generate_options(word_item, all_words)

        # 显示选项
        print("选项:")
        for j, option in enumerate(options, 1):
            print(f"{j}. {option}")

        # 获取用户输入
        while True:
            try:
                choice = input("你的选择: ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    break
                else:
                    print(f"请输入1到{len(options)}之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n测验已中断")
                return correct_count, i - 1

        # 检查答案
        selected_answer = options[choice_num - 1]
        if selected_answer == word_item.translate:
            print(f"✅ 正确！{word_item.translate}")
            correct_count += 1
        else:
            print(f"❌ 错误！正确答案是: {word_item.translate}")
            print(f"   你选择了: {selected_answer}")

    return correct_count, total


def main():
    """主函数"""
    # 获取命令行参数
    if len(sys.argv) > 1:
        try:
            daily_total = int(sys.argv[1])
        except ValueError:
            print("错误：参数必须是整数")
            print("用法：python review.py [每日单词数量]")
            sys.exit(1)
    else:
        daily_total = DAILY_TOTAL

    print(f"=== 单词测验开始 ===")
    print(f"每日单词数量: {daily_total}\n")

    # 读取单词
    all_words = read_words(CSV_FILE)

    # 分层
    high_freq, mid_freq, low_freq = classify_words(all_words)
    print(f"分层统计：")
    print(f"  高频词(>={HIGH_THRESHOLD}): {len(high_freq)}个")
    print(f"  中频词({LOW_THRESHOLD}-{HIGH_THRESHOLD-1}): {len(mid_freq)}个")
    print(f"  低频词(<{LOW_THRESHOLD}): {len(low_freq)}个\n")

    # 计算各层抽取数量
    high_num, mid_num, low_num = calculate_sample_sizes(
        daily_total, len(high_freq), len(mid_freq), len(low_freq)
    )

    # 显示抽取统计
    print("抽取统计：")
    high_pct = high_num / len(high_freq) * 100 if len(high_freq) > 0 else 0
    mid_pct = mid_num / len(mid_freq) * 100 if len(mid_freq) > 0 else 0
    low_pct = low_num / len(low_freq) * 100 if len(low_freq) > 0 else 0
    print(f"  高频词: {high_num}/{len(high_freq)}个 ({high_pct:.1f}%)")
    print(f"  中频词: {mid_num}/{len(mid_freq)}个 ({mid_pct:.1f}%)")
    print(f"  低频词: {low_num}/{len(low_freq)}个 ({low_pct:.1f}%)")

    # 抽取单词
    sampled_words = sample_words(high_freq, mid_freq, low_freq, high_num, mid_num, low_num)

    if len(sampled_words) < daily_total:
        print(f"\n警告：总单词数不足，实际抽取 {len(sampled_words)} 个")

    print()

    # 开始测验
    correct_count, total_answered = run_quiz(sampled_words, all_words)

    # 显示统计
    print("\n" + "="*50)
    print("=== 测验结束 ===")
    print(f"总计: {total_answered} 题")
    print(f"正确: {correct_count} 题")
    print(f"错误: {total_answered - correct_count} 题")
    if total_answered > 0:
        accuracy = correct_count / total_answered * 100
        print(f"正确率: {accuracy:.1f}%")
    print("="*50)


if __name__ == "__main__":
    main()
