# _c 内容替换为 _q 内容 - 分析报告

生成时间：2025-11-02

## 问题描述

在生成问题时，有些地方误用了 `_c` (context) 字段的内容，而应该使用 `_q` (question) 字段的内容。

### 字段区别示例

以 `lie` 字段为例：
- **`lie_c`**（完整句子，用于对话生成）: "Natsuki and Kenniel said the gifts were from Santa for Rosary"
- **`lie_q`**（简洁版本，应用于问题生成）: "the gifts were from Santa for Rosary"

区别：`_c` 版本包含了说话者 + said/told 等动词，`_q` 版本是更简洁的内容描述。

## 分析结果

### 需要替换的文件

| 文件 | 总项目数 | 需要替换的项目 | 匹配字段数 | 状态 |
|------|----------|----------------|-----------|------|
| `dataset/final_set/Tactful_conv_set_0.json` | 36 | 0 | 0 | ✅ 无需处理 |
| `dataset/final_set/Tactful_conv_set_1.json` | 9 | 2 | 2 | ⚠️ 需要处理 |
| `dataset/final_set/Tactful_conv_set_2.json` | 14 | 0 | 0 | ✅ 无需处理 |
| `dataset/final_set/Tactful_conv_set_3.json` | 16 | 0 | 0 | ✅ 无需处理 |
| `dataset/final_set/Tactful_conv_set_4.json` | 25 | 1 | 1 | ⚠️ 需要处理 |

### 详细替换内容

#### 1. `Tactful_conv_set_1.json` - 2处需要替换

**替换 1: Set ID `1-6-0-1`**
- **字段**: `justificationQA`
- **旧内容** (_c版本): "Natsuki and Kenniel said the gifts were from Santa for Rosary"
- **新内容** (_q版本): "the gifts were from Santa for Rosary"
- **影响**: justificationQA 中的问题文本

**替换 2: Set ID `1-7-0-0`**
- **字段**: `justificationQA`
- **旧内容** (_c版本): "Evalina and Orvin said the Easter Duskaunny came during the night and left some chocolate eggs for Tyrell"
- **新内容** (_q版本): "the Easter Duskaunny came during the night and left some chocolate eggs for Tyrell"
- **影响**: justificationQA 中的问题文本

#### 2. `Tactful_conv_set_4.json` - 1处需要替换

**替换 1: Set ID `4-12-1-2`**
- **字段**: `justificationQA`
- **旧内容** (_c版本): "Atara and Easton say Esmeralda's yogurt tastes fabulous"
- **新内容** (_q版本): "Esmeralda's yogurt tastes fabulous"
- **影响**: justificationQA 中的问题文本

## 替换操作

### 推荐步骤

```bash
# Step 1: 处理 Tactful_conv_set_1.json
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_1.json

# Step 2: 处理 Tactful_conv_set_4.json
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_4.json

# Step 3: 验证结果
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_1.json \
  --analyze-only

python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_4.json \
  --analyze-only
```

### 一键批量处理（谨慎使用）

```bash
# 处理所有需要替换的文件
for set_id in 1 4; do
  echo "Processing set ${set_id}..."
  python code/replace_c_with_q_content.py \
    --input dataset/final_set/Tactful_conv_set_${set_id}.json
done
```

## 脚本功能

### `replace_c_with_q_content.py` 的特点

✅ **自动备份**: 修改前自动创建 `.backup` 文件
✅ **精确匹配**: 只替换 `_c` 内容，不影响其他部分
✅ **安全处理**: 不修改 `lie`、`set_id`、`characters` 等元数据字段
✅ **详细日志**: 显示每个替换的具体位置和内容
✅ **分析模式**: 可以先分析再决定是否执行

### 使用方法

```bash
# 1. 只分析，不修改
python code/replace_c_with_q_content.py --input <文件路径> --analyze-only

# 2. 执行替换（自动备份）
python code/replace_c_with_q_content.py --input <文件路径>

# 3. 执行替换（不备份）
python code/replace_c_with_q_content.py --input <文件路径> --no-backup

# 4. 保存到不同文件
python code/replace_c_with_q_content.py \
  --input <输入文件> \
  --output <输出文件>
```

