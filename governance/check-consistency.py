#!/usr/bin/env python3
"""vault 全局一致性检查 —— 任何触及 索引/状态/链接 的更新后必须运行。

借鉴 dba 项目 learn/_audit 模式：机器可验证的一致性，不靠人眼。
用法: python3 governance/check-consistency.py   （exit 0 = 全部通过）

检查项:
  1. INDEX 素材行 ↔ research/materials/ 实际文件（双向 + 路径存在；不含 raw/）
  2. research/materials/README.md 索引表行数 ↔ materials/ 顶层文件数
  3. 观点列三方一致：INDEX 观点列 ↔ 素材 related: ↔ 观点 source:
  4. 议题/结论引用可达（相对 .md 链接指向存在的文件）+ INDEX 议题表 ↔ research/issues/
  5. 所有 raw: 路径存在
  6. 状态健全性：有观点的素材状态必须 ≥ digested
  7. PROJECTS.md 注册表 ↔ projects/ 目录（双向）+ 项目 README 必存 + done⇒回写结论链接
  8. 全部相对链接可达（无断链；含 front matter raw: 路径）
  9. 孤儿文件检查（可链接/可索引闭环：每个文件都被某个链接或上级目录链接覆盖）
  10. 依赖声明校验：素材/观点/议题/项目 depends: 必填且合法（independent/intra/external:），矛盾即报错
  11. 旧命名漂移提示（条目/卡片/线索/综合 → 素材/观点/议题/结论；warning 不阻断）
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, oks, warns = [], [], []
def ok(m): oks.append(m)
def err(m): errors.append(m)
def warn(m): warns.append(m)

MAT = ROOT / 'research/materials'
INS = ROOT / 'research/insights'
ISS = ROOT / 'research/issues'
CON = ROOT / 'research/conclusions'

def skip_runtime(p: Path) -> bool:
    """跳过运行时/第三方源码资产：projects/*/workspace/ 与 vendored 工具源码。

    这些文件不是研究 vault 内容，不应参与断链/孤儿/旧词检查。
    """
    rel = p.relative_to(ROOT)
    parts = rel.parts
    if 'workspace' in parts:
        return True
    if 'refs/extract-wechat-messages-linux' in str(rel):
        return True
    return False

def fm(path: Path, key: str):
    text = path.read_text(encoding='utf-8')
    m = re.search(r'^---\n(.*?)\n---', text, re.S | re.M)
    if not m: return None
    for line in m.group(1).splitlines():
        mm = re.match(rf'^{key}:\s*(.*)$', line)
        if mm: return mm.group(1).strip()
    return None

# ---- 1. INDEX 素材行 ↔ research/materials/ 文件 ----
index = (ROOT / 'INDEX.md').read_text(encoding='utf-8')
rows = []
for line in index.splitlines():
    m = re.match(r'^\| (\d{4}-\d{2}-\d{2}) \| (.+?) \| (\w+) \| (\w+) \| ([^|]*)\| ([^|]*)\| \[([^\]]+)\]\(([^)]+)\) \|', line)
    if m:
        rows.append(dict(date=m.group(1), title=m.group(2), status=m.group(4),
                         cards=[c.strip() for c in m.group(5).split(',') if c.strip() and c.strip() != '—'],
                         file=m.group(8)))
item_files = {str(p.relative_to(ROOT)) for p in MAT.glob('*.md') if p.name != 'README.md'}
row_files = {r['file'] for r in rows}
if row_files == item_files:
    ok(f'1. INDEX 素材行 ({len(rows)}) ↔ materials/ 文件一致')
else:
    err(f'1. INDEX↔文件不一致: 仅INDEX={sorted(row_files - item_files)} 仅磁盘={sorted(item_files - row_files)}')

# ---- 2. materials/README.md 索引表 ↔ materials/ 顶层文件 ----
mreadme = MAT / 'README.md'
if mreadme.exists():
    sec = re.search(r'^## 索引\n(.*?)(?=^## )', mreadme.read_text(encoding='utf-8'), re.S | re.M)
    n_rows = len(re.findall(r'^\| \d{4}-\d{2}-\d{2} \|', sec.group(1), re.M)) if sec else 0
    n_files = len([f for f in MAT.glob('*.md') if f.name != 'README.md'])
    if n_rows == n_files:
        ok(f'2. materials/README 索引行 ({n_rows}) = materials 文件 ({n_files})')
    else:
        err(f'2. materials/README 索引行 ({n_rows}) ≠ materials 文件 ({n_files})')
else:
    err('2. research/materials/README.md 缺失')

# ---- 3. 观点列三方一致 ----
bad = []
for r in rows:
    item_path = ROOT / r['file']
    item_id = fm(item_path, 'id')
    related = (fm(item_path, 'related') or '').strip('[] ')
    related_slugs = {s.strip() for s in related.split(',') if s.strip()}
    for cid in r['cards']:
        matches = list(INS.glob(f'{cid}-*.md'))
        if not matches:
            bad.append(f"{r['file']}: 观点 {cid} 文件不存在"); continue
        card = matches[0]
        source = (fm(card, 'source') or '').strip('[] ')
        sources = {s.strip() for s in source.split(',') if s.strip()}
        if item_id and item_id not in sources:
            bad.append(f'{card.name}: source 缺 {item_id}')
        card_slug = card.name[:-3]
        if not any(s == card_slug or s.startswith(cid) for s in related_slugs):
            bad.append(f"{r['file']}: related 缺 {card_slug}")
if bad: err('3. 观点三方一致: ' + '; '.join(bad))
else: ok('3. INDEX 观点列 ↔ 素材 related ↔ 观点 source 三方一致')

# ---- 4. 议题引用可达 + INDEX 议题表 ----
thread_files = {p.name for p in ISS.glob('t*.md')}
idx_threads = set(re.findall(r'^\| (t\d+) \| .+? \| \w+ \| \[([^\]]+)\]\(([^)]+)\) \|', index, re.M))
for tid, fname, fpath in idx_threads:
    if not (ROOT / fpath).exists(): err(f'4. INDEX 议题 {tid}: 文件不存在 {fpath}')
if {t[0] for t in idx_threads} == {p.split('-')[0] for p in thread_files}:
    ok(f'4a. INDEX 议题表 ↔ research/issues/ 一致 ({len(thread_files)} 条)')
else:
    err(f'4a. INDEX 议题表 {sorted(t[0] for t in idx_threads)} ≠ issues 目录 {sorted(p.split("-")[0] for p in thread_files)}')
for tf in sorted(ISS.glob('t*.md')):
    text = tf.read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+\.md)\)', text):
        if link.startswith('http'): continue
        target = (tf.parent / link).resolve()
        if not target.exists(): err(f'4b. {tf.name}: 断链 {link}')

# ---- 5. raw: 路径存在 ----
missing = []
for p in MAT.glob('*.md'):
    raw = fm(p, 'raw')
    if raw and not (ROOT / raw).exists(): missing.append(f'{p.name}: {raw}')
if missing: err('5. raw 缺失: ' + '; '.join(missing))
else: ok('5. 所有 raw: 路径存在')

# ---- 6. 状态健全性 ----
ORDER = ['collected', 'read', 'digested', 'threaded', 'synthesized']
bad = []
for r in rows:
    if r['cards'] and ORDER.index(r['status']) < ORDER.index('digested'):
        bad.append(f"{r['file']}: 有卡片但状态={r['status']} (应 ≥ digested)")
if bad: err('6. 状态健全性: ' + '; '.join(bad))
else: ok('6. 状态与卡片/线索喂养关系一致')

# ---- 7. PROJECTS 注册表一致性 ----
pdir = ROOT / 'projects'
proj_dirs = {d.name for d in pdir.iterdir() if d.is_dir()}
pf = ROOT / 'PROJECTS.md'
if not pf.exists():
    err('7. PROJECTS.md 缺失')
else:
    pt = pf.read_text(encoding='utf-8')
    listed = set(re.findall(r'\]\(projects/([A-Za-z0-9_-]+)/?\)', pt))
    if listed == proj_dirs:
        ok(f'7a. PROJECTS 注册表 ({len(listed)}) ↔ projects/ 目录一致')
    else:
        err(f'7a. 注册表↔目录不一致: 仅注册表={sorted(listed - proj_dirs)} 仅目录={sorted(proj_dirs - listed)}')
    for d in sorted(pdir.iterdir()):
        if not (d / 'README.md').exists(): err(f'7b. {d.name}: 缺 README.md')
    for line in pt.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 6 and cells[0].startswith('['):
            m = re.match(r'\[([A-Za-z0-9_-]+)\]', cells[0])
            if not m: continue
            name, status = m.group(1), cells[2]
            if status == 'done':
                readme = (pdir / name / 'README.md').read_text(encoding='utf-8')
                if not re.search(r'research/conclusions/[^)\s]*\.md', readme):
                    err(f'7c. {name}: 标 done 但 README 无回写结论链接')

# ---- 8. 相对链接可达（断链检查）----
HUBS = {'README.md', 'INDEX.md', 'AGENTS.md', 'EXTERNAL.md', 'PROJECTS.md', 'progress.md'}
all_md = [p for p in ROOT.rglob('*.md') if not any(part.startswith('.') for part in p.parts) and not skip_runtime(p)]
link_re = re.compile(r'\]\(([^)]+)\)')
targets = set()
broken = []
for p in all_md:
    if '_sources' in p.parts or 'raw' in p.parts or '.refs' in p.parts: continue  # 第三方逐字来源（projects/*/_sources/、materials/raw/、.refs/）不适用链接完整性
    text = p.read_text(encoding='utf-8')
    for m in link_re.finditer(text):
        t = m.group(1).strip().split('#')[0]
        # 伪链接：含空白 / 以反引号或冒号开头（证据格式 "文件路径:行号" 记号，如 (`:275-282`)）→ 跳过
        if not t or t.startswith(('http', 'mailto:', '/', '`', ':')) or ' ' in t: continue
        target = (p.parent / t).resolve()
        targets.add(target)
        if not target.exists(): broken.append(f'{p.relative_to(ROOT)} → {m.group(1)}')
    fmsec = re.search(r'^---\n(.*?)\n---', text, re.S | re.M)
    if fmsec:
        rm = re.search(r'^raw:[ \t]*(\S+)', fmsec.group(1), re.M)
        if rm and not rm.group(1).startswith(('http', '(', '#')):
            rp = (ROOT / rm.group(1)).resolve()
            targets.add(rp)
            if not rp.exists(): broken.append(f'{p.relative_to(ROOT)} raw: {rm.group(1)}')
