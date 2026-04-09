#!/usr/bin/env python3
"""
PDF 全文词频统计工具
依赖: PyPDF2
Windows + Python 3.12/3.13 可用
"""

import sys
import re
import csv
from collections import Counter
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("请先安装 PyPDF2: pip install PyPDF2")
    sys.exit(1)

# 可选英文停用词
STOPWORDS = {
    "the","and","or","but","is","are","was","were","be","been","to","of",
    "in","on","for","from","with","this","that","these","those","as","an",
    "a","by","can","could","may","might","must","shall","should","will",
    "would","it","its","at","we","you","they","their","our","has","have",
    "had","do","does","did","not","so","than","then","there","here","etc",
    "such","using","used","very","also","based","into",
    "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
    "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
    "dw","apb","no","en","ahb","th","scl","de","ip","sclk","src","your","err","hs","mhz","wr","co","rd","mi",
    "'b","kb","ic","if","tx","rx","ch","re","id","ss","up","ws","fs","er","io","'r","ki","ir","xr","od","ga",
    "tn","fh","gl","lr","ii","hr",
    
    "xffffffffffffffff",
}

def extract_text(pdf_path):
    """提取 PDF 文本"""
    reader = PdfReader(str(pdf_path))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return " ".join(texts)

def count_words(text, min_length=1, remove_stopwords=True):
    """统计词频"""
    words = re.findall(r"[A-Za-z']+", text.lower())
    if remove_stopwords:
        words = [w for w in words if w not in STOPWORDS and len(w) >= min_length]
    return Counter(words)

def process_pdf(pdf_path, min_length=1, remove_stopwords=True):
    print(f"Processing: {pdf_path}")
    text = extract_text(pdf_path)
    counter = count_words(text, min_length, remove_stopwords)
    return counter

def merge_counters(counters):
    total = Counter()
    for c in counters:
        total.update(c)
    return total

def save_csv(counter, outfile):
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        for word, count in counter.most_common():
            writer.writerow([word, count])
    print(f"Saved CSV: {outfile}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PDF 全文词频统计")
    parser.add_argument("pdfs", nargs="+", help="PDF 文件路径")
    parser.add_argument("--min-length", type=int, default=1, help="忽略短词")
    parser.add_argument("--no-stopwords", action="store_true", help="不过滤英文停用词")
    parser.add_argument("--out", default="", help="输出 CSV 文件路径")
    parser.add_argument("--top", type=int, default=50, help="打印前 N 高频词")
    args = parser.parse_args()

    counters = []
    for pdf in args.pdfs:
        pdf_path = Path(pdf)
        if not pdf_path.is_file():
            print(f"文件不存在: {pdf}")
            continue
        counters.append(process_pdf(pdf_path, args.min_length, not args.no_stopwords))

    if not counters:
        print("没有处理任何 PDF。")
        sys.exit(1)

    total_counter = merge_counters(counters)

    # 打印前 N 高频词
    print(f"\nTop {args.top} words:")
    for word, count in total_counter.most_common(args.top):
        print(f"{word}: {count}")

    # 保存 CSV
    if args.out:
        save_csv(total_counter, args.out)

if __name__ == "__main__":
    main()
