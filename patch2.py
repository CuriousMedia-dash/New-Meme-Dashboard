#!/usr/bin/env python3
"""
Patches report.html:
1. Category tabs show table layout (like Top 10) instead of card grid
2. Number format changed to international commas (300,000)
Run in your Meme Dashboard folder:  python patch_report.py
"""
import sys, os

path = 'report.html'
if not os.path.exists(path):
    print(f"Error: {path} not found. Run this in your project folder.")
    sys.exit(1)

with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

with open(path + '.report.bak', 'w', encoding='utf-8') as f:
    f.write(code)
print(f"Backup saved to {path}.report.bak")

# ═══════════════════════════════════════════
# PATCH 1: Change fmt() to international comma format
# ═══════════════════════════════════════════
old_fmt = "function fmt(n){ if(!n||isNaN(n))return'0'; if(n>=1e6)return(n/1e6).toFixed(2)+'M'; if(n>=1e3)return(n/1e3).toFixed(1)+'K'; return Number(n).toLocaleString('en-IN'); }"
new_fmt = "function fmt(n){ if(!n||isNaN(n))return'0'; return Number(n).toLocaleString('en-US'); }"
code = code.replace(old_fmt, new_fmt, 1)

# ═══════════════════════════════════════════
# PATCH 2: Replace renderCards to use table layout
# ═══════════════════════════════════════════
old_render = '''    function renderCards(sk,sort){
      sort=sort||'views';
      const cat=catSlugMap[sk];
      const data=(DATA.categories&&DATA.categories[cat])||[];
      const el=document.getElementById(sk+'Cards');
      if(!el)return;
      if(!data.length){ el.innerHTML='<div class="no-data">No profiles in this category.</div>'; return; }
      let sorted=[...data];
      if(sort==='views') sorted.sort((a,b)=>b.views-a.views);
      else if(sort==='followers') sorted.sort((a,b)=>b.followers-a.followers);
      else sorted.sort((a,b)=>(a.name||'').localeCompare(b.name||''));
      el.innerHTML=sorted.map(p=>{
        const ppl=getPlat(p.platform);
        const ini=(p.name||'?').slice(0,2).toUpperCase();
        const bodyBits=[];
        if(p.comments) bodyBits.push('\\u{1f4ac} '+fmt(p.comments));
        if(p.shares) bodyBits.push('\\u2197 '+fmt(p.shares));
        return `<div class="card">
          <div class="card-top">
            <div class="card-user">
              <div class="ava" style="background:${ppl.bg};color:${ppl.color}">${esc(ini)}</div>
              <div><div class="uname" title="${esc(p.name)}">${esc(p.name)}</div><div class="ufoll">${p.followers?fmt(p.followers)+' followers':''}</div></div>
            </div>
            <div class="card-acts">
              <div class="pl-icon-sm" style="background:${ppl.bg}">${ppl.svg}</div>
              ${p.postLink?`<a class="view-btn" href="${esc(p.postLink)}" target="_blank" rel="noopener">View</a>`:`<span class="view-btn" style="background:#ccc;cursor:default">\\u2014</span>`}
            </div>
          </div>
          <div class="card-body">${bodyBits.join('&nbsp;&nbsp;')}</div>
          <div class="card-metrics three">
            <div class="met"><div class="met-val">${fmt(p.views)}</div><div class="met-key">Views</div></div>
            <div class="met"><div class="met-val">${fmt(p.likes)}</div><div class="met-key">Likes</div></div>
            <div class="met"><div class="met-val">${fmt(p.followers)}</div><div class="met-key">Followers</div></div>
          </div>
        </div>`;
      }).join('');
    }'''

new_render = '''    function renderCards(sk,sort){
      sort=sort||'views';
      const cat=catSlugMap[sk];
      const data=(DATA.categories&&DATA.categories[cat])||[];
      const el=document.getElementById(sk+'Cards');
      if(!el)return;
      if(!data.length){ el.innerHTML='<div class="no-data">No profiles in this category.</div>'; return; }
      let sorted=[...data];
      if(sort==='views') sorted.sort((a,b)=>b.views-a.views);
      else if(sort==='followers') sorted.sort((a,b)=>b.followers-a.followers);
      else sorted.sort((a,b)=>(a.name||'').localeCompare(b.name||''));
      el.innerHTML=`<div class="top10-card"><div style="overflow-x:auto"><table>
        <thead><tr><th>#</th><th>Page / Account</th><th>Platform</th><th>Category</th><th>Followers</th><th>Views</th><th>Likes</th><th>Comments</th><th>Shares</th><th>Post Link</th></tr></thead>
        <tbody>`+sorted.map((p,i)=>{
          const pl=getPlat(p.platform);
          return `<tr>
            <td>${i+1}</td>
            <td style="font-weight:600;color:var(--text)">${esc(p.name)}</td>
            <td><div class="pl-cell"><div class="pl-ico" style="background:${pl.bg}">${pl.svg}</div>${pl.label}</div></td>
            <td><span class="tag">${esc(p.category)}</span></td>
            <td style="font-weight:700;color:var(--text)">${fmt(p.followers)}</td>
            <td style="font-weight:700;font-size:14px;color:var(--text)">${fmt(p.views)}</td>
            <td>${fmt(p.likes)}</td>
            <td>${fmt(p.comments)}</td>
            <td>${fmt(p.shares)}</td>
            <td>${p.postLink?`<a href="${esc(p.postLink)}" target="_blank" rel="noopener">View \\u2197</a>`:'-'}</td>
          </tr>`;
        }).join('')+`</tbody></table></div></div>`;
    }'''

code = code.replace(old_render, new_render, 1)

# ═══════════════════════════════════════════
# PATCH 3: Change the tab content template from cards-grid to simple container
# ═══════════════════════════════════════════
old_template = '''          <div class="cards-grid" id="${sk}Cards"></div>`;'''
new_template = '''          <div id="${sk}Cards"></div>`;'''
code = code.replace(old_template, new_template, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nDone! Patched {path}")
print("\nChanges:")
print("  1. Category tabs now show a clean table (like Top 10) instead of cards")
print("  2. Numbers use international comma format (e.g. 300,000 instead of 3L)")
print("\nDeploy:")
print('  git add . && git commit -m "report: table layout + intl number format" && git push')