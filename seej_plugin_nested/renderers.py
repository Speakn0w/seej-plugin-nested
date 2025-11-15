"""Nested structure renderers for complex JSON data."""

import json
from typing import Any, Dict, List
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax

console = Console()


def truncate_value(value: Any, max_length: int = 100) -> str:
    """截断长值"""
    value_str = str(value)
    if len(value_str) > max_length:
        return value_str[: max_length - 3] + "..."
    return value_str


def get_type_color(value: Any) -> str:
    """根据类型返回颜色"""
    if isinstance(value, str):
        return "green"
    elif isinstance(value, (int, float)):
        return "cyan"
    elif isinstance(value, bool):
        return "magenta"
    elif value is None:
        return "dim"
    elif isinstance(value, dict):
        return "yellow"
    elif isinstance(value, list):
        return "blue"
    else:
        return "white"


def build_tree_recursive(tree: Tree, data: Any, max_depth: int = 10, current_depth: int = 0):
    """递归构建树结构"""
    if current_depth >= max_depth:
        tree.add("[dim]... (max depth reached)[/dim]")
        return

    if isinstance(data, dict):
        if not data:
            tree.add("[dim](empty dict)[/dim]")
            return

        for key, value in data.items():
            color = get_type_color(value)

            if isinstance(value, dict):
                branch = tree.add(f"[bold {color}]{key}[/bold {color}] [dim](dict, {len(value)} keys)[/dim]")
                build_tree_recursive(branch, value, max_depth, current_depth + 1)
            elif isinstance(value, list):
                branch = tree.add(f"[bold {color}]{key}[/bold {color}] [dim](list, {len(value)} items)[/dim]")
                build_tree_recursive(branch, value, max_depth, current_depth + 1)
            else:
                value_str = truncate_value(value, max_length=80)
                tree.add(f"[{color}]{key}[/{color}]: [{color}]{value_str}[/{color}]")

    elif isinstance(data, list):
        if not data:
            tree.add("[dim](empty list)[/dim]")
            return

        for idx, item in enumerate(data):
            color = get_type_color(item)

            if isinstance(item, dict):
                branch = tree.add(f"[bold {color}][{idx}][/bold {color}] [dim](dict, {len(item)} keys)[/dim]")
                build_tree_recursive(branch, item, max_depth, current_depth + 1)
            elif isinstance(item, list):
                branch = tree.add(f"[bold {color}][{idx}][/bold {color}] [dim](list, {len(item)} items)[/dim]")
                build_tree_recursive(branch, item, max_depth, current_depth + 1)
            else:
                value_str = truncate_value(item, max_length=80)
                tree.add(f"[{color}][{idx}][/{color}]: [{color}]{value_str}[/{color}]")
    else:
        color = get_type_color(data)
        value_str = truncate_value(data)
        tree.add(f"[{color}]{value_str}[/{color}]")


def nested_dict_tree(v: Dict, no_rich: bool = False, max_depth: int = 10, **kwargs):
    """
    树形渲染嵌套字典

    适合：复杂的 JSON 对象，配置文件
    """
    if no_rich:
        print(json.dumps(v, indent=2, ensure_ascii=False))
        return

    tree = Tree(f"[bold magenta]📦 Nested Dict[/bold magenta] [dim]({len(v)} keys)[/dim]", guide_style="dim")
    build_tree_recursive(tree, v, max_depth=max_depth)
    console.print(tree)


