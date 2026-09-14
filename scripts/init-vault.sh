#!/usr/bin/env bash
# ============================================================================
# init-vault.sh — 生成一个新的研究库（vault）骨架
# 用法: scripts/init-vault.sh <目标目录> [--name "名称"]
# 生成: AGENTS.md / progress.md / INDEX.md / inbox/ / research/ 五区 /
#       governance/{workflow.md,reporting.md,check-consistency.py,gen-vault-view.py,templates/}
# 自包含：生成后任何 Agent 打开即用（不依赖框架仓库在场）。
# ============================================================================
set -euo pipefail

TARGET="${1:-}"
[ -n "$TARGET" ] || { echo "用法: scripts/init-vault.sh <目标目录> [--name 名称]" >&2; exit 1; }
NAME="$(basename "$(realpath -m "$TARGET")")"
[ "$#" -ge 3 ] && [ "$2" = "--name" ] && NAME="$3"

[ -d "$TARGET" ] && [ -n "$(ls -A "$TARGET")" ] && { echo "错误: 目标目录非空（init-vault 只接受空目录）" >&2; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$TARGET"

# ---- 骨架目录 ----
mkdir -p "$TARGET"/{inbox,research/{materials/raw,insights,issues,conclusions,notes},projects,archive,governance/profile,tmp}

# ---- governance 模板 ----
cp -r "$ROOT"/governance/{check-consistency.py,vault_data.py,gen-vault-view.py,workflow.md,reporting.md} "$TARGET/governance/" 2>/dev/null || true
mkdir -p "$TARGET/governance/templates"
for t in material insight issue; do
  [ -f "$ROOT/governance/templates/$t.md" ] && cp "$ROOT/governance/templates/$t.md" "$TARGET/governance/templates/"
done

# ---- AGENTS.md（研究 vault 版）----
cat > "$TARGET/AGENTS.md" <<AGEOF
# AGENTS.md — 研究库（$NAME）协作契约

> 对任何在本仓库工作的 AI 会话的约束性约定。本文件是 agent 行为唯一真源；governance/ 是详细流程。

## 1. 会话开场 / 收尾
1. 开场先读 progress.md（当前焦点 / 进行中表 / 下一步）。
2. 任何触及索引/状态/链接的更新后：跑 \`python3 governance/check-consistency.py\`（exit 0 = 通过），结果随汇报给出。
3. 收尾：更新 progress.md + git commit（一个逻辑改动一个 commit，中文信息）。

## 2. 加工链（来自 dsh-research-starter）
素材 material（它说了什么）→ 观点 insight（提炼出什么）→ 议题 issue（怎么一步步想）→ 结论 conclusion（最终认为什么）。
素材状态 collected→read→digested→threaded→synthesized，只升不降；晋升必须与索引同步。

## 3. 存放位置
| 内容 | 放哪 |
|---|---|
| 任何新内容 | inbox/（先收再整） |
| 素材/观点/议题/结论 | research/{materials,insights,issues,conclusions}/ |
| 工作交付物/项目 | projects/<name>/ |
| 个人笔记 | research/notes/ |
| 画像/规则 | governance/profile/（个人化内容） |

## 4. Front matter 最低要求
素材/观点/议题/结论必填：id / title / type / date / topic / tags / status / related / depends（independent|intra|external:<path-or-url>）。
AGEOF

# ---- progress.md / INDEX.md 占位 ----
cat > "$TARGET/progress.md" <<PEOF
# progress — $NAME

> 最近变更 + 进行中表。每次会话结束更新。

## 最近变更
- （暂无）

## 进行中
| 事项 | 状态 | 下一步 |
|---|---|---|
| （暂无） | — | — |
PEOF
cat > "$TARGET/INDEX.md" <<IEOF
# INDEX — $NAME

| 素材 | 状态 | 观点 | 议题 | 依赖 |
|---|---|---|---|---|
| （空） | — | — | — | — |
IEOF

# ---- 一致性检查依赖的配套文件 ----
cat > "$TARGET/PROJECTS.md" <<PJEOF
# PROJECTS — $NAME

| 项目 | 依赖 | 状态 | 备注 |
|---|---|---|---|
| （暂无） | — | — | — |
PJEOF
cat > "$TARGET/EXTERNAL.md" <<EUF
# EXTERNAL — 外部参考

（外部链接/参考资料速记，不参与加工链）
EUF
for zone in materials insights issues conclusions notes; do
  cat > "$TARGET/research/$zone/README.md" <<ZEOF
# $zone/

（$zone 目录：$(case $zone in materials) echo 素材——外部资料，命名 YYYYMMDD-slug.md;; insights) echo 观点——原子主张 cNNNN-slug.md;; issues) echo 议题——演化的问题 tNN-slug.md;; conclusions) echo 结论——跨域熔炼 YYYYMMDD-slug.md;; notes) echo 个人笔记——主观自由体;; esac)）
ZEOF
done
cat > "$TARGET/research/materials/README.md" <<ZEOF
# materials/ — 素材索引

| 素材 | 状态 | 观点 | 议题 | 依赖 |
|---|---|---|---|---|
| （空） | — | — | — | — |
ZEOF
cat > "$TARGET/archive/README.md" <<ARF
# archive/ — 归档

（仅当不再被任何活跃议题/结论引用时归档；索引见本目录）
ARF

# ---- 生成初始 vault-view（一致性检查 12 项需要）----
if [ -f "$TARGET/governance/gen-vault-view.py" ]; then
  ( cd "$TARGET" && python3 governance/gen-vault-view.py >/dev/null 2>&1 || true )
fi

echo ""
echo "✅ 研究库初始化完成: $TARGET"
echo "  - workspace 指向该目录，DSH 选「研究模式」即可开始收录。"
echo "  - 协议见 AGENTS.md；一致性检查: python3 governance/check-consistency.py"