if broken: err('8. 断链: ' + '; '.join(broken[:10]) + (' …' if len(broken) > 10 else ''))
else: ok(f'8. 全部相对链接可达（{len(all_md)} 个 md 文件）')

# ---- 9. 孤儿文件检查（可链接/可索引闭环）----
all_files = [p for p in ROOT.rglob('*') if p.is_file() and not any(part.startswith('.') for part in p.parts) and not skip_runtime(p)]
orphans = []
for f in all_files:
    rel = str(f.relative_to(ROOT))
    if rel == '.gitignore' or rel.startswith('tmp/') or '__pycache__' in rel: continue  # tmp/ = 会话暂存区；__pycache__ = Python 缓存，均不属闭环
    if f.name in HUBS or f.name == 'README.md': continue  # hub 与目录索引豁免
    fp = f.resolve()
    covered = any(fp == t or t in fp.parents for t in targets)
    if not covered: orphans.append(rel)
if orphans: err('9. 孤儿文件(未被任何链接索引): ' + ', '.join(orphans[:15]) + (' …' if len(orphans) > 15 else ''))
else: ok(f'9. 无孤儿文件（{len(all_files)} 个文件全部可链接/可索引）')

# ---- 10. 依赖声明校验（depends: independent / intra / external:…）----
def depends_of(path: Path):
    d = fm(path, 'depends')
    return (d or '').strip().strip('"\'')
