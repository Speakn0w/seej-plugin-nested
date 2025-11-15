## 🛠️ 插件开发指南

### 核心原理

seej 使用**入口点（Entry Points）机制**进行插件发现和加载。这是 Python 包管理的标准方式，允许包在安装时声明它们提供的扩展点。

#### 工作流程

1. **插件安装**：pip 在安装时注册入口点
2. **seej 启动**：通过 `importlib.metadata` 发现所有 `seej.plugins` 入口点
3. **加载插件**：调用入口点函数获取渲染器
4. **注册渲染器**：将渲染器函数注册到全局注册表
5. **用户使用**：通过 `-r renderer=field` 使用插件渲染器

---

### 必须实现的组件

#### 1. 包结构

```
your-plugin-name/
├── pyproject.toml        # 必需：包配置
├── README.md             # 推荐：文档
└── seej_plugin_xxx/      # 必需：插件模块
    ├── __init__.py       # 必需：导出 get_renderers
    └── renderers.py      # 推荐：渲染器实现
```

#### 2. 入口点声明

**pyproject.toml**

```toml
[project.entry-points."seej.plugins"]
yourname = "seej_plugin_yourname:get_renderers"

#
# For example:
# [project.entry-points."seej.plugins"]
# nested = "seej_plugin_nested:get_renderers"
#
```

**关键点：**
- 入口点组名必须是 `seej.plugins`
- 入口点名称（如 `yourname`）会显示在插件列表中
- 入口点值指向 `get_renderers` 函数


#### 3. `get_renderers()` 函数（核心）

这是插件的**唯一必需接口**，必须返回渲染器字典。

**基础版本（最简）：**

```python
def get_renderers():
    """返回渲染器字典"""
    return {
        'my_renderer': my_renderer_function,
        'another': another_function,
    }
```

**完整版本（推荐）：**

```python
def get_renderers():
    """
    返回渲染器字典和描述
    
    Returns:
        tuple: (renderers_dict, descriptions_dict)
    """
    renderers = {
        'my_renderer': my_renderer_function,
        'my_alias': my_renderer_function,  # 别名指向同一函数
    }
    
    descriptions = {
        'my_renderer': '描述这个渲染器的功能',
        'my_alias': '别名描述',
    }
    
    return renderers, descriptions
```

**重要说明：**
- 如果只返回字典，描述会为空
- 如果返回元组 `(dict, dict)`，第二个字典是描述
- 别名可以通过映射到同一函数实现

#### 4. 渲染器函数签名

每个渲染器函数必须遵循以下签名：

```python
def your_renderer(v, no_rich=False, **kwargs):
    """
    渲染器函数
    
    Args:
        v: 要渲染的数据（任意类型）
        no_rich: 是否使用纯文本模式（用户按 T 切换）
        **kwargs: 其他配置（如 show_tool_call_details）
    
    Returns:
        None (直接打印输出)
    """
    if no_rich:
        # 纯文本模式实现
        print(v)
    else:
        # Rich 模式实现
        from rich.console import Console
        console = Console()
        console.print(v, style="cyan")
```

**关键点：**
- 必须接受 `no_rich` 参数并提供纯文本实现
- 必须接受 `**kwargs` 以兼容未来扩展
- 不要返回值，直接打印输出
- 异常应该被捕获并优雅处理

---

### 调试技巧

#### 1. 检查插件是否被发现

```bash
# 查看已安装的入口点
python -c "
from importlib import metadata
eps = metadata.entry_points()
for ep in eps.get('seej.plugins', []):
    print(f'{ep.name}: {ep.value}')
"
```

#### 2. 手动测试渲染器

```python
# test_renderer.py
from seej_plugin_myname import get_renderers

renderers, descriptions = get_renderers()

# 测试渲染器
test_data = {"key": "value", "nested": {"a": 1}}
renderers['custom'](test_data, no_rich=False)
```

#### 3. 查看加载错误

seej 会打印插件加载失败的错误信息：

