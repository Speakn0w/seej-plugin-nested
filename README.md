# [插件] seej-plugin-nested

嵌套结构渲染插件 - 为 seej 提供复杂 JSON 数据的优美可视化。

## 安装

```bash
# 暂未发布，pip 不可用
pip install seej-plugin-nested

# 请先 clone 本仓库并手动安装
git clone http://this-repo-name
pip install cloned-folder/
```

## 功能渲染器

此插件提供以下渲染器：

- **`nested`** - 自动检测并选择最佳渲染方式（字典用树形，列表用表格）
- **`nested_dict` / `nested_tree`** - 树形视图展示嵌套字典
- **`nested_list` / `nested_table`** - 表格视图展示字典列表
- **`json`** - 带语法高亮和行号的 JSON 格式
- **`compact`** - 单行紧凑表示

## 使用方法

```bash
# 自动渲染
seej data.jsonl -r nested=config,metadata

# 强制使用树形视图
seej data.jsonl -r nested_tree=config

# 强制使用表格视图
seej data.jsonl -r nested_table=records

# JSON 格式（带语法高亮）
seej data.jsonl -r json=raw_data

# 紧凑视图
seej data.jsonl -r compact=summary
```

## 效果示例

### 树形视图 (nested_dict)

```
Nested Dict (3 keys)
├── name: "Example Project"
├── version: 1.2
└── config (dict, 4 keys)
    ├── env: "production"
    ├── debug: false
    ├── timeout: 30
    └── servers (list, 2 items)
        ├── [0] (dict, 2 keys)
        │   ├── host: "server1.example.com"
        │   └── port: 8080
        └── [1] (dict, 2 keys)
            ├── host: "server2.example.com"
            └── port: 8080
```

### 表格视图 (nested_list)

```
┏━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ #  ┃ name    ┃ age   ┃ city   ┃
┡━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ 0  │ Alice   │ 30    │ NYC    │
│ 1  │ Bob     │ 25    │ LA     │
│ 2  │ Charlie │ 35    │ SF     │
└────┴─────────┴───────┴────────┘
```