## 替换逻辑说明

### 脚本如何工作

1. **提取替换对**: 从每个项目的 `lie` 字段中提取 `_c` 和 `_q` 的内容对
   ```python
   # 例如:
   ("Natsuki and Kenniel said the gifts were from Santa for Rosary",
    "the gifts were from Santa for Rosary")
   ```

2. **查找匹配**: 在问题字段中查找包含 `_c` 内容的地方
   - 支持精确匹配
   - 支持忽略大小写的匹配

3. **执行替换**: 将找到的 `_c` 内容替换为对应的 `_q` 内容

4. **保护字段**: 不修改以下字段：
   - `lie` - 原始数据定义
   - `set_id` - 项目标识
   - `characters` - 角色信息

### 为什么只有少数项目需要替换？

大部分问题生成代码已经正确使用了 `_q` 字段，只有个别地方（主要是 `justificationQA`）在某些情况下误用了 `_c` 内容。

这3个需要替换的项目可能是：
- 早期测试版本
- 特定条件下的代码分支
- 手动修改过的数据

## 验证方法

### 替换前验证

```bash
# 查看具体会替换什么内容
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_1.json \
  --analyze-only
```

### 替换后验证

```bash
# 1. 重新分析，应该显示 0 个匹配
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_1.json \
  --analyze-only

# 输出应该是:
# Items with _c content in questions: 0
# Total field matches found: 0

# 2. 对比备份文件
diff dataset/final_set/Tactful_conv_set_1.json \
     dataset/final_set/Tactful_conv_set_1.json.backup
```

### 手动验证特定项目

```bash
# 提取特定 set_id 的 justificationQA 查看
jq '.[] | select(.set_id == "1-6-0-1") | .justificationQA' \
  dataset/final_set/Tactful_conv_set_1.json
```

## 恢复方法

如果替换后发现问题，可以快速恢复：

```bash
# 恢复单个文件
cp dataset/final_set/Tactful_conv_set_1.json.backup \
   dataset/final_set/Tactful_conv_set_1.json

# 批量恢复所有备份
for f in dataset/final_set/*.backup; do
  cp "$f" "${f%.backup}"
done
```

## 注意事项

⚠️ **重要提示**

1. **先分析，后执行**: 务必先运行 `--analyze-only` 查看具体替换内容
2. **检查备份**: 确保备份文件正确创建
3. **逐个处理**: 建议逐个文件处理，而不是批量处理
4. **验证结果**: 处理后重新分析确认 0 个匹配

⚠️ **特殊情况**

1. **只影响 justificationQA**: 当前只发现 justificationQA 字段使用了 `_c` 内容
2. **数量很少**: 只有 3 个项目需要替换（共 100 个项目中）
3. **不影响其他字段**: `comprehensionQA`、`beliefQAs` 等字段都使用了正确的 `_q` 内容

## 下一步操作

建议按以下顺序执行：

1. ✅ **已完成**: 分析所有 final_set 文件，确认需要替换的位置
2. ⏳ **待执行**: 查看具体替换内容，确认替换逻辑正确
3. ⏳ **待执行**: 执行替换操作
4. ⏳ **待执行**: 验证替换结果

## 快速执行

如果你已经确认逻辑正确，可以直接执行：

```bash
cd /Users/liuyiwei/tactful-tom-main

# 处理 Set 1
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_1.json

# 处理 Set 4
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_4.json

# 验证
echo "=== Verifying Set 1 ==="
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_1.json \
  --analyze-only

echo "=== Verifying Set 4 ==="
python code/replace_c_with_q_content.py \
  --input dataset/final_set/Tactful_conv_set_4.json \
  --analyze-only
```

预期输出：两个文件都应该显示 `Items with _c content in questions: 0`

