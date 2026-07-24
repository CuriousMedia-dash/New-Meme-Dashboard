#!/usr/bin/env python3
"""
Adds CSV upload feature to index.html
Run in your Meme Dashboard folder:  python patch_upload.py
"""
import sys, os

path = 'index.html'
if not os.path.exists(path):
    print(f"Error: {path} not found. Run this in your project folder.")
    sys.exit(1)

with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

with open(path + '.upload.bak', 'w', encoding='utf-8') as f:
    f.write(code)
print(f"Backup saved to {path}.upload.bak")

# ═══════════════════════════════════════════════════════════════════
# PATCH 1: Add upload button next to the settings gear icon
# ═══════════════════════════════════════════════════════════════════
old_btn = '<button class="icb" id="setBtn" title="Connect sheet" aria-label="Connect sheet">⚙</button>'
new_btn = '<button class="icb" id="uploadBtn" title="Upload CSV" aria-label="Upload CSV">📤</button>\n    <button class="icb" id="setBtn" title="Connect sheet" aria-label="Connect sheet">⚙</button>'
code = code.replace(old_btn, new_btn, 1)

# ═══════════════════════════════════════════════════════════════════
# PATCH 2: Add upload overlay HTML (before the toast div)
# ═══════════════════════════════════════════════════════════════════
upload_html = '''
<!-- Upload CSV overlay -->
<div class="ovl" id="uploadOvl" style="display:none">
  <div class="spanel" style="max-width:600px">
    <h3>Upload Creator Data</h3>
    <p>Upload a <code>.csv</code> file with columns: <b>Page Name, Page Link, Followers, Platform, Language, Category</b>. New rows will be added to your database. Duplicates (same name + platform) are skipped.</p>
    <div id="uploadDropZone" style="border:2px dashed var(--ln);border-radius:10px;padding:36px 20px;text-align:center;cursor:pointer;color:var(--ink3);font-size:13px;margin-bottom:12px;transition:border-color .2s,background .2s">
      <div style="font-size:28px;margin-bottom:8px;opacity:.5">📁</div>
      <div>Drag & drop a CSV file here, or <span style="color:var(--am);font-weight:600;text-decoration:underline">browse</span></div>
      <input type="file" id="uploadFileInput" accept=".csv" style="display:none">
    </div>
    <div id="uploadFileInfo" style="display:none;margin-bottom:12px">
      <div style="display:flex;align-items:center;justify-content:space-between;background:var(--up);border:1px solid var(--ln);border-radius:8px;padding:8px 12px;font-size:12px">
        <span id="uploadFileName" style="font-weight:600;color:var(--ink)"></span>
        <span id="uploadRowCount" style="color:var(--ink2);font-family:'JetBrains Mono',monospace"></span>
      </div>
    </div>
    <div id="uploadPreview" style="display:none;margin-bottom:12px;max-height:200px;overflow:auto;border:1px solid var(--ln);border-radius:8px">
      <table class="ct" id="uploadPreviewTbl" style="font-size:11px">
        <thead><tr id="uploadPreviewHead"></tr></thead>
        <tbody id="uploadPreviewBody"></tbody>
      </table>
    </div>
    <div id="uploadColMap" style="display:none;margin-bottom:12px;background:var(--up);border:1px solid var(--ln);border-radius:8px;padding:10px 12px">
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--ink3);margin-bottom:8px">Column Mapping</div>
      <div id="uploadColMapGrid" style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px"></div>
    </div>
    <div class="sa">
      <button class="bp" id="uploadPushBtn" disabled>Push to Database</button>
      <button class="bs" id="uploadCloseBtn">Close</button>
    </div>
    <div class="sm" id="uploadMsg"></div>
  </div>
</div>
'''
code = code.replace('<div class="toast" id="toast"></div>', upload_html + '\n<div class="toast" id="toast"></div>', 1)

