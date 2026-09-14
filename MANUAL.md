# MANUAL — dsh-research-starter 使用手册

## 1. 安装

```bash
scripts/install-dsh.sh                  # 装 preset → $DSH_HOME/.agent-presets/research/
scripts/install-dsh.sh --dsh-home DIR   # 指定 DSH home
scripts/install-dsh.sh --uninstall      # 卸载（保留 .bak 备份）
```

无需重启 DSH；新会话选「研究模式」即生效。

## 2. 新建研究库（init-vault.sh）

```bash
scripts/init-vault.sh ~/notes/my-vault
```

生成：AGENTS.md / progress.md / INDEX.md / inbox/ / research/{materials,insights,issues,conclusions,notes} / governance/{workflow.md,reporting.md,check-consistency.py,gen-vault-view.py,templates/}。

## 3. 日常使用

- **丢链接**：「帮我研究 https://…」→ 自动 11 步收录。
- **问进度**：「当前研究内容 / 数量」→ 分类表 + 内容层汇报（见 reporting skill）。
- **收尾**：Agent 更新 progress.md + git commit。

## 4. 常见问题

| 问题 | 答案 |
|---|---|
| preset 装哪？ | `$DSH_HOME/.agent-presets/research/` |
| skills 装哪？ | 随 preset 走（preset 层注册），不动 `~/.agents/skills` |
| 一致性检查？ | `python3 governance/check-consistency.py`（exit 0 = 通过） |
| 要重启吗？ | 不需要，新会话生效 |
| 画像/代理/路径放哪？ | 工作区 `governance/profile/`（个人化不写框架） |

## 5. 目录结构

```
presets/research/           # DSH preset（persona + 工具集 + skills/）
presets/research/skills/    # vault-protocol / collecting / reporting
governance/                 # 新 vault 模板：workflow / reporting / check-consistency.py / templates
scripts/                    # install-dsh.sh / init-vault.sh
```
