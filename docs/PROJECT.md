# itolcli 调研与立项

调研日期：2026-10-26。当前状态：0.1.0 首版实现，离线流程通过；账户联调待完成。

## 结论

可行。采用官方 batch 接口，以本地注释准备和可复用导出配置作为工具的主要价值。项目独立于 iTOL，不宣称官方身份，也不重新实现其绘图引擎。

## 调研依据

- [iTOL 官方帮助](https://itol.embl.de/help.cgi#batch)：提供批量上传和导出；上传需要有效标准订阅、API key 和项目名，导出不要求订阅。应在请求之间留出数秒。
- [官方订阅说明](https://itol.embl.de/pricing.cgi)：学术及非营利个人标准订阅当前为 €6/月或 €60/年；商业用户年度标准订阅为 €120。价格可能变化，以官网为准。
- [itolapi](https://github.com/albertyw/itolapi)：已有 Python 上传/导出封装和基础命令行入口。其 README 保留了 2020 年的弃用公告；不能仅据此断言仓库完全停止维护。
- [table2itol](https://github.com/mgoeker/table2itol)：已有从表格生成注释的 R 工具，说明注释转换已有成熟先例。本项目选择 Python 标准库，减少运行依赖，并统一命令体验。
- 注释格式逐项参考官方模板：[颜色条](https://itol.embl.de/help/dataset_color_strip_template.txt)、[柱状图](https://itol.embl.de/help/dataset_simplebar_template.txt)、[热图](https://itol.embl.de/help/dataset_heatmap_template.txt)、[标签](https://itol.embl.de/help/labels_template.txt)。

## 首版范围与验收

| 工作项 | 交付 | 当前证据 |
| --- | --- | --- |
| 注释生成 | CSV/TSV → 四类 iTOL 文件 | 示例及错误输入测试通过 |
| 素材打包 | 原始树 + 有序注释 → ZIP | 顺序、内容及重复输入测试通过 |
| 官方上传 | multipart、响应解析、警告与密钥脱敏 | 模拟接口测试通过；真实账户待验收 |
| 样式导出 | 两个预设、JSON 配置及参数覆盖 | 请求与响应测试通过；成功线上导出待验收 |
| 工程交付 | 安装入口、示例、测试、文档、CI | 本地测试通过；远程 CI 以 GitHub 实际结果为准 |

所有示例均为新建演示数据，不包含用户研究数据。CLI 的成功输出是 JSON，便于脚本继续处理；错误走 stderr，并返回非零状态码。写文件默认不覆盖已有产物。

## 后续里程碑

1. 用有效订阅账户与专用测试项目，上传演示树和三类注释，验证 ID、图例、轨道顺序及 SVG/PDF 的实际显示。完成后才能宣称在线闭环可用。
2. 引入可靠树格式解析，检查重复叶名及注释 ID 与树的匹配情况；覆盖 Newick 引号、内部节点和祖先 ID。
3. 增加更多注释类型、自定义配色、整批树任务清单、跨命令限速和可恢复执行记录。
4. 增加独立的版本发布与安装分发验证；当前没有发布到 PyPI。

首版不提供删除远程树、账户管理、本地渲染或网页所有交互功能。现有参数透传也不意味着所有网页操作均可自动化。