# ═══════════════════════════════════════════════════════════════════
# PATCH 3: Add upload JS logic (before the closing })(); )
# ═══════════════════════════════════════════════════════════════════
upload_js = r'''
// ─── CSV Upload to Supabase ─────────────────────────────────────────
(function initUpload(){
  const uploadOvl=document.getElementById('uploadOvl');
  const dropZone=document.getElementById('uploadDropZone');
  const fileInput=document.getElementById('uploadFileInput');
  const fileInfo=document.getElementById('uploadFileInfo');
  const preview=document.getElementById('uploadPreview');
  const colMapWrap=document.getElementById('uploadColMap');
  const pushBtn=document.getElementById('uploadPushBtn');
  const uploadMsg=document.getElementById('uploadMsg');
  let parsedRows=[];
  let colMapping={};

  const DB_FIELDS=[
    {key:'page_name',label:'Page Name',required:true},
    {key:'page_link',label:'Page Link',required:false},
    {key:'followers',label:'Followers',required:true},
    {key:'platform',label:'Platform',required:true},
    {key:'language',label:'Language',required:true},
    {key:'category',label:'Category',required:true}
  ];

  const FIELD_ALIASES={
    page_name:['page name','page_name','name','influencer name','creator name','creator','influencer','account','handle','pagename','page'],
    page_link:['page link','page_link','link','url','profile url','profile link','channel link','instagram link','youtube link','profile','social link','pagelink','page url'],
    followers:['followers','subscriber','subscribers','follower count','subscriber count','follower','fans','fan count'],
    platform:['platform','channel','social media','network','site'],
    language:['language','lang','languages'],
    category:['category','content type','type','niche','genre','categories','cat']
  };

  document.getElementById('uploadBtn').addEventListener('click',()=>{
    resetUpload();
    uploadOvl.style.display='flex';
  });
  document.getElementById('uploadCloseBtn').addEventListener('click',()=>{uploadOvl.style.display='none'});
  uploadOvl.addEventListener('click',e=>{if(e.target===uploadOvl)uploadOvl.style.display='none'});

  dropZone.addEventListener('click',()=>fileInput.click());
  dropZone.addEventListener('dragover',e=>{e.preventDefault();dropZone.style.borderColor='var(--am)';dropZone.style.background='rgba(30,111,224,.04)'});
  dropZone.addEventListener('dragleave',()=>{dropZone.style.borderColor='var(--ln)';dropZone.style.background='transparent'});
  dropZone.addEventListener('drop',e=>{
    e.preventDefault();dropZone.style.borderColor='var(--ln)';dropZone.style.background='transparent';
    const file=e.dataTransfer.files[0];
    if(file)handleFile(file);
  });
  fileInput.addEventListener('change',e=>{if(e.target.files[0])handleFile(e.target.files[0])});

  function resetUpload(){
    parsedRows=[];colMapping={};
    fileInput.value='';
    fileInfo.style.display='none';
    preview.style.display='none';
    colMapWrap.style.display='none';
    pushBtn.disabled=true;
    uploadMsg.textContent='';uploadMsg.className='sm';
    dropZone.style.display='';
  }

  function parseCSV(text){
    const lines=[];let cur='';let inQ=false;
    for(let i=0;i<text.length;i++){
      const ch=text[i];
      if(ch==='"'){if(inQ&&text[i+1]==='"'){cur+='"';i++}else inQ=!inQ}
      else if((ch===','||ch==='\t')&&!inQ){lines.length===0?lines.push([cur]):lines[lines.length-1].push(cur);cur=''}
      else if((ch==='\n'||ch==='\r')&&!inQ){
        if(cur||lines.length>0&&lines[lines.length-1]){
          if(lines.length===0)lines.push([cur]);else lines[lines.length-1].push(cur);
        }
        if(lines[lines.length-1]&&lines[lines.length-1].length>0)lines.push([]);
        cur='';
        if(ch==='\r'&&text[i+1]==='\n')i++;
      }
      else cur+=ch;
    }
    if(cur&&lines.length>0)lines[lines.length-1].push(cur);
    return lines.filter(r=>r.length>1||r[0]&&r[0].trim());
  }

  function guessMapping(headers){
    const map={};
    const lowerHeaders=headers.map(h=>(h||'').trim().toLowerCase());
    DB_FIELDS.forEach(f=>{
      const aliases=FIELD_ALIASES[f.key]||[f.key];
      let bestIdx=-1;
      for(let i=0;i<lowerHeaders.length;i++){
        if(aliases.includes(lowerHeaders[i])){bestIdx=i;break}
      }
      if(bestIdx===-1){
        for(let i=0;i<lowerHeaders.length;i++){
          if(aliases.some(a=>lowerHeaders[i].includes(a)||a.includes(lowerHeaders[i]))){bestIdx=i;break}
        }
      }
      map[f.key]=bestIdx;
    });
    return map;
  }

  function handleFile(file){
    if(!file.name.toLowerCase().endsWith('.csv')){
      uploadMsg.textContent='Please upload a .csv file';uploadMsg.className='sm err';return;
    }
    const reader=new FileReader();
    reader.onload=e=>{
      const text=e.target.result;
      const lines=parseCSV(text);
      if(lines.length<2){uploadMsg.textContent='File is empty or has no data rows';uploadMsg.className='sm err';return}

      const headers=lines[0].map(h=>h.trim());
      const rows=lines.slice(1).filter(r=>r.some(c=>c&&c.trim()));
      parsedRows=rows;
      colMapping=guessMapping(headers);

      dropZone.style.display='none';
      document.getElementById('uploadFileName').textContent=file.name;
      document.getElementById('uploadRowCount').textContent=rows.length+' rows';
      fileInfo.style.display='block';

      // Preview table
      const headTr=document.getElementById('uploadPreviewHead');
      headTr.innerHTML=headers.map(h=>'<th style="font-size:10px;padding:6px 8px">'+esc(h)+'</th>').join('');
      const body=document.getElementById('uploadPreviewBody');
      body.innerHTML=rows.slice(0,5).map(r=>'<tr>'+r.map(c=>'<td style="padding:5px 8px;font-size:11px">'+esc((c||'').trim())+'</td>').join('')+'</tr>').join('');
      if(rows.length>5)body.innerHTML+='<tr><td colspan="'+headers.length+'" style="padding:6px 8px;color:var(--ink3);font-size:11px;text-align:center">… and '+(rows.length-5)+' more rows</td></tr>';
      preview.style.display='block';

      // Column mapping
      const grid=document.getElementById('uploadColMapGrid');
      grid.innerHTML='';
      DB_FIELDS.forEach(f=>{
        const label=document.createElement('div');
        label.style.cssText='color:var(--ink2);display:flex;align-items:center;gap:4px';
        label.innerHTML=(f.required?'<span style="color:var(--bd)">*</span>':'')+f.label+' →';
        const sel=document.createElement('select');
        sel.style.cssText='width:100%;padding:5px 8px;border:1px solid var(--ln);border-radius:6px;font-size:12px;background:var(--panel);color:var(--ink);font-family:Inter,sans-serif';
        sel.innerHTML='<option value="-1">— skip —</option>'+headers.map((h,i)=>'<option value="'+i+'"'+(colMapping[f.key]===i?' selected':'')+'>'+esc(h)+'</option>').join('');
        sel.addEventListener('change',()=>{colMapping[f.key]=parseInt(sel.value);checkReady()});
        grid.appendChild(label);grid.appendChild(sel);
      });
      colMapWrap.style.display='block';
      checkReady();
    };
    reader.readAsText(file);
  }

  function checkReady(){
    const ok=DB_FIELDS.filter(f=>f.required).every(f=>colMapping[f.key]>=0);
    pushBtn.disabled=!ok;
    if(!ok)uploadMsg.textContent='Map all required (*) columns to continue';
    else{uploadMsg.textContent=parsedRows.length+' rows ready to upload';uploadMsg.className='sm ok'}
  }

  function parseFollowers(v){
    if(v==null)return 0;if(typeof v==='number')return v;
    let s=String(v).trim().toLowerCase().replace(/,/g,'');
    let m=1;
    if(s.endsWith('k')){m=1e3;s=s.slice(0,-1)}
    else if(s.endsWith('m')){m=1e6;s=s.slice(0,-1)}
    else if(s.endsWith('l')||s.endsWith('lac')||s.endsWith('lakh')){m=1e5;s=s.replace(/l(?:ac|akh?)?$/i,'');}
    else if(s.endsWith('cr')||s.endsWith('crore')){m=1e7;s=s.replace(/cr(?:ore)?$/i,'');}
    const n=parseFloat(s);return isNaN(n)?0:Math.round(n*m);
  }

  pushBtn.addEventListener('click',async()=>{
    const {data:{user}}=await sb.auth.getUser();
    if(!user){uploadMsg.textContent='You must be signed in';uploadMsg.className='sm err';return}

    pushBtn.disabled=true;pushBtn.textContent='Uploading…';
    uploadMsg.textContent='';uploadMsg.className='sm';

    const toInsert=[];
    parsedRows.forEach(row=>{
      const get=key=>{const idx=colMapping[key];return idx>=0&&idx<row.length?(row[idx]||'').trim():''};
      const name=get('page_name');
      const platform=get('platform');
      if(!name||!platform)return;
      toInsert.push({
        page_name:name,
        page_link:get('page_link'),
        followers:parseFollowers(get('followers')),
        platform:platform,
        language:get('language')||'Unknown',
        category:get('category')||'Uncategorized'
      });
    });

    if(!toInsert.length){
      uploadMsg.textContent='No valid rows to upload';uploadMsg.className='sm err';
      pushBtn.disabled=false;pushBtn.textContent='Push to Database';return;
    }

    // Batch insert in chunks of 100
    let inserted=0,skipped=0,errors=0;
    const BATCH=100;
    for(let i=0;i<toInsert.length;i+=BATCH){
      const chunk=toInsert.slice(i,i+BATCH);
      pushBtn.textContent='Uploading… '+(i+chunk.length)+'/'+toInsert.length;
      const {data:result,error}=await sb.from('creators').upsert(chunk,{onConflict:'page_name,platform',ignoreDuplicates:true});
      if(error){
        console.warn('Batch insert error:',error.message);
        // Try individual inserts for this chunk
        for(const row of chunk){
          const {error:e2}=await sb.from('creators').upsert(row,{onConflict:'page_name,platform',ignoreDuplicates:true});
          if(e2){skipped++;console.warn('Row error:',row.page_name,e2.message)}
          else inserted++;
        }
      } else {
        inserted+=chunk.length;
      }
    }

    pushBtn.textContent='Push to Database';pushBtn.disabled=false;

    if(inserted>0){
      uploadMsg.textContent='✓ '+inserted+' creators added'+(skipped?' ('+skipped+' skipped)':'');
      uploadMsg.className='sm ok';
      showToast(inserted+' new creators added',true);
      // Reload the data
      await loadFromSupabase();
    } else {
      uploadMsg.textContent='No new rows added'+(skipped?' — '+skipped+' duplicates skipped':'');
      uploadMsg.className='sm err';
    }
  });
})();
'''

# Insert before the closing })();
old_close = '\n})();\n</script>'
new_close = '\n' + upload_js + '\n})();\n</script>'
code = code.replace(old_close, new_close, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nDone! Upload feature added to {path}")
print("\nWhat was added:")
print("  📤 Upload button in the header (next to ⚙)")
print("  📁 Drag & drop CSV upload modal")
print("  🔍 Auto column mapping with preview")
print("  ☁️  Push to Supabase with duplicate detection")
print("  🔄 Auto-refresh dashboard after upload")
print("\nIMPORTANT — Run this SQL in your Supabase SQL Editor to enable duplicate detection:")
print("  ALTER TABLE creators ADD CONSTRAINT creators_name_platform_unique UNIQUE (page_name, platform);")
print("\nThen commit and push:")
print('  git add . && git commit -m "add CSV upload feature" && git push')