```bash
seej data.jsonl
# 如果有错误会显示：
# ✗ Failed to load plugin 'myname': <error message>
```

#### 4. 调试模式

在插件代码中添加调试输出：

```python
def get_renderers():
    print("DEBUG: get_renderers() called")
    renderers = {...}
    print(f"DEBUG: Returning {len(renderers)} renderers")
    return renderers
```
---

### 常见问题

#### Q1: 插件安装后不显示？

**检查清单：**

```bash
# 1. 确认包已安装
pip list | grep seej-plugin

# 2. 检查入口点
python -c "
from importlib import metadata
eps = metadata.entry_points()
print(list(eps.get('seej.plugins', [])))
"

# 3. 检查 get_renderers 可调用
python -c "
from seej_plugin_myname import get_renderers
print(get_renderers())
"

# 4. 查看 seej 加载日志
seej --list-renderers
```

#### Q2: 渲染器报错 "Unknown renderer"？

**原因：** `get_renderers()` 返回的字典中没有该名称

**解决：**
```python
def get_renderers():
    return {
        'myrenderer': my_func,  # ← 确保名称正确
        'alias1': my_func,      # 别名
    }
```

#### Q3: Rich 渲染不生效？

**检查：**
- 是否正确判断 `no_rich` 参数
- 是否安装了 `rich` 库
- 用户是否按了 `T` 键切换到纯文本模式

```python
def my_renderer(v, no_rich=False, **kwargs):
    print(f"DEBUG: no_rich={no_rich}")  # 调试
    
    if no_rich:
        print("Plain text mode")
    else:
        from rich.console import Console
        console = Console()
        console.print("Rich mode", style="bold green")
```

#### Q4: 如何处理大数据？

```python
def large_data_renderer(v, no_rich=False, **kwargs):
    """处理大数据集"""
    MAX_ITEMS = 1000
    
    if isinstance(v, list) and len(v) > MAX_ITEMS:
        console.print(f"[yellow]Dataset too large ({len(v)} items)[/yellow]")
        console.print(f"[yellow]Showing first {MAX_ITEMS} items[/yellow]")
        v = v[:MAX_ITEMS]
    
    # 正常渲染
    render_data(v, no_rich)
```

#### Q5: 如何支持多种数据格式？

```python
def universal_renderer(v, no_rich=False, **kwargs):
    """通用渲染器"""
    # 检测数据类型
    if isinstance(v, str):
        try:
            # 尝试解析 JSON
            import json
            v = json.loads(v)
        except:
            pass
    
    # 根据类型渲染
    if isinstance(v, dict):
        render_dict(v, no_rich)
    elif isinstance(v, list):
        render_list(v, no_rich)
    else:
        console.print(v)
```

---

### 插件生态建议

#### 推荐的插件命名

- `seej-plugin-<功能>`
- 例如：`seej-plugin-table`, `seej-plugin-chart`, `seej-plugin-sql`

#### 推荐的渲染器命名

- 简短清晰：`table`, `chart`, `sql`
- 带前缀避免冲突：`mytable`, `mychart`
- 提供别名：`tbl` → `table`

---

### 总结

#### 必须实现的三件事：

1. **入口点声明** - 在 `pyproject.toml` 或 `setup.py` 中
2. **`get_renderers()` 函数** - 返回渲染器字典
3. **渲染器函数** - 接受 `(v, no_rich, **kwargs)` 参数

#### 最小可行插件：

```python
# seej_plugin_minimal/__init__.py
def my_renderer(v, no_rich=False, **kwargs):
    print(v)

def get_renderers():
    return {'minimal': my_renderer}
```

```toml
# pyproject.toml
[project.entry-points."seej.plugins"]
minimal = "seej_plugin_minimal:get_renderers"
```

就这么简单！🎉

---

## 许可证

MIT

## 贡献

- 欢迎提交 Issue 和 Pull Request！
- 欢迎一起开发更多 seej 插件！

## 联系方式

- Email: jason.yang98@foxmail.com