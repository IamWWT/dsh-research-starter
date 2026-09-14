#!/usr/bin/env python3
"""vault 数据层：从 INDEX / materials / insights / issues / PROJECTS 提取全部状态。

用于：
- governance/gen-vault-view.py 生成根目录 vault-view.html（实时仪表盘）
- governance/check-consistency.py 第 12 项校验仪表盘是否过期（hash 对比）

任何收录/变更后运行生成器，与变更同一 commit（AGENTS §6）。
"""
import re, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fm(path: Path, key: str):
    """读取 front matter 单值。"""
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None
    m = re.search(r'^---\n(.*?)\n---', text, re.S | re.M)
    if not m:
        return None
    for line in m.group(1).splitlines():
        mm = re.match(rf'^{key}:\s*(.*)$', line)
        if mm:
            return mm.group(1).strip()
    return None


def _pick_issues(path: Path):
    """议题正文「未解/待验证」节的首条内容（展示用）。"""
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None
    m = re.search(r'##\s*未解\s*/\s*待验证(.*?)(\n## |\Z)', text, re.S)
    if not m:
        return None
    for line in m.group(1).splitlines():
        s = line.strip().lstrip('-').strip()
        if s:
            return s[:140]
    return None


def _depends_class(depends: str) -> str:
    """归一化依赖类别：independent / intra / external。"""
    d = (depends or '').strip()
    if d == 'independent':
        return 'independent'
    if d == 'intra':
        return 'intra'
    if d.startswith('external'):
        return 'external'
    return '—'


def collect() -> dict:
    """提取全部数据。返回 dict，供生成器渲染与检查器比对。"""
    materials = []
    for p in sorted((ROOT / 'research/materials').glob('*.md')):
        if p.name == 'README.md':
            continue
        depends = fm(p, 'depends') or ''
        materials.append({
            'file': str(p.relative_to(ROOT)),
            'id': fm(p, 'id') or p.stem,
            'title': fm(p, 'title') or p.stem,
            'date': fm(p, 'date_added') or '',
            'type': fm(p, 'type') or '',
            'status': fm(p, 'status') or '',
            'topic': fm(p, 'topic') or '',
            'depends': depends,
            'depends_class': _depends_class(depends),
        })

    insights = []
    for p in sorted((ROOT / 'research/insights').glob('c*.md')):
        depends = fm(p, 'depends') or ''
        insights.append({
            'file': str(p.relative_to(ROOT)),
            'id': fm(p, 'id') or p.stem,
            'title': fm(p, 'title') or p.stem,
            'source': (fm(p, 'source') or '')[:220],
            'depends': depends,
            'depends_class': _depends_class(depends),
        })

    issues = []
    for p in sorted((ROOT / 'research/issues').glob('t*.md')):
        depends = fm(p, 'depends') or ''
        issues.append({
            'file': str(p.relative_to(ROOT)),
            'id': fm(p, 'id') or p.stem,
            'title': fm(p, 'title') or p.stem,
            'status': fm(p, 'status') or '',
            'open_issue': _pick_issues(p) or '',
            'depends': depends,
            'depends_class': _depends_class(depends),
        })

    conclusions = []
    for p in sorted((ROOT / 'research/conclusions').glob('*.md')):
        conclusions.append({
            'file': str(p.relative_to(ROOT)),
            'id': fm(p, 'id') or p.stem,
            'title': fm(p, 'title') or p.stem,
        })

    projects = []
    pf = ROOT / 'PROJECTS.md'
    if pf.exists():
        for line in pf.read_text(encoding='utf-8').splitlines():
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 7 or not cells[0].startswith('['):
                continue
            m = re.match(r'\[([A-Za-z0-9_-]+)\]', cells[0])
            if not m:
                continue
            projects.append({
                'name': m.group(1),
                'pos': cells[1],
                'status': cells[2],
                'related': cells[3],
                'writeback': cells[4],
                'depends': cells[5],
                'depends_class': _depends_class(cells[5]),
                'next': cells[6][:220],
            })

    all_content = materials + insights + issues

    def count_by(items, key):
        out = {}
        for it in items:
            v = it.get(key) or '—'
            out[v] = out.get(v, 0) + 1
        return list(sorted(out.items(), key=lambda x: -x[1]))

    stats = {
        'materials': len(materials),
        'insights': len(insights),
        'issues': len(issues),
        'conclusions': len(conclusions),
        'projects': len(projects),
        'content_total': len(all_content),
        'topics': count_by(materials, 'topic'),
        'mat_status': count_by(materials, 'status'),
        'proj_status': count_by(projects, 'status'),
        'depends': count_by(all_content, 'depends_class'),
    }

    return {
        'generated': None,
        'stats': stats,
        'materials': materials,
        'insights': insights,
        'issues': issues,
        'conclusions': conclusions,
        'projects': projects,
    }


def vault_hash(data: dict) -> str:
    """数据 JSON 稳定 hash（排序键），供检查器比对仪表盘是否过期。"""
    body = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]