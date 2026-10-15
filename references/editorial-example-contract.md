# 编辑式示例适配契约

此契约只属于可选的小型参考骨架，不取代 skill 的通用实体/观测设计。
生产报告可以用任意现有格式和分析策略，按需要重写适配层。

输入为一个 JSON 对象：

| 字段 | 含义 |
|---|---|
| `title`, `summary` | 报告任务与核心说明；不是统计规则 |
| `eyebrow`, `snapshot`, `scope` | 可选栏目、快照与范围说明 |
| `synthetic` | 合成数据必须为 true；页面显式显示演示标记 |
| `rows` | 任意字段的记录；`idField` 指向唯一非空标识 |
| `columns` | `{field,label,numeric?}`，控制明细与导出列 |
| `facet` | `{field,label}`，单一分类维度，分类名称直接来自记录 |
| `drilldown` | 可选 `{field,label}`，上层分类下的具体项目；点击第二组柱图收紧明细 |
| `comparison` | 可为 null；否则包含 baseline/candidate 映射、direction、unit、deltaUnit、precision、pairingNote |
| `baseline`, `candidate` | comparison 内的 `{field,label,statusField?,validStatus?}` |
| `direction` | `higher` 或 `lower`，不得由字段名称或正负值推测 |
| `theme` | 可选语义颜色键：background/surface/text/muted/line/accent/soft；值仅接受十六进制颜色 |
| `detailsField`, `sourcesField` | 可选的证据说明文本和资料链接数组字段 |

`pairingNote` 应解释为什么这两列能逐项比较；有同一个行 ID 不自动证明可比。
构建器检查显式契约，无法认证数据的真实配对语义。条件不兼容时不使用此配对指标；
可设置 comparison=null，或回到通用分析层做分别汇总/明确映射。

只有双方是有限数值且各自状态有效时计算差值。higher 用 candidate−baseline，lower 用
baseline−candidate；正值表示当前配置指标改善。均值仅使用共同有效集合，显示 N。
单位与差值单位分开：百分比的相减可用“个百分点”，延迟可用“天”。未声明比较时隐藏相关
列与摘要，分类分布/明细仍能使用。骨架不提供补值、加权、ANY/ALL、多对象选择或统计显著性。
这些需求按原 skill 设计，不应靠扩充此小示例推断。

每条 row 可有说明和资料链接。仅允许 http/https 资料链接；其他内容按纯文本渲染，不能执行。
构建时安全序列化数据，运行时用 textContent 呈现原文。CSV 保留数值零和负数；可能作为公式
执行的非数值文本加前缀，且始终正确引用。视图 JSON 包含筛选、摘要和分析口径，供恢复/追查，
不会自动联网。模板未实现状态导入或任意复杂条件，不声称完整支持这些能力。

主题只改变语义颜色；密度、字体、行宽等通过 CSS tokens 或现有框架配置。
添加新领域时优先改配置/字段映射，保持原始数据、失败分类和统计定义。
