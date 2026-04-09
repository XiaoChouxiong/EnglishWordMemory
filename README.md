# 英文单词记忆工具

从技术文档 PDF 中提取高频词汇，自动翻译，并提供互动式单词背诵测验。

## 功能特点

- **PDF 词频提取**：从多个 PDF 文档中提取英文单词并统计词频
- **自动翻译**：批量调用有道/百度翻译 API 获取中文释义
- **分层背诵**：根据词频分为高/中/低三层，智能抽取单词进行测验
- **互动测验**：四选一选择题模式，实时反馈正确率

## 目录结构

```
EnglishWordMemory/
├── PDFS/                      # PDF 文档存放目录
│   ├── DW_apb_gpio_databook.pdf
│   ├── DW_apb_i2c_databook.pdf
│   └── ...
├── pdf_freq.py               # PDF 词频提取工具
├── translate_with_youdao.py  # 单词翻译工具
├── review.py                 # 单词背诵测验
└── README.md                 # 本文档
```

## 环境要求

- Python 3.12+
- 依赖库：
  ```bash
  pip install PyPDF2 requests pandas
  ```

## 使用方法

### 1. PDF 词频提取

从 PDF 文档中提取单词并统计出现频率：

```bash
python pdf_freq.py <PDF文件>... [选项]

# 选项:
#   --top N         打印前 N 个高频词（默认: 50）
#   --out FILE      输出 CSV 文件路径
#   --min-length N  忽略短于 N 个字符的单词（默认: 1）
#   --no-stopwords  不过滤英文停用词
```

**示例：**
```bash
# 处理单个 PDF
python pdf_freq.py PDFS/DW_apb_gpio_databook.pdf --out words_count.csv

# 处理多个 PDF
python pdf_freq.py PDFS/*.pdf --top 100 --out words_count.csv
```

**输出格式：** `word,count`
```csv
word,count
gpio,1316
register,451
designware,402
```

### 2. 单词翻译

批量翻译 CSV 中的单词：

```bash
python translate_with_youdao.py [输入文件] [-o 输出文件]

# 参数:
#   输入文件    CSV 文件路径（默认: test.csv）
#   -o, --output  输出文件路径（默认: {输入文件名}_translated.csv）
```

**示例：**
```bash
# 使用默认输入
python translate_with_youdao.py

# 指定输入输出
python translate_with_youdao.py words_count.csv -o words_translated.csv
```

**注意：** 每个单词间隔 0.3-0.8 秒，避免 API 限流

### 3. 单词背诵测验

基于词频分层的互动测验：

```bash
python review.py [每日单词数量]

# 参数:
#   每日单词数量  每次测验抽取的单词总数（默认: 100）
```

**示例：**
```bash
# 每天背诵 50 个单词
python review.py 50
```

**测验流程：**
1. 系统根据词频分层抽取单词
2. 显示英文单词和四个中文选项
3. 选择答案后立即显示正确/错误
4. 测验结束显示正确率统计

## 完整工作流程

```bash
# 步骤 1: 从 PDF 提取词频
python pdf_freq.py PDFS/*.pdf --top 5000 --out words_count.csv

# 步骤 2: 翻译单词
python translate_with_youdao.py words_count.csv -o words_translated.csv

# 步骤 3: 开始背诵测验
python review.py 50
```

## 配置说明

### review.py 配置

可在脚本开头修改以下参数：

```python
DAILY_TOTAL = 100          # 默认每日单词数量
HIGH_THRESHOLD = 1000      # 高频词阈值（>= 此值）
LOW_THRESHOLD = 100        # 低频词阈值（< 此值）

# 分层抽取比例
HIGH_RATIO = 0.1           # 高频词 10%
MID_RATIO = 0.4            # 中频词 40%
LOW_RATIO = 0.5            # 低频词 50%
```

### pdf_freq.py 配置

停用词列表已内置，可编辑 `STOPWORDS` 变量自定义。

## 文件说明

| 文件 | 说明 |
|------|------|
| `words_count.csv` | 词频统计结果（word, count） |
| `words_translated.csv` | 翻译结果（word, count, translate） |
| `test_translated.csv` | 测试输出文件 |

## 注意事项

1. **翻译 API 限流**：已内置随机延时（0.3-0.8 秒），但仍建议避免频繁调用
2. **控制台编码**：Windows 下已自动处理 UTF-8 编码问题
3. **单词分层**：高频词重点复习，低频词快速记忆
4. **Git Bash 用户**：使用 `/d/Path/to/python.exe` 格式调用 Python

## 许可证

MIT
