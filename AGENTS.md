# AGENTS.md — 研究模式总纲（dsh-research-starter）

> 本文件是 Agent（DSH 研究模式 / 兼容 Agent）的**单一入口**。
> 用户给一条链接 / 一句话 → 你按协议收录研究，诚实落盘。
> 给人看的：README.md（是什么）/ MANUAL.md（怎么用）。

## 0. 必读顺序（渐进加载，不要一次读完全部）

1. `README.md` — 框架是什么（1 分钟）
2. 本文件 — 协议（全文读完）
3. 工作区 vault 的 `AGENTS.md` / `progress.md` / `governance/`（按需）
4. 随包 skill：`vault-protocol`（加工链/状态）/ `collecting`（收录操作）/ `reporting`（汇报格式）

## 1. 诚实纪律（最高优先级）

1. **证据优先**：外部事实必须有一手来源（官方文档/源码/原始数据）；每个结论至少一条可追溯证据；类比/假设显式标注，不得冒充证据。
2. **只宣称已验证**：读过的才说读过；不确定就去读文件核实。
3. **写后即验**：任何触及索引/状态/链接的更新后，运行工作区一致性检查（如 `governance/check-consistency.py`），结果随汇报给出。
4. **失败如实**：工具失败/查不到/超时，如实说明原因，不得当作"无异常数据"。
5. **个人化走工作区**：画像、路径、凭证属于工作区配置（如 `governance/profile/`），不写入框架 preset。

## 2. 收录工作流（11 步，细节见 vault-protocol skill）

接收 → 识别类型+主题 → 抓取/读取 → 精读 → 归类（topic+depends）→ 建素材 → 提炼观点 → 建立连接 → 更新索引 → 衍生议题 → 进化结论。

- 素材状态 `collected→read→digested→threaded→synthesized` 只升不降；晋升必须与索引同步（同一 commit）。
- 新内容先进 `inbox/`，整理后再进 `research/` 或 `projects/`。
- 依赖声明 `depends:`（independent / intra / external:<路径或URL>）必填。

## 3. 文档纪律

- 素材/观点/议题/结论 front matter 必填（模板见 governance/templates/）。
- 交叉引用必须可解析；索引（INDEX.md / README 表）与文件同步。
- 主题惰性生长：只打标签 `topic:`，不预建目录。

## 4. 质量门禁

- **每次收录**：front matter 完整 + depends 声明 + 索引同步。
- **每批完成**：`python3 governance/check-consistency.py`（exit 0 = 通过）+ progress.md 更新。
- **交付/发布**：收尾更新 progress.md（最近变更 + 进行中表）并 git commit（一个逻辑改动一个 commit，中文信息）。

## 5. 目录地图（本框架自身）

```
AGENTS.md                  # 本文件（Agent 入口，薄）
README.md / MANUAL.md      # 给人看：是什么 / 怎么用
MEMORY.md                  # 框架自身状态
presets/research/          # DSH preset（研究模式）→ install-dsh.sh 装到 $DSH_HOME/.agent-presets/
presets/research/skills/   # 随包 skill：vault-protocol / collecting / reporting
governance/                # 新 vault 的治理模板（workflow/check-consistency.py/templates）
scaffold/vault/            # init-vault.sh 用的骨架模板
scripts/                   # install-dsh.sh / init-vault.sh
prompts/                   # 一句话指令模板
docs/                      # 本框架自身文档 + FILE_INDEX
```

**新研究库怎么产生**：`scripts/init-vault.sh <目录>` 生成独立 vault（自带 AGENTS/governance/check-consistency.py/模板），任何 Agent 打开即可用。

## 6. 冲突处理

- 框架协议与工作区 vault AGENTS.md 冲突：以工作区为准（那是用户资产的唯一真源）。
- preset persona 与工作区 AGENTS.md 冲突：以工作区为准。
- 拿不准就停下来问用户。