def nested_list_table(v: List[Dict], no_rich: bool = False, **kwargs):
    """
    表格渲染字典列表

    适合：统一结构的记录列表，类似 CSV
    """

    if not v:
        console.print("[dim](empty list)[/dim]")
        return

    if no_rich:
        for idx, item in enumerate(v):
            print(f"=== [{idx}] ===")
            print(json.dumps(item, indent=2, ensure_ascii=False))
        return

    # 检查是否所有元素都是字典
    if not all(isinstance(item, dict) for item in v):
        # 回退到树形渲染
        tree = Tree(f"[bold blue]📋 List[/bold blue] [dim]({len(v)} items)[/dim]", guide_style="dim")
        build_tree_recursive(tree, v, max_depth=5)
        console.print(tree)
        return

    # 收集所有键
    all_keys = set()
    for item in v:
        all_keys.update(item.keys())
    all_keys = sorted(all_keys)

    # 如果键太多，使用树形渲染
    if len(all_keys) > 10:
        tree = Tree(f"[bold blue]📋 List of Dicts[/bold blue] [dim]({len(v)} items, {len(all_keys)} keys)[/dim]", guide_style="dim")
        build_tree_recursive(tree, v, max_depth=3)
        console.print(tree)
        return

    # 创建表格
    table = Table(title=f"List of Dicts ({len(v)} items)", show_header=True, header_style="bold cyan")

    # 添加索引列
    table.add_column("#", style="dim", width=4)

    # 添加数据列
    for key in all_keys:
        table.add_column(key, overflow="fold")

    # 填充数据
    for idx, item in enumerate(v):
        row = [str(idx)]
        for key in all_keys:
            value = item.get(key)
            if value is None:
                row.append(Text("-", style="dim"))
            else:
                value_str = truncate_value(value, max_length=50)
                color = get_type_color(value)
                row.append(Text(value_str, style=color))
        table.add_row(*row)

    console.print(table)


def nested_auto(v: Any, no_rich: bool = False, max_depth: int = 10, **kwargs):
    """
    自动选择最佳渲染方式

    - Dict → 树形
    - List[Dict] → 表格或树形
    - 其他 → JSON 格式
    """
    if isinstance(v, dict):
        nested_dict_tree(v, no_rich=no_rich, max_depth=max_depth, **kwargs)
    elif isinstance(v, list):
        nested_list_table(v, no_rich=no_rich, **kwargs)
    else:
        if no_rich:
            print(json.dumps(v, indent=2, ensure_ascii=False, default=str))
        else:
            syntax = Syntax(json.dumps(v, indent=2, ensure_ascii=False, default=str), "json", theme="monokai", line_numbers=False)
            console.print(syntax)


def nested_json(v: Any, no_rich: bool = False, **kwargs):
    """
    JSON 格式渲染（带语法高亮）
    """
    json_str = json.dumps(v, indent=2, ensure_ascii=False, default=str)

    if no_rich:
        print(json_str)
    else:
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="JSON", border_style="blue"))


def nested_compact(v: Any, no_rich: bool = False, **kwargs):
    """
    紧凑型渲染（单行）
    """
    if no_rich:
        print(json.dumps(v, ensure_ascii=False, default=str))
    else:
        json_str = json.dumps(v, ensure_ascii=False, default=str)
        if len(json_str) > 200:
            json_str = json_str[:197] + "..."
        console.print(Text(json_str, style="cyan"))


# 导出渲染器映射（支持两种格式）
def get_renderers():
    """
    返回插件提供的渲染器

    Returns:
        可以返回以下两种格式之一:
        1. 简单格式: {name: function}
        2. 扩展格式: ({name: function}, {name: description})
    """
    renderers = {
        "nested": nested_auto,
        "nested_dict": nested_dict_tree,
        "nested_list": nested_list_table,
        "nested_table": nested_list_table,  # 别名
        "nested_tree": nested_dict_tree,  # 别名
        "json": nested_json,
        "compact": nested_compact,
    }

    descriptions = {
        "nested": "Auto-detect and render nested structures (tree/table)",
        "nested_dict": "Tree view for nested dictionaries",
        "nested_list": "Table view for list of dictionaries",
        "nested_tree": "Alias for nested_dict",
        "nested_table": "Alias for nested_list",
        "json": "Syntax-highlighted JSON format",
        "compact": "Compact single-line representation",
    }

    return renderers, descriptions
