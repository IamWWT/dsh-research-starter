# dsh-research-starter — 研究模式框架（DSH）

> 证据优先的个人研究库（vault）Agent 框架。与 [dsh-engineering-starter](../dsh-engineering-starter/) 同族：DSH 专属 preset + 随包 skills + 一键安装，通用化、无机器路径。

## 是什么

一句话需求（丢链接 / 一句话）→ 研究模式 Agent 按「素材→观点→议题→结论」加工链收录进你的研究库，每一步诚实落盘、证据可追溯、索引与状态同步。

## 快速开始

```bash
# 1. 安装 preset + 随包 skills（幂等；不写 ~/.agents/skills，preset 层 shadow）
scripts/install-dsh.sh                      # 默认 $DSH_HOME=~/.dsh-dev
scripts/install-dsh.sh --dsh-home <DIR>     # 指定 DSH home

# 2. 新建研究库（可选）
scripts/init-vault.sh <目录>                # 生成独立 vault：AGENTS/governance/check-consistency.py/模板

# 3. DSH 新会话 → 选「研究模式」→ workspace 指向 vault → 丢链接或一句话
```

## 设计要点

- **通用化**：persona 薄（入口+纪律），重内容在随包 skills 渐进加载；画像/路径/凭证归工作区。
- **证据优先**：一手来源、可追溯证据、事实/推断分开、假设显式标注。
- **机器校验**：`governance/check-consistency.py`（11 项检查：索引↔文件、依赖声明、状态晋升、断链、孤儿文件…）exit 0 才算过。
- **preset 层 skills**：随 preset 走、shadow 全局同名技能、模式外不影响；`~/.agents/skills` 原样保留。

## 与工程模式的关系

研究模式负责「知识沉淀」，工程模式负责「工程交付」：调研报告放 `projects/`（工程侧），研究观点走收录流程进 `research/`（研究侧）。两者可组合使用。

## License

Apache-2.0
