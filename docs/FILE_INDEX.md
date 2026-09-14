---
title: FILE_INDEX — dsh-research-starter
type: index
status: active
version: 1.0.0
date: 2026-09-14
---

# FILE_INDEX — dsh-research-starter

## 根目录

- AGENTS.md — 研究模式总纲（Agent 入口，薄）
- README.md — 是什么
- MANUAL.md — 怎么用
- MEMORY.md — 框架自身状态
- LICENSE — Apache-2.0
- .gitignore

## presets/research/

- presets/research/preset.yml — 研究模式元数据
- presets/research/agent.cordis.yml — agent 平面组合（persona + 工具集 + skill-filesystem）
- presets/research/skills/README.md — 随包 skill 清单
- presets/research/skills/vault-protocol/SKILL.md — 加工链/状态/可追溯
- presets/research/skills/collecting/SKILL.md — 素材收录操作
- presets/research/skills/reporting/SKILL.md — 证据优先汇报格式

## governance/（新 vault 模板）

- governance/workflow.md — 11 步收录工作流
- governance/reporting.md — 汇报规范
- governance/check-consistency.py — 全局一致性检查（11 项）
- governance/vault_data.py — vault 数据模型
- governance/gen-vault-view.py — 生成 vault-view.html
- governance/templates/material.md — 素材模板
- governance/templates/insight.md — 观点模板
- governance/templates/issue.md — 议题模板

## scripts/

- scripts/install-dsh.sh — 安装 preset+skills 到 DSH
- scripts/init-vault.sh — 生成新研究库骨架

## prompts/

- prompts/study-url.md — 「帮我研究这个链接」
- prompts/progress.md — 「当前研究内容/进度」

## docs/

- docs/FILE_INDEX.md — 本文件
