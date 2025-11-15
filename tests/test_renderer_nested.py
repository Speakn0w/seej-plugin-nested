from seej_plugin_nested import get_renderers

renderers, descriptions = get_renderers()

for k in renderers:
    print(f"[Renderer: {k}]")
    print(f"\t  Fn: {renderers[k]}")
    print(f"\tDesc: {descriptions[k]}")
    print("-" * 20)

test_data = {"key": "value", "nested": {"a": 1}}
test_data["a"] = test_data  # self-ref for endless recursion

renderers["nested"](test_data, no_rich=False)
# 📦 Nested Dict (3 keys)
# ├── key: value
# ├── nested (dict, 1 keys)
# │   └── a: 1
# └── a (dict, 3 keys)
#     ├── key: value
#     ├── nested (dict, 1 keys)
#     │   └── a: 1
#     └── a (dict, 3 keys)
#         ├── key: value
#         ├── nested (dict, 1 keys)
#         │   └── a: 1
#         └── a (dict, 3 keys)
#             ├── key: value
#             ├── nested (dict, 1 keys)
#             │   └── a: 1
#             └── a (dict, 3 keys)
#                 ├── key: value
#                 ├── nested (dict, 1 keys)
#                 │   └── a: 1
#                 └── a (dict, 3 keys)
#                     ├── key: value
#                     ├── nested (dict, 1 keys)
#                     │   └── a: 1
#                     └── a (dict, 3 keys)
#                         ├── key: value
#                         ├── nested (dict, 1 keys)
#                         │   └── a: 1
#                         └── a (dict, 3 keys)
#                             ├── key: value
#                             ├── nested (dict, 1 keys)
#                             │   └── a: 1
#                             └── a (dict, 3 keys)
#                                 ├── key: value
#                                 ├── nested (dict, 1 keys)
#                                 │   └── a: 1
#                                 └── a (dict, 3 keys)
#                                     ├── key: value
#                                     ├── nested (dict, 1 keys)
#                                     │   └── ... (max depth reached)
#                                     └── a (dict, 3 keys)
#                                         └── ... (max depth reached)
