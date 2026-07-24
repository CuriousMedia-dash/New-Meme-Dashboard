#!/usr/bin/env python3
"""Run this script in your Meme Dashboard folder: python patch_index.py"""
import sys, os

path = 'index.html'
if not os.path.exists(path):
    print(f"Error: {path} not found. Run this script in your project folder.")
    sys.exit(1)

with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Backup
with open(path + '.bak', 'w', encoding='utf-8') as f:
    f.write(code)
print(f"Backup saved to {path}.bak")

replacements = [
    # 1. Enter key saves the edit
    (
        "document.getElementById('epCancel').addEventListener('click',closeEdit);",
        "document.getElementById('epCancel').addEventListener('click',closeEdit);\n"
        "document.getElementById('epInput').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();document.getElementById('epSave').click()}});\n"
        "document.getElementById('epTextarea').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();document.getElementById('epSave').click()}});"
    ),
    # 2. Phone value clickable
    (
        "phoneValEl.textContent=phone||'\u2014';phoneValEl.title=phone||'Click \u270e to add';",
        "phoneValEl.textContent=phone||'\u2014';phoneValEl.title=phone||'Click to edit';\n"
        "  phoneValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(phoneValEl,r.id,'phone',phone,'Phone',false)});"
    ),
    # 3. Live link empty value clickable
    (
        "else{liveValEl=document.createElement('span');liveValEl.className='edit-val';liveValEl.textContent='\u2014';liveValEl.title='Click \u270e to add'}",
        "else{liveValEl=document.createElement('span');liveValEl.className='edit-val';liveValEl.textContent='\u2014';liveValEl.title='Click to edit';\n"
        "  liveValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(liveValEl,r.id,'liveLink',liveLink,'Live Link',false)})}"
    ),
    # 4. Views value clickable
    (
        "viewsValEl.className='edit-val'+(views?' has-val':'');viewsValEl.textContent=views?fmt(views):'\u2014';",
        "viewsValEl.className='edit-val'+(views?' has-val':'');viewsValEl.textContent=views?fmt(views):'\u2014';\n"
        "  viewsValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(viewsValEl,r.id,'views',views||'','Views',false)});"
    ),
    # 5. Likes value clickable
    (
        "likesValEl.className='edit-val'+(likes?' has-val':'');likesValEl.textContent=likes?fmt(likes):'\u2014';",
        "likesValEl.className='edit-val'+(likes?' has-val':'');likesValEl.textContent=likes?fmt(likes):'\u2014';\n"
        "  likesValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(likesValEl,r.id,'likes',likes||'','Like',false)});"
    ),
    # 6. Comments value clickable
    (
        "commentsValEl.className='edit-val'+(comments?' has-val':'');commentsValEl.textContent=comments?fmt(comments):'\u2014';",
        "commentsValEl.className='edit-val'+(comments?' has-val':'');commentsValEl.textContent=comments?fmt(comments):'\u2014';\n"
        "  commentsValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(commentsValEl,r.id,'comments',comments||'','Comment',false)});"
    ),
    # 7. Shares value clickable
    (
        "sharesValEl.className='edit-val'+(shares?' has-val':'');sharesValEl.textContent=shares?fmt(shares):'\u2014';",
        "sharesValEl.className='edit-val'+(shares?' has-val':'');sharesValEl.textContent=shares?fmt(shares):'\u2014';\n"
        "  sharesValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(sharesValEl,r.id,'shares',shares||'','Share',false)});"
    ),
    # 8. Remark empty value clickable
    (
        "else{remValEl=document.createElement('span');remValEl.className='edit-val';remValEl.textContent='\u2014';remValEl.style.color='var(--ink3)'}",
        "else{remValEl=document.createElement('span');remValEl.className='edit-val';remValEl.textContent='\u2014';remValEl.style.color='var(--ink3)';\n"
        "  remValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(remValEl,r.id,'remark',remark,'Remark',true)})}"
    ),
    # 9. Remark with value clickable
    (
        "if(remark){remValEl=document.createElement('span');remValEl.className='remark-pill';remValEl.textContent=remark;remValEl.title=remark}",
        "if(remark){remValEl=document.createElement('span');remValEl.className='remark-pill';remValEl.textContent=remark;remValEl.title=remark;\n"
        "  remValEl.style.cursor='pointer';remValEl.addEventListener('click',e=>{e.stopPropagation();openEdit(remValEl,r.id,'remark',remark,'Remark',true)})}"
    ),
    # 10-16. Campaign stat fields clickable
    (
        "wireCampFieldPencil('cdProvidedBudgetPen','providedBudget','Provided Budget');",
        "wireCampFieldPencil('cdProvidedBudgetPen','providedBudget','Provided Budget');\n"
        "document.getElementById('cdProvidedBudget').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'providedBudget',camp.providedBudget||'','Provided Budget',false)});"
    ),
    (
        "wireCampFieldPencil('cdExhaustedBudgetPen','exhaustedBudget','Exhausted Budget');",
        "wireCampFieldPencil('cdExhaustedBudgetPen','exhaustedBudget','Exhausted Budget');\n"
        "document.getElementById('cdExhaustedBudget').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'exhaustedBudget',camp.exhaustedBudget||'','Exhausted Budget',false)});"
    ),
    (
        "wireCampFieldPencil('cdTotalViewershipPen','totalViewership','Total Viewership');",
        "wireCampFieldPencil('cdTotalViewershipPen','totalViewership','Total Viewership');\n"
        "document.getElementById('cdTotalViewership').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'totalViewership',camp.totalViewership||'','Total Viewership',false)});"
    ),
    (
        "wireCampFieldPencil('cdTargetedViewershipPen','targetedViewership','Targeted Viewership');",
        "wireCampFieldPencil('cdTargetedViewershipPen','targetedViewership','Targeted Viewership');\n"
        "document.getElementById('cdTargetedViewership').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'targetedViewership',camp.targetedViewership||'','Targeted Viewership',false)});"
    ),
    (
        "wireCampFieldPencil('cdTotalEngagementPen','totalEngagement','Total Engagement');",
        "wireCampFieldPencil('cdTotalEngagementPen','totalEngagement','Total Engagement');\n"
        "document.getElementById('cdTotalEngagement').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'totalEngagement',camp.totalEngagement||'','Total Engagement',false)});"
    ),
    (
        "wireCampFieldPencil('cdTimelinePen','timeline','Timeline');",
        "wireCampFieldPencil('cdTimelinePen','timeline','Timeline');\n"
        "document.getElementById('cdTimeline').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'timeline',camp.timeline||'','Timeline',false)});"
    ),
    (
        "wireCampFieldPencil('cdPocPen','poc','Point of Contact',true);",
        "wireCampFieldPencil('cdPocPen','poc','Point of Contact',true);\n"
        "document.getElementById('cdPoc').addEventListener('click',e=>{e.stopPropagation();const camp=campaigns.get(activeCampaignId);if(!camp)return;openCampFieldEdit(e.currentTarget,'poc',camp.poc||'','Point of Contact',true)});"
    ),
]

applied = 0
for old, new in replacements:
    if old in code:
        code = code.replace(old, new, 1)
        applied += 1
    else:
        print(f"WARNING: Could not find: {old[:60]}...")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nDone! Applied {applied}/{len(replacements)} patches to {path}")
print("Changes:")
print("  1. Click anywhere on a value field to open the editor")
print("  2. Press Enter to save (Shift+Enter for new line in remarks)")
print("\nNow commit and push:")
print('  git add . && git commit -m "click-to-edit and enter-to-save" && git push')