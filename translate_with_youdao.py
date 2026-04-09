#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用多个翻译接口自动翻译 CSV 中的单词
支持有道翻译、百度翻译
无需 API KEY，无需登录

输入文件:
    test.csv  (包含 word 列)

输出文件:
    test_translated.csv  (新增 translate 列)
"""

import argparse
import io
import requests
import pandas as pd
import time
import random
import hashlib
import sys
from pathlib import Path

YOUDAO_URL = "https://dict.youdao.com/jsonapi"
BAIDU_URL = "https://fanyi.baidu.com/sug"

def youdao_translate(word: str):
    """
    调用有道网页接口翻译
    """
    try:
        params = {
            "q": word,
            "dicts": '{"count":7,"dicts":[["ec","phrs"],["ce"],["ecs"],["new_ec"],["new_ce"],["web_search"],["baike"]]}'
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(YOUDAO_URL, params=params, headers=headers, timeout=5)
        data = r.json()

        # 优先取英译中
        if "ec" in data and "word" in data["ec"]:
            trs = data["ec"]["word"][0].get("trs", [])
            if trs:
                return trs[0]["tr"][0]["l"]["i"][0]

        # 取短语
        if "phrs" in data and "phrs" in data["phrs"]:
            phr_list = data["phrs"]["phrs"]
            if phr_list:
                return phr_list[0]["trs"][0]["tr"][0]["l"]["i"][0]

        # 兜底
        return ""
    except Exception as e:
        print(f"  有道翻译失败: {e}")
        return ""

def baidu_translate(word: str):
    """
    调用百度翻译网页接口翻译
    """
    try:
        params = {
            "kw": word
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.post(BAIDU_URL, data=params, headers=headers, timeout=5)
        data = r.json()

        # 提取翻译结果
        if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            return data["data"][0].get("v", "").split(";")[0].strip()

        return ""
    except Exception as e:
        print(f"  百度翻译失败: {e}")
        return ""

def translate_with_fallback(word: str):
    """
    使用多个翻译接口，按顺序尝试
    只有所有接口都返回空时才返回空
    """
    # 尝试有道翻译
    result = youdao_translate(word)
    if result:
        print(f"  ✓ 有道翻译: {result}")
        return result

    # 尝试百度翻译
    result = baidu_translate(word)
    if result:
        print(f"  ✓ 百度翻译: {result}")
        return result

    # 所有接口都返回空
    print(f"  ✗ 所有翻译接口均无结果")
    return ""

def main():
    # 修复 Windows 控制台编码问题
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(description="批量翻译CSV中的单词")
    parser.add_argument("input", nargs="?", default="test.csv", help="输入CSV文件（包含word列）")
    parser.add_argument("-o", "--output", help="输出CSV文件（默认为输入文件名_translated.csv）")
    args = parser.parse_args()

    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = f"{input_path.stem}_translated{input_path.suffix}"

    df = pd.read_csv(args.input)

    if "word" not in df.columns:
        print("CSV 中没有 'word' 列")
        return

    translate_list = []

    for idx, w in enumerate(df["word"]):
        print(f"[{idx+1}/{len(df)}] 翻译: {w}")

        zh = translate_with_fallback(str(w))
        translate_list.append(zh)

        # 避免请求太快被封
        time.sleep(random.uniform(0.3, 0.8))

    df["translate"] = translate_list
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n翻译完成！输出文件: {output_file}")

if __name__ == "__main__":
    main()
