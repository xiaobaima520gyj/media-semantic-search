# Media Dataset Retrieval System - 使用指南

## 项目简介

这是一个语义搜索系统，用于通过自然语言描述来检索图片和视频文件。系统使用 AI 嵌入模型将文本转换为向量，通过语义相似度匹配来找到最相关的媒体文件。

### 语言支持

- **默认模型**：英文优化（all-MiniLM-L6-v2）
- **多语言模型**：支持中文、英文及其他 50+ 语言（paraphrase-multilingual-MiniLM-L12-v2）

## 快速开始

### 1. 安装

```bash
# 克隆项目后安装依赖（包含 CLI）
pip install -e ".[cli]"

# 安装服务器依赖（用于 API 服务器模式）
pip install -e ".[server]"

# 或安装所有依赖
pip install -e ".[cli,server]"

# 或仅安装核心依赖
pip install -e .
```

### 2. 准备数据集

创建 `data/dataset.json` 文件，格式如下：

```json
{
  "version": "1.0",
  "items": [
    {
      "id": "img_001",
      "path": "sample/images/cat.jpg",
      "description": "A sleeping orange tabby cat curled up on a sunny windowsill",
      "media_type": "image",
      "format": "jpg",
      "categories": ["animals", "pets", "cats"],
      "tags": ["sleeping", "orange", "windowsill"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**字段说明：**
| 字段 | 必需 | 说明 |
|------|------|------|
| `id` | 是 | 唯一标识符 |
| `path` | 是 | 相对文件路径 |
| `description` | 是 | 媒体描述（语义搜索基于此字段） |
| `media_type` | 是 | `image` 或 `video` |
| `format` | 是 | 文件格式（如 jpg, png, mp4） |
| `categories` | 否 | 分类标签列表 |
| `tags` | 否 | 关键词标签列表 |

### 3. 执行搜索

```bash
# 基本搜索（返回前5条结果）
media-search search "cats on windowsill"

# 指定返回结果数量
media-search search "sunset" --top 10

# JSON 格式输出
media-search search "sunset" --format json

# 简单格式输出
media-search search "beach" --format simple
```

### 4. 快速启动（推荐）

项目提供了快捷脚本，方便快速启动：

| 脚本 | 用途 |
|------|------|
| `run_server.bat` | 启动 API 服务器（模型常驻内存） |
| `run_test.bat` | 启动聊天式测试客户端 |

**使用流程：**

1. 双击 `run_server.bat` 启动 API 服务器（保持运行）
2. 双击 `run_test.bat` 打开聊天式搜索界面
3. 输入查询内容进行搜索

★ Insight ─────────────────────────────────────
- 服务器模式模型只加载一次，后续搜索非常快
- 聊天客户端支持中文输入，交互更友好
- 适合频繁搜索的场景
─────────────────────────────────────────────────

## 命令详解

### search - 语义搜索

```bash
media-search search <QUERY> [OPTIONS]
```

**选项：**
| 选项 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--top` | `-n` | 5 | 返回结果数量 |
| `--format` | `-f` | table | 输出格式：table/json/simple |
| `--dataset` | `-d` | data/dataset.json | 数据集文件路径 |
| `--index` | `-i` | None | 预建索引路径（加速加载） |

**示例：**
```bash
# 表格输出（默认）
media-search search "technology innovation"

# JSON 输出（适合程序处理）
media-search search "nature landscape" --format json --top 20

# 使用预建索引加速
media-search search "cat" --index data/index.pkl
```

### build-index - 构建索引

预建索引可以加速搜索启动时间：

```bash
media-search build-index <DATASET> [OPTIONS]
```

**选项：**
| 选项 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--output` | `-o` | data/index.pkl | 索引输出路径 |
| `--model` | `-m` | all-MiniLM-L6-v2 | 嵌入模型名称 |

**示例：**
```bash
# 构建索引
media-search build-index data/dataset.json -o data/index.pkl

# 后续搜索使用索引
media-search search "sunset" --index data/index.pkl
```

### server - API 服务器

启动 FastAPI 服务器，模型常驻内存，后续搜索非常快：

```bash
media-search server [OPTIONS]
```

**选项：**
| 选项 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--dataset` | `-d` | data/dataset.json | 数据集文件路径 |
| `--index` | `-i` | None | 预建索引路径 |
| `--model` | `-m` | all-MiniLM-L6-v2 | 嵌入模型名称 |
| `--port` | `-p` | 8000 | 服务器端口 |
| `--host` | | 127.0.0.1 | 服务器地址 |

**示例：**
```bash
# 启动服务器（中文模式）
media-search server -d data/dataset.json -i data/index_zh.pkl -m paraphrase-multilingual-MiniLM-L12-v2 -p 8000
```

★ Insight ─────────────────────────────────────
- 服务器启动后模型只加载一次，后续搜索只需几十毫秒
- 适合高频搜索场景
- 可通过 HTTP API 集成到其他应用
─────────────────────────────────────────────────

## API 服务器

服务器启动后，提供以下 HTTP 接口：

### 接口列表

| 接口 | 方法 | 描述 |
|------|------|------|
| `/search` | POST | 语义搜索 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | API 文档（Swagger UI） |

### 使用示例

**curl：**
```bash
# 搜索
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "我想找个猫", "top_k": 5}'

# 健康检查
curl http://localhost:8000/health
```

**Python：**
```python
import requests

# 搜索
response = requests.post(
    "http://localhost:8000/search",
    json={"query": "我想找个猫", "top_k": 5}
)
results = response.json()

# 查看结果
for r in results["results"]:
    print(f"{r['score']:.4f} - {r['path']}")
```

### 交互式文档

访问 `http://localhost:8000/docs` 可以查看和测试所有 API 接口。

