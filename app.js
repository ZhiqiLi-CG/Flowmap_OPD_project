const models=[['base','Base'],['teacher_ocr','OCR teacher'],['teacher_pickscore','PickScore teacher'],['teacher_geneval','GenEval teacher'],['velocity','Student · FlowMap-OPD']];
const $=s=>document.querySelector(s);
let task='ocr',index=0,mode='grid';
const selected=new Set(models.map(([id])=>id));
const samples=()=>window.SAMPLES.filter(s=>s.task===task);
const current=()=>samples()[index];
for(const [id,label] of models){
 const l=document.createElement('label');l.className='toggle';const input=document.createElement('input');input.type='checkbox';input.value=id;input.checked=selected.has(id);
 input.addEventListener('change',()=>{input.checked?selected.add(id):selected.delete(id);renderImages()});l.append(input,document.createTextNode(label));$('#models').append(l);
 for(const target of ['#left-model','#right-model'])$(target).add(new Option(label,id));
}
$('#left-model').value='teacher_ocr';$('#right-model').value='velocity';
function lightbox(src,label){$('#lightbox-image').src=src;$('#lightbox-image').alt=label;$('#lightbox-caption').textContent=label;$('#lightbox').showModal()}
function renderImages(){
 const s=current(),gallery=$('#gallery');gallery.replaceChildren();gallery.style.setProperty('--cols',Math.max(1,Math.min(selected.size,5)));
 for(const [id,label]of models){if(!selected.has(id))continue;const f=document.createElement('figure');if(id==='velocity'||id==='teacher_'+s.task)f.className='highlight';const c=document.createElement('figcaption');c.textContent=label;const button=document.createElement('button');button.className='image-button';button.setAttribute('aria-label','Enlarge '+label);const im=document.createElement('img');im.src=s.images[id];im.alt=label+': '+s.prompt;button.append(im);button.addEventListener('click',()=>lightbox(im.src,label));f.append(c,button);gallery.append(f)}
 if(!selected.size){const p=document.createElement('p');p.textContent='Select a model above to begin comparing.';gallery.append(p)}
 for(const side of ['left','right']){const id=$('#'+side+'-model').value;$('#'+side+'-image').src=s.images[id];$('#'+side+'-image').alt=models.find(m=>m[0]===id)[1]+': '+s.prompt;$('#'+side+'-label').textContent=models.find(m=>m[0]===id)[1]}
}
function render(){const s=current();$('#prompt').textContent=s.prompt;$('#counter').textContent=String(index+1).padStart(2,'0')+' / '+samples().length;const thumbs=$('#thumbnails');thumbs.replaceChildren();samples().forEach((sample,i)=>{const b=document.createElement('button');b.className=i===index?'thumb active':'thumb';b.setAttribute('aria-label','Show example '+(i+1));b.setAttribute('aria-pressed',String(i===index));const im=document.createElement('img');im.src=sample.thumbnail;im.alt='';const num=document.createElement('span');num.textContent=String(i+1).padStart(2,'0');b.append(im,num);b.addEventListener('click',()=>{index=i;render()});thumbs.append(b)});renderImages()}
function setMode(next){mode=next;$('#gallery').hidden=mode!=='grid';$('#slider-panel').hidden=mode!=='slider';$('#models').hidden=mode!=='grid';$('#all').hidden=mode!=='grid';for(const key of ['grid','slider']){$('#'+key+'-mode').classList.toggle('active',mode===key);$('#'+key+'-mode').setAttribute('aria-pressed',String(mode===key))}}
document.querySelectorAll('[data-task]').forEach(b=>b.addEventListener('click',()=>{task=b.dataset.task;index=0;document.querySelectorAll('[data-task]').forEach(t=>{t.classList.toggle('active',t===b);t.setAttribute('aria-pressed',String(t===b))});$('#left-model').value='teacher_'+task;render()}));
$('#prev').addEventListener('click',()=>{index=(index+samples().length-1)%samples().length;render()});$('#next').addEventListener('click',()=>{index=(index+1)%samples().length;render()});
$('#all').addEventListener('click',()=>{document.querySelectorAll('#models input').forEach(i=>{i.checked=true;selected.add(i.value)});renderImages()});
for(const key of ['grid','slider'])$('#'+key+'-mode').addEventListener('click',()=>setMode(key));
for(const side of ['left','right'])$('#'+side+'-model').addEventListener('change',renderImages);
$('#wipe').addEventListener('input',e=>{const p=e.target.value;$('#left-layer').style.clipPath=`inset(0 ${100-p}% 0 0)`;$('#divider').style.left=p+'%'});
$('#close-lightbox').addEventListener('click',()=>$('#lightbox').close());$('#lightbox').addEventListener('click',e=>{if(e.target===$('#lightbox'))$('#lightbox').close()});render();
