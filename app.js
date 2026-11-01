const models=[['base','Base'],['teacher_ocr','OCR teacher'],['teacher_pickscore','PickScore teacher'],['teacher_geneval','GenEval teacher'],['velocity','FlowMap-OPD']];
const $=s=>document.querySelector(s);
let task='ocr',index=0;
const samples=()=>window.SAMPLES.filter(s=>s.task===task);
const current=()=>samples()[index];
const pad=n=>String(n).padStart(2,'0');
function lightbox(src,label){$('#lightbox-image').src=src;$('#lightbox-image').alt=label;$('#lightbox-caption').textContent=label;$('#lightbox').showModal()}
function renderStage(){
 const s=current(),stage=$('#stage');stage.replaceChildren();
 for(const [id,label] of models){
  const f=document.createElement('figure');if(id==='velocity')f.className='ours';else if(id==='teacher_'+task)f.className='specialist';
  const c=document.createElement('figcaption');c.textContent=label;
  const b=document.createElement('button');b.type='button';b.className='zoom';b.setAttribute('aria-label','Enlarge '+label);
  const im=document.createElement('img');im.src=s.images[id];im.alt=label+': '+s.prompt;b.append(im);b.addEventListener('click',()=>lightbox(s.images[id],label));
  f.append(c,b);stage.append(f)}}
function render(){
 const list=samples(),s=current();$('#prompt').textContent='“'+s.prompt+'”';$('#counter').textContent=pad(index+1)+' / '+pad(list.length);
 const thumbs=$('#thumbs');thumbs.replaceChildren();
 list.forEach((sample,i)=>{const b=document.createElement('button');b.type='button';b.className=i===index?'thumb active':'thumb';b.setAttribute('aria-label','Example '+(i+1));b.setAttribute('aria-pressed',String(i===index));const im=document.createElement('img');im.src=sample.thumbnail;im.alt='';b.append(im);b.addEventListener('click',()=>{index=i;render()});thumbs.append(b)});
 renderStage()}
document.querySelectorAll('[data-task]').forEach(b=>b.addEventListener('click',()=>{task=b.dataset.task;index=0;document.querySelectorAll('[data-task]').forEach(t=>{t.classList.toggle('active',t===b);t.setAttribute('aria-pressed',String(t===b))});render()}));
const step=d=>{const n=samples().length;index=(index+n+d)%n;render()};
$('#prev').addEventListener('click',()=>step(-1));$('#next').addEventListener('click',()=>step(1));
document.addEventListener('keydown',e=>{if($('#lightbox').open)return;const r=$('#comparison').getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;if(e.key==='ArrowLeft')step(-1);if(e.key==='ArrowRight')step(1)});
$('#close-lightbox').addEventListener('click',()=>$('#lightbox').close());$('#lightbox').addEventListener('click',e=>{if(e.target===$('#lightbox'))$('#lightbox').close()});
$('#copy-bib').addEventListener('click',async()=>{const t=$('#bib').textContent;try{await navigator.clipboard.writeText(t)}catch{const r=document.createRange();r.selectNodeContents($('#bib'));const sel=getSelection();sel.removeAllRanges();sel.addRange(r);document.execCommand('copy');sel.removeAllRanges()}$('#copy-bib').textContent='Copied';setTimeout(()=>$('#copy-bib').textContent='Copy',1600)});
render();
