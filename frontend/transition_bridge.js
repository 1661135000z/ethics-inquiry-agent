export default function(component) {
  const {parentElement,data}=component;
  const root=parentElement.querySelector('.transition-bridge');
  const seen=root._seen||(root._seen=new Set());
  if(!Number.isSafeInteger(data.nonce)||data.nonce<=0||seen.has(data.nonce))return;
  if(root._finish)root._finish();
  const anchors={model:'.st-key-model_entry',scenario:'.st-key-scenario_region',conversation:'.st-key-conversation_region'};
  const target=document.querySelector(anchors[data.kind]);if(!target)return;
  seen.add(data.nonce);
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const registry=document[Symbol.for('inquire.publicMotion')]||{};
  const source=data.kind==='conversation'?registry.case:registry.model;
  const destination=target.getBoundingClientRect();
  if(reduced){target.scrollIntoView({behavior:'instant',block:'start'});return;}
  const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
  // Ghost geometry and labels are public UI data only. No configuration inputs are read.
  const layer=make('div');Object.assign(layer.style,{position:'fixed',inset:'0',zIndex:'10000',pointerEvents:'none',overflow:'hidden'});layer.setAttribute('aria-hidden','true');
  const card=make('div'),label=make('div',source?.title||data.title||''),note=make('div',data.title||'');
  const width=Math.min(source?.width||300,350,window.innerWidth-40),height=Math.min(source?.height||190,220);
  const startX=Math.max(20,Math.min(source?.left||window.innerWidth/2-width/2,window.innerWidth-width-20)),startY=Math.max(20,Math.min(source?.top||window.innerHeight/2-height/2,window.innerHeight-height-20));
  const centerX=(window.innerWidth-width)/2,centerY=(window.innerHeight-height)/2;
  Object.assign(card.style,{position:'absolute',left:`${startX}px`,top:`${startY}px`,width:`${width}px`,height:`${height}px`,boxSizing:'border-box',padding:'27px',border:'1px solid #b7a6d8',borderRadius:'18px',background:'radial-gradient(ellipse at 85% 0%,#d6c9ec,#fcfaff 70%)',color:'#4e3e67',boxShadow:'0 30px 100px #45326525',display:'flex',flexDirection:'column',justifyContent:'center',transformOrigin:'top left',fontFamily:'InquireSans, Noto Sans SC, sans-serif'});
  Object.assign(label.style,{fontSize:'26px',fontWeight:'650',letterSpacing:'-.035em',lineHeight:'1.3'});Object.assign(note.style,{fontSize:'12px',marginTop:'15px',opacity:'.7',lineHeight:'1.6'});card.append(label,note);
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 300 300');Object.assign(svg.style,{position:'absolute',left:`${window.innerWidth/2-150}px`,top:`${window.innerHeight/2-150}px`,width:'300px',height:'300px',opacity:'.35'});
  const ring=document.createElementNS('http://www.w3.org/2000/svg','circle');ring.setAttribute('cx','150');ring.setAttribute('cy','150');ring.setAttribute('r','120');ring.setAttribute('fill','none');ring.setAttribute('stroke','#aa92ce');ring.setAttribute('stroke-width','.7');ring.setAttribute('stroke-dasharray','240 30 80 30');svg.append(ring);
  layer.append(svg,card);target.append(layer);
  const skip=make('button','跳过 / Skip');skip.type='button';Object.assign(skip.style,{position:'fixed',bottom:'30px',left:'50%',transform:'translateX(-50%)',zIndex:'10001',font:'inherit',fontSize:'12px',padding:'8px 15px',border:'1px solid #cdbfde',borderRadius:'20px',background:'#fcfaff',color:'#6857c8',cursor:'pointer',pointerEvents:'auto'});target.append(skip);
  const animations=[];let ended=false,timer,observer;
  const finish=()=>{if(ended)return;ended=true;clearTimeout(timer);observer?.disconnect();animations.forEach(animation=>animation.cancel());layer.remove();skip.remove();root._finish=null;};root._finish=finish;skip.onclick=finish;skip.onkeydown=e=>{if(e.key==='Escape')finish();};
  const endX=Math.max(10,Math.min(destination.left+16,window.innerWidth-100)),endY=Math.max(10,Math.min(destination.top+20,window.innerHeight-55));
  animations.push(card.animate([
    {transform:'translate(0,0) scale(1)',opacity:.65},
    {transform:`translate(${centerX-startX}px,${centerY-startY}px) scale(1.04)`,opacity:1,offset:.38},
    {transform:`translate(${centerX-startX}px,${centerY-startY}px) scale(1)`,opacity:1,offset:.58},
    {transform:`translate(${endX-startX}px,${endY-startY}px) scale(.22,.22)`,opacity:0,offset:.9},
    {transform:`translate(${endX-startX}px,${endY-startY}px) scale(.22,.22)`,opacity:0}
  ],{duration:1050,easing:'cubic-bezier(.22,.8,.25,1)',fill:'both'}));
  animations.push(svg.animate([{transform:'scale(.6) rotate(-30deg)',opacity:0},{transform:'scale(1) rotate(0)',opacity:.4,offset:.45},{transform:'scale(1.1) rotate(25deg)',opacity:0}],{duration:1050,easing:'ease-out'}));
  const revealSelectors=data.kind==='model'?['.st-key-scenario_region','.st-key-journey_rail']:['.st-key-conversation_region','.st-key-journey_rail'];
  revealSelectors.forEach((selector,index)=>{const region=document.querySelector(selector);if(region)animations.push(region.animate([{opacity:.3,transform:'translateY(14px)'},{opacity:1,transform:'translateY(0)'}],{duration:400,delay:620+index*65,easing:'cubic-bezier(.2,.8,.2,1)',fill:'backwards'}));});
  observer=new MutationObserver(()=>{if(!target.isConnected)finish();});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  timer=setTimeout(finish,1080);
}
