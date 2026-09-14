#!/usr/bin/env python3
"""生成根目录 vault-view.html。

用法：python3 governance/gen-vault-view.py
任何素材/观点/议题/结论/项目更新后，与更新同一 commit 重生成。
"""
import html, json
from datetime import datetime
from pathlib import Path

from vault_data import collect, vault_hash, ROOT


def esc(value):
    return html.escape(str(value or ''), quote=True)


def render(data, digest, generated):
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>研究库 · Vault Dashboard</title>
<style>
:root{--bg:#0b1020;--panel:#121a2b;--panel2:#18243a;--line:#263653;--text:#e8eef8;--muted:#8da0bb;--blue:#65a7ff;--purple:#bd8aff;--orange:#ffad66;--green:#57d68d;--cyan:#55d6d2;--red:#ff7b8b;--shadow:0 18px 50px #02061180}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 12% -10%,#1f3960 0,#0b1020 36%),var(--bg);color:var(--text);font:14px/1.65 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.shell{max-width:1480px;margin:auto;padding:28px 28px 70px}.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;padding:22px 0 30px}.eyebrow{color:var(--blue);font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:700}.hero h1{font-size:clamp(30px,5vw,56px);line-height:1.05;margin:8px 0 10px;letter-spacing:-.04em}.hero p{color:var(--muted);margin:0;max-width:720px}.stamp{color:var(--muted);font-size:12px;text-align:right}.live{display:inline-flex;align-items:center;gap:7px;color:var(--green);font-weight:700}.live:before{content:"";width:8px;height:8px;background:var(--green);border-radius:50%;box-shadow:0 0 14px var(--green)}.chain{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:22px}.node{background:linear-gradient(145deg,#182742,#111a2d);border:1px solid var(--line);border-radius:16px;padding:18px;position:relative;box-shadow:var(--shadow)}.node:not(:last-child):after{content:"→";position:absolute;right:-18px;top:34px;color:var(--muted);font-size:22px;z-index:2}.node .label{font-size:12px;color:var(--muted)}.node strong{display:block;font-size:30px;line-height:1.2;margin:5px 0;color:var(--accent)}.node small{color:var(--muted)}.node.material{--accent:var(--blue)}.node.insight{--accent:var(--purple)}.node.issue{--accent:var(--orange)}.node.conclusion{--accent:var(--green)}.branch{display:flex;gap:12px;margin:0 0 25px}.branch-card{flex:1;padding:13px 16px;border:1px solid var(--line);border-radius:13px;background:#10192a;color:var(--muted)}.branch-card b{color:var(--cyan);margin-right:10px}.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:25px}.stat{padding:16px 18px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(145deg,#141f34,#101728)}.stat .num{font-size:27px;font-weight:800}.stat .caption{color:var(--muted);font-size:12px}.section{margin:32px 0}.section-head{display:flex;align-items:end;justify-content:space-between;gap:16px;margin-bottom:12px}.section h2{font-size:21px;margin:0;letter-spacing:-.02em}.section-note{color:var(--muted);font-size:12px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{border:1px solid var(--line);border-radius:16px;background:#10182a;overflow:hidden}.panel-title{padding:15px 17px;border-bottom:1px solid var(--line);font-weight:750}.bars{padding:15px 17px}.barline{display:grid;grid-template-columns:110px 1fr 30px;align-items:center;gap:10px;margin:10px 0}.barline label{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--muted);font-size:12px}.bar{height:8px;border-radius:99px;background:#26344e;overflow:hidden}.bar i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,var(--blue),var(--purple))}.barline b{font-size:12px;text-align:right}.table-wrap{overflow:auto}.toolbar{display:flex;gap:10px;margin-bottom:12px}.search{width:min(420px,100%);background:#10182a;border:1px solid var(--line);border-radius:10px;padding:10px 13px;color:var(--text);outline:none}.search:focus{border-color:var(--blue);box-shadow:0 0 0 3px #65a7ff20}table{border-collapse:collapse;width:100%;min-width:820px}th,td{text-align:left;padding:12px 14px;border-bottom:1px solid #21304a;vertical-align:top}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;background:#131e32;position:sticky;top:0}td{font-size:13px}tr:hover td{background:#18243a}.muted{color:var(--muted)}.pill{display:inline-block;padding:2px 8px;border-radius:999px;background:#253450;color:#cfe0f8;font-size:11px;margin:1px 3px 1px 0}.pill.blue{background:#173a68;color:#8fc4ff}.pill.purple{background:#382467;color:#d5b8ff}.pill.orange{background:#55341d;color:#ffc28d}.pill.green{background:#16432f;color:#8af0b5}.pill.cyan{background:#154749;color:#82ece7}.empty{padding:24px;color:var(--muted);text-align:center}.footer{margin-top:45px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;display:flex;justify-content:space-between;gap:20px}@media(max-width:900px){.chain{grid-template-columns:repeat(2,1fr)}.node:not(:last-child):after{display:none}.stats{grid-template-columns:repeat(3,1fr)}}@media(max-width:620px){.shell{padding:18px 14px 50px}.hero{display:block}.stamp{text-align:left;margin-top:15px}.chain,.grid2{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.branch{display:block}.branch-card{margin:8px 0}}
</style>
</head>
<body>
<div class="shell">
<header class="hero"><div><div class="eyebrow">Personal Research Vault · v3</div><h1>研究库全景</h1><p>素材 → 观点 → 议题 → 结论。一个把外部资料变成可复用理解的研究仪表盘。</p></div><div class="stamp"><div class="live">LIVE SNAPSHOT</div><div>生成于 __GENERATED__</div><div>数据指纹 <code>__HASH__</code></div></div></header>
<section class="chain" id="chain"></section>
<div class="branch"><div class="branch-card"><b>PROJECTS</b><span>交付旁支 · 工程产出与研究回写</span></div><div class="branch-card"><b>GOVERNANCE</b><span>治理旁支 · 规则、流程、依赖与闭环</span></div></div>
<section class="stats" id="stats"></section>
<section class="section"><div class="grid2"><div class="panel"><div class="panel-title">主题分布</div><div class="bars" id="topics"></div></div><div class="panel"><div class="panel-title">依赖关系</div><div class="bars" id="depends"></div></div></div></section>
<section class="section"><div class="section-head"><div><h2>素材 · Materials</h2><div class="section-note">外部资料与本地原件的结构化入口</div></div><input class="search" data-target="materials-table" placeholder="搜索标题、主题、状态、依赖…"></div><div class="panel table-wrap"><table id="materials-table"><thead><tr><th>日期</th><th>标题</th><th>主题</th><th>状态</th><th>依赖</th><th>入口</th></tr></thead><tbody></tbody></table></div></section>
<section class="section"><div class="section-head"><div><h2>观点 · Insights</h2><div class="section-note">可复用的原子主张</div></div><input class="search" data-target="insights-table" placeholder="搜索观点、来源、依赖…"></div><div class="panel table-wrap"><table id="insights-table"><thead><tr><th>编号</th><th>主张</th><th>来源素材</th><th>依赖</th><th>入口</th></tr></thead><tbody></tbody></table></div></section>
<section class="section"><div class="section-head"><div><h2>议题 · Issues</h2><div class="section-note">持续演化的问题与待验证项</div></div><input class="search" data-target="issues-table" placeholder="搜索议题、状态、待验证…"></div><div class="panel table-wrap"><table id="issues-table"><thead><tr><th>编号</th><th>问题</th><th>状态</th><th>待验证</th><th>入口</th></tr></thead><tbody></tbody></table></div></section>
<section class="section"><div class="section-head"><div><h2>项目 · Projects</h2><div class="section-note">交付状态、外部依赖与下一步</div></div><input class="search" data-target="projects-table" placeholder="搜索项目、依赖、下一步…"></div><div class="panel table-wrap"><table id="projects-table"><thead><tr><th>项目</th><th>定位</th><th>状态</th><th>依赖</th><th>回写</th><th>下一步</th></tr></thead><tbody></tbody></table></div></section>
<footer class="footer"><span>根目录 <code>/home/wwt/Downloads/aigc/proj/research</code></span><span>更新内容后运行：<code>python3 governance/gen-vault-view.py</code></span></footer>
</div>
<script>
const DATA=__DATA__;
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(file,label)=>file?`<a href="${esc(file)}">${esc(label||file)}</a>`:'—';
const dep=v=>`<span class="pill ${v==='intra'?'purple':v==='independent'?'green':'cyan'}">${esc(v||'—')}</span>`;
const status=v=>`<span class="pill ${v==='synthesized'||v==='done'?'green':v==='threaded'||v==='active'?'orange':v==='digested'?'purple':'blue'}">${esc(v||'—')}</span>`;
function rows(id, items, fn){document.querySelector(`#${id} tbody`).innerHTML=items.length?items.map(fn).join(''):`<tr><td colspan="8" class="empty">暂无数据</td></tr>`}
function bars(id, arr){const max=Math.max(1,...arr.map(x=>x[1]));document.getElementById(id).innerHTML=arr.length?arr.map(([k,n])=>`<div class="barline"><label title="${esc(k)}">${esc(k)}</label><div class="bar"><i style="width:${n/max*100}%"></i></div><b>${n}</b></div>`).join(''):`<div class="empty">暂无数据</div>`}
function render(){const s=DATA.stats;document.getElementById('chain').innerHTML=[['material','素材','materials','var(--blue)'],['insight','观点','insights','var(--purple)'],['issue','议题','issues','var(--orange)'],['conclusion','结论','conclusions','var(--green)']].map(x=>`<div class="node ${x[0]}"><div class="label">${x[1]}</div><strong>${s[x[2]]}</strong><small>主链节点</small></div>`).join('');document.getElementById('stats').innerHTML=[['素材',s.materials,'blue'],['观点',s.insights,'purple'],['议题',s.issues,'orange'],['结论',s.conclusions,'green'],['项目',s.projects,'cyan']].map(x=>`<div class="stat"><div class="num" style="color:var(--${x[2]})">${x[1]}</div><div class="caption">${x[0]}</div></div>`).join('');bars('topics',s.topics);bars('depends',s.depends);rows('materials-table',DATA.materials,m=>`<tr><td>${esc(m.date)}</td><td><b>${esc(m.title)}</b><br><span class="muted">${esc(m.id)}</span></td><td><span class="pill blue">${esc(m.topic)}</span></td><td>${status(m.status)}</td><td>${dep(m.depends)}</td><td>${link(m.file,'打开素材')}</td></tr>`);rows('insights-table',DATA.insights,m=>`<tr><td><b>${esc(m.id)}</b></td><td>${esc(m.title)}</td><td class="muted">${esc(m.source)}</td><td>${dep(m.depends)}</td><td>${link(m.file,'打开观点')}</td></tr>`);rows('issues-table',DATA.issues,m=>`<tr><td><b>${esc(m.id)}</b></td><td>${esc(m.title)}</td><td>${status(m.status)}</td><td class="muted">${esc(m.open_issue||'暂无摘录')}</td><td>${link(m.file,'打开议题')}</td></tr>`);rows('projects-table',DATA.projects,m=>`<tr><td><a href="projects/${esc(m.name)}/"><b>${esc(m.name)}</b></a></td><td>${esc(m.pos)}</td><td>${status(m.status)}</td><td>${dep(m.depends)}</td><td>${esc(m.writeback)}</td><td>${esc(m.next)}</td></tr>`)}
document.querySelectorAll('.search').forEach(input=>input.addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll(`#${e.target.dataset.target} tbody tr`).forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none')}));render();
</script>
</body>
</html>
'''.replace('__DATA__', payload).replace('__GENERATED__', esc(generated)).replace('__HASH__', digest)


def main():
    data = collect()
    digest = vault_hash(data)
    generated = datetime.now().astimezone().isoformat(timespec='seconds')
    data['generated'] = generated
    out = ROOT / 'vault-view.html'
    out.write_text(render(data, digest, generated), encoding='utf-8')
    print(f'generated {out} (hash={digest}, materials={data["stats"]["materials"]}, insights={data["stats"]["insights"]}, issues={data["stats"]["issues"]}, projects={data["stats"]["projects"]})')


if __name__ == '__main__':
    main()