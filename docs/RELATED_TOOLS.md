# GitHub 同类工具调研

调研时间：2026-10-26。结论：已有多个相关工具，**PyiTOL 与“iTOL 美化 CLI”需求最接近**；新项目应重用上游，而不是把 CLI、配置或模板生成当成尚无人实现的能力。

| 项目 | 是否有 CLI | 主要能力 | 我们的采用方式 |
| --- | --- | --- | --- |
| [PyiTOL](https://github.com/ZengZichao/PyiTOL) | 是，`pyitol` | 多类注释模板、配置、分类分析、上传导出 | 可选依赖，`itol pyitol …` 直接调用；安装版本与 GitHub main 区分 |
| [itolapi](https://github.com/albertyw/itolapi) | 有基础脚本 | Python API、上传和导出 | 参考 API 工作流及错误处理，不重复包装多个上传后端 |
| [table2itol](https://github.com/mgoeker/table2itol) | R 脚本命令行 | 表格转注释、按列数据选择可视化 | 推荐给 R/表格用户，当前不复制代码 |
| [Gotree](https://github.com/evolbioinfo/gotree) | 是 | 树处理、本地绘图、iTOL 上传下载 | 作为树操作生态工具，当前不内置其可执行文件 |
| [itol.toolkit](https://github.com/TongZhou2017/itol.toolkit) | 主要是 R 函数 | 注释文件生成及样式处理 | 参考注释建模；当前未集成 |
| [iBiology/iTOL](https://github.com/iBiology/iTOL) | 是 | 较早的 Python API/CLI 和注释能力 | 历史方案参考，采用前需验证当前接口 |

更完整的维护时间、许可元数据和调用边界见[随包知识库](../itol_cli/knowledge/ecosystem.md)。维护信息来自 GitHub 仓库 API；不能用星数或最近推送时间替代质量验收。

## 决策

本轮直接接入 Biopython 作为可选解析库，接入 PyiTOL 1.0.3 作为可选 CLI 后端。这样可以继续跟随上游发布，同时明确哪些功能由谁实现。现阶段不把整个 PyiTOL 复制为私有分支，也不声称本项目的六类原生生成器已覆盖它的全部模板。

自己的重点是：明确输入与输出契约、树和注释 ID 校验、可复用美化设置、离线知识库、能被现有 Agent 加载的 Skill。Skill 是操作知识和工具编排指引，不是额外启动的一套自主 Agent 服务。

## 验证边界

研究读取了候选仓库 README、GitHub 元数据及 PyiTOL 的 pyproject/CLI 源文件。未对六个工具做全量性能评测，也未用真实订阅逐个验证上传接口。第三方 README 中的格式支持和模板数量，不能直接视为官方接口已验收支持。