def depends_ok(d, path):
    if not d: return False, f'{path.name}: 缺 depends: 声明'
    if d == 'independent' or d == 'intra': return True, ''
    if d.startswith('external:') and len(d) > len('external:'):
        ext = d[len('external:'):].strip()
        if ext.startswith(('.', '/', '~')):  # 本地路径需存在
            cand = ROOT / ext.lstrip('./').lstrip('/')
            if not cand.exists(): return False, f'{path.name}: external 路径不存在 {ext}'
        return True, ''
    return False, f'{path.name}: depends 非法值 {d!r}'

dep_bad = []
for p in sorted(MAT.glob('*.md')):  # 素材：必须声明且合法
    if p.name == 'README.md': continue  # 目录索引，非素材
    ok_, why = depends_ok(depends_of(p), p)
    if not ok_: dep_bad.append(f'素材 {why}')
    else:
        # 有外部 url 却标 independent → 矛盾
        if depends_of(p) == 'independent' and fm(p, 'url') and not str(fm(p, 'url')).startswith('('):
            dep_bad.append(f'素材 {p.name}: 标 independent 但有 url（应 external:）')
for p in sorted(INS.glob('c*.md')):  # 观点：有 source → 必须 intra
    d = depends_of(p)
    ok_, why = depends_ok(d, p)
    if not ok_: dep_bad.append(f'观点 {why}')
    elif d == 'independent' and fm(p, 'source'):
        dep_bad.append(f'观点 {p.name}: 标 independent 但有 source（应 intra）')