★ Insight ─────────────────────────────────────
- Swagger UI 提供在线测试功能
- 无需编写代码即可调试 API
- 支持生成客户端代码
─────────────────────────────────────────────────

## Python API 使用

### 基本用法

```python
from src.api import MediaSearch

# 初始化搜索（加载数据集）
search = MediaSearch("data/dataset.json")

# 执行搜索
results = search.query("cats", top_k=5)

# 遍历结果
for result in results:
    print(f"路径: {result.path}")
    print(f"相似度: {result.score:.4f}")
    print(f"描述: {result.description}")
    print(f"类型: {result.media_type}/{result.format}")
    print("---")
```

### 使用预建索引

```python
from src.api import MediaSearch

# 使用预建索引初始化（更快）
search = MediaSearch("data/dataset.json", index_path="data/index.pkl")

# 执行搜索
results = search.query("sunset beach", top_k=10)
```

### 手动构建索引

```python
from src.models.media import MediaDataset
from src.search import SemanticSearch

# 加载数据集
media_dataset = MediaDataset.load("data/dataset.json")

# 构建索引
search = SemanticSearch()
search.build_index(media_dataset)

# 保存索引
search.save_index("data/index.pkl")
```

## 中文搜索

系统支持中文语义检索，需要使用多语言模型：

### CLI 方式

```bash
# 使用多语言模型构建索引
media-search build-index data/dataset.json -o data/index_zh.pkl --model paraphrase-multilingual-MiniLM-L12-v2

# 中文搜索
media-search search "熊猫" --index data/index_zh.pkl
```

### Python API 方式

```python
from src.models.media import MediaDataset
from src.search import SemanticSearch, MULTILINGUAL_MODEL

# 加载数据集
media_dataset = MediaDataset.load("data/dataset.json")

# 使用多语言模型
search = SemanticSearch(model_name=MULTILINGUAL_MODEL)
search.build_index(media_dataset)

# 中文搜索
results = search.search("熊猫")

# 混合中英文搜索
results = search.search("可爱的猫咪和狗狗")
```

### 多语言混合检索

支持中英文混合查询：

```python
results = search.search("可爱的小猫 cute cat")
```

★ Insight ─────────────────────────────────────
- 多语言模型与默认模型向量维度相同(384维)，可直接替换
- 切换模型后需要重新构建索引
- 建议为不同语言分别建立专用索引
─────────────────────────────────────────────────

## 输出格式示例

### Table 格式（默认）

```
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┬─────────┬────────────────────────────────────────┓
┃  Score  ┃       Path         ┃  Type   ┃            Description                 ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇────────────────────────────────────────┩
│ 0.8542  │ sample/images/cat… │ image/… │ A sleeping orange tabby cat curled…    │
│ 0.7231  │ sample/videos/…   │ video/… │ A cat video in a sunny room           │
└─────────┴────────────────────┴─────────┴────────────────────────────────────────┘
```

### JSON 格式

```json
[
  {
    "id": "img_001",
    "path": "sample/images/cat.jpg",
    "description": "A sleeping orange tabby cat...",
    "media_type": "image",
    "format": "jpg",
    "categories": ["animals", "pets"],
    "tags": ["sleeping", "orange"],
    "score": 0.8542
  }
]
```

### Simple 格式

```
0.8542  sample/images/cat.jpg
0.7231  sample/videos/cat_video.mp4
```

## 常见问题

### Q: 搜索结果不准确？

A: 检查数据集的 `description` 字段，确保描述足够详细和准确。语义搜索依赖描述文本的质量。

### Q: 首次搜索很慢？

A: 使用 `build-index` 命令预建索引，后续搜索会快很多。

### Q: 支持哪些文件格式？

A: 系统不直接处理文件，只存储路径。支持的格式取决于你的实际媒体文件，数据库中记录 `media_type` 和 `format` 即可。

### Q: 如何添加新的媒体条目？

A: 直接编辑 `dataset.json`，添加新的 item 对象即可。无需重新构建索引。

### Q: 如何让搜索更快？

A: 有两种方式：
1. 使用预建索引：`media-search search "query" --index data/index.pkl`
2. 启动 API 服务器：双击 `run_server.bat`，模型常驻内存，后续搜索只需几十毫秒

### Q: 为什么每次 CLI 搜索都要加载模型？

A: CLI 每次执行都是新进程，进程结束后模型内存释放。解决方法：
1. 使用 API 服务器模式（推荐）
2. 或确保模型已下载到本地缓存（第二次运行会更快）

## 项目结构

```
rag_demo1/
├── src/
│   ├── api/              # API 接口
│   │   └── media_search.py
│   ├── cli/              # 命令行工具
│   │   └── main.py
│   ├── models/           # 数据模型
│   │   └── media.py
│   ├── search/           # 搜索引擎
│   │   ├── embedder.py
│   │   ├── index.py
│   │   └── semantic_search.py
│   ├── server/           # API 服务器
│   │   └── main.py
│   └── validators/       # 数据验证
│       └── dataset_validator.py
├── data/
│   ├── dataset.json      # 示例数据集
│   ├── index.pkl        # 预建索引
│   └── sample/           # 示例媒体文件
│       ├── images/
│       └── videos/
├── tests/                # 测试用例
├── run_server.bat       # 快速启动服务器（双击运行）
└── run_test.bat         # 快速启动测试客户端（双击运行）
```

## 性能说明

- **数据集大小**：推荐 < 10,000 条目
- **CLI 首次搜索**：约 3-5 秒（加载模型）
- **CLI 后续搜索**：< 1 秒（使用缓存模型）
- **API 服务器搜索**：< 0.1 秒（模型常驻内存）
- **使用索引**：首次搜索 < 1 秒