for p in sorted(ISS.glob('t*.md')):  # 议题
    ok_, why = depends_ok(depends_of(p), p)
    if not ok_: dep_bad.append(f'议题 {why}')
# 项目：PROJECTS.md 依赖列非空合法
pt2 = pf.read_text(encoding='utf-8')
for line in pt2.splitlines():
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if len(cells) >= 7 and cells[0].startswith('['):
        m = re.match(r'\[([A-Za-z0-9_-]+)\]', cells[0])
        if not m: continue
        dep_val = cells[5].strip() if len(cells) > 5 else ''
        ok_, why = depends_ok(dep_val, pdir / m.group(1))
        if not ok_: dep_bad.append(f'项目 {m.group(1)}: {why}')
if dep_bad: err('10. 依赖声明: ' + '; '.join(dep_bad[:8]) + (' …' if len(dep_bad) > 8 else ''))
else: ok('10. 依赖声明全部合法（独立/库内/外部）')

# ---- 11. 旧命名漂移提示（warning 不阻断）----
OLD_TERMS = {
    '条目': '素材', '条目行': '素材行',
    '卡片': '观点', '线索': '议题', '综合': '结论',
    'items/': 'materials/', 'cards/': 'insights/', 'threads/': 'issues/', 'syntheses/': 'conclusions/',
}
for p in all_md:
    if '_sources' in p.parts or 'raw' in p.parts: continue
    text = p.read_text(encoding='utf-8')
    for old, new in OLD_TERMS.items():
        if old in text and old not in ('条目行',):
            # 避免误报：链接/目录名形式的替换已在 items/ 等 key 覆盖，且只提示正文出现
            warn(f'{p.relative_to(ROOT)}: 出现旧词「{old}」（建议改「{new}」）')

# ---- 12. vault-view.html 仪表盘不过期（与素材/观点/议题/项目/统计一致）----
try:
    from vault_data import collect, vault_hash  # noqa
    vv = ROOT / 'vault-view.html'
    if not vv.exists():
        err('12. vault-view.html 缺失（运行 python3 governance/gen-vault-view.py）')
    else:
        data = collect()
        cur = vault_hash(data)
        ht = vv.read_text(encoding='utf-8')
        m = re.search(r'数据指纹 <code>([0-9a-f]{16})</code>', ht)
        if not m:
            err('12. vault-view.html 格式异常（无数据指纹，请重新生成）')
        elif m.group(1) != cur:
            err(f'12. vault-view.html 已过期（内嵌 {m.group(1)} ≠ 当前 {cur}）——运行 python3 governance/gen-vault-view.py 后与本变更同 commit')
        else:
            ok('12. vault-view.html 仪表盘最新（数据指纹一致）')
except ImportError:
    err('12. vault_data.py 不可导入，无法校验仪表盘')

for m in oks: print('✓', m)
for m in warns: print('⚠', m)
for m in errors: print('✗', m)
sys.exit(1 if errors else 0)
