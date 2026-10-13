// Public UI geometry and labels only. No inputs, credentials or transcripts.
function getMotionRuntime(){
  const key=Symbol.for('inquire.motion.v2');if(document[key])return document[key];
  const state={seen:new Set(),active:null,suppressNext:null};
  const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
  const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function begin({title='',rect=null,kind='model',zh=false}={}){
    if(state.active)state.active.finish();
    if(reduced())return null;
    const theme=getComputedStyle(document.documentElement);
    const color=(name,fallback)=>theme.getPropertyValue(name).trim()||fallback;
    const bg=color('--inquire-bg','#f8f9fc'),surface=color('--inquire-surface','#fff'),ink=color('--inquire-ink','#302b3b'),accent=color('--inquire-accent','#6857c8'),line=color('--inquire-line','#e1dbea');
    const layer=make('div');layer.dataset.inquireTransition=kind;
    Object.assign(layer.style,{position:'fixed',inset:'0',zIndex:'10000',background:bg,overflow:'hidden',pointerEvents:'auto',fontFamily:'InquireSans, Noto Sans SC, sans-serif'});
    const glow=make('div');Object.assign(glow.style,{position:'absolute',width:'760px',height:'760px',left:'calc(50% - 380px)',top:'calc(50% - 380px)',background:`radial-gradient(ellipse,${accent}22,transparent 66%)`,opacity:'0',pointerEvents:'none'});
    const card=make('div');const width=Math.min(rect?.width||340,380,window.innerWidth-48),height=Math.min(rect?.height||174,190);
    const left=Math.max(24,Math.min(rect?.left??(window.innerWidth-width)/2,window.innerWidth-width-24)),top=Math.max(24,Math.min(rect?.top??(window.innerHeight-height)/2,window.innerHeight-height-24));
    Object.assign(card.style,{position:'absolute',left:`${left}px`,top:`${top}px`,width:`${width}px`,height:`${height}px`,border:`1px solid ${line}`,borderRadius:'14px',background:surface,color:ink,boxSizing:'border-box',padding:'24px',boxShadow:`0 25px 100px ${accent}18`,display:'flex',alignItems:'center',gap:'16px',overflow:'hidden',transformOrigin:'center'});
    const mark=document.createElementNS('http://www.w3.org/2000/svg','svg');mark.setAttribute('viewBox','0 0 32 32');mark.setAttribute('aria-hidden','true');Object.assign(mark.style,{width:'30px',height:'30px',color:accent,flex:'none'});
    const icon=document.createElementNS('http://www.w3.org/2000/svg','path');icon.setAttribute('d',title.includes('Gemini')?'M16 3C18 11 21 14 29 16C21 18 18 21 16 29C14 21 11 18 3 16C11 14 14 11 16 3Z':kind==='conversation'?'M5 6H27V23H15L7 28V23H5ZM10 12H22M10 17H17':'M16 3 29 16 16 29 3 16ZM16 9 23 16 16 23 9 16Z');icon.setAttribute('fill','none');icon.setAttribute('stroke','currentColor');icon.setAttribute('stroke-width','1.3');icon.setAttribute('stroke-linejoin','round');mark.append(icon);
    const content=make('div'),label=make('div',title),note=make('div',zh?'连接你的探究空间':'Opening your inquiry workspace');Object.assign(label.style,{fontSize:'25px',fontWeight:'600',letterSpacing:'-.035em',whiteSpace:'nowrap'});Object.assign(note.style,{fontSize:'12px',color:ink,opacity:'.55',marginTop:'10px',whiteSpace:'nowrap'});content.append(label,note);card.append(mark,content);
    const trace=document.createElementNS('http://www.w3.org/2000/svg','svg');trace.setAttribute('viewBox','0 0 600 220');Object.assign(trace.style,{position:'absolute',left:'calc(50% - 300px)',top:'calc(50% - 110px)',width:'600px',height:'220px',opacity:'.5',pointerEvents:'none'});
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d','M0 110H145C185 110 180 35 225 35H370C410 35 410 180 455 180H600');path.setAttribute('fill','none');path.setAttribute('stroke',accent);path.setAttribute('stroke-width','1');path.setAttribute('pathLength','1');trace.append(path);
    const skip=make('button',zh?'跳过转场':'Skip transition');skip.type='button';Object.assign(skip.style,{position:'absolute',bottom:'28px',right:'28px',border:`1px solid ${line}`,borderRadius:'8px',background:surface,color:ink,padding:'8px 13px',font:'inherit',fontSize:'12px',cursor:'pointer'});
    layer.append(glow,trace,card,skip);document.body.append(layer);
    const animations=[];let ended=false,timer,settled=false;
    const escape=e=>{if(e.key==='Escape')finish('skip');};
    function finish(reason){if(ended)return;if(!settled&&(reason==='skip'||reason==='timeout'))state.suppressNext=kind;ended=true;clearTimeout(timer);animations.forEach(a=>a.cancel());layer.remove();const publicState=document[Symbol.for('inquire.publicMotion')]||(document[Symbol.for('inquire.publicMotion')]={});publicState.hoverAfter=performance.now()+180;document.removeEventListener('keydown',escape);if(state.active?.layer===layer)state.active=null;}
    skip.onclick=()=>finish('skip');document.addEventListener('keydown',escape);
    const center={left:(window.innerWidth-width)/2,top:(window.innerHeight-height)/2};
    animations.push(card.animate([{left:`${left}px`,top:`${top}px`,opacity:.75,transform:'scale(.98)'},{left:`${center.left}px`,top:`${center.top}px`,opacity:1,transform:'scale(1.04)'},{left:`${center.left}px`,top:`${center.top}px`,opacity:1,transform:'scale(1)'}],{duration:460,easing:'cubic-bezier(.16,1,.3,1)',fill:'forwards'}));
    animations.push(glow.animate([{opacity:0,transform:'scale(.55)'},{opacity:1,transform:'scale(1)'}],{duration:600,fill:'forwards',easing:'ease-out'}));
    animations.push(path.animate([{strokeDasharray:'1',strokeDashoffset:1},{strokeDasharray:'1',strokeDashoffset:0}],{duration:700,fill:'forwards',easing:'ease-out'}));
    timer=setTimeout(()=>finish('timeout'),4000);
    state.active={layer,card,label,note,mark,trace,glow,animations,center,width,height,started:performance.now(),finish,markSettled(){settled=true},setTimer(fn,ms){clearTimeout(timer);timer=setTimeout(fn,ms);}};
    return state.active;
  }
  function settle({nonce,kind,title='',zh=false,target,regions=[]}){
    if(!Number.isSafeInteger(nonce)||nonce<=0||state.seen.has(nonce)||!target)return;
    state.seen.add(nonce);if(state.seen.size>128)state.seen.delete(state.seen.values().next().value);
    if(state.suppressNext===kind){state.suppressNext=null;state.active?.finish();return;}
    if(reduced()){state.active?.finish();return;}
    const source=document[Symbol.for('inquire.publicMotion')]||{};
    const active=state.active||begin({title,kind,zh,rect:(kind==='conversation'?source.case:source.model)});if(!active)return;
    active.markSettled();
    const delay=Math.max(0,460-(performance.now()-active.started));
    const finish=active.finish;
    active.setTimer(()=>{
      if(state.active!==active)return;
      const dest=target.getBoundingClientRect(),endWidth=Math.min(Math.max(dest.width,150),370),endHeight=Math.min(Math.max(dest.height,32),55);
      // Continue the same portal across Python's redraw, then reveal the real UI.
      active.animations.forEach(a=>a.cancel());Object.assign(active.card.style,{left:`${active.center.left}px`,top:`${active.center.top}px`,width:`${active.width}px`,height:`${active.height}px`,opacity:'1'});
      active.animations.push(active.card.animate([{left:`${active.center.left}px`,top:`${active.center.top}px`,width:`${active.width}px`,height:`${active.height}px`,padding:'24px',borderRadius:'14px',opacity:1},{left:`${Math.max(12,dest.left)}px`,top:`${Math.max(12,dest.top)}px`,width:`${endWidth}px`,height:`${endHeight}px`,padding:'8px 12px',borderRadius:'8px',opacity:1,offset:.82},{left:`${Math.max(12,dest.left)}px`,top:`${Math.max(12,dest.top)}px`,width:`${endWidth}px`,height:`${endHeight}px`,padding:'8px 12px',borderRadius:'8px',opacity:0}],{duration:720,easing:'cubic-bezier(.65,0,.2,1)',fill:'forwards'}));
      active.animations.push(active.label.animate([{fontSize:'25px'},{fontSize:'12px'}],{duration:580,fill:'forwards',easing:'ease-in-out'}),active.note.animate([{opacity:.55},{opacity:0}],{duration:240,fill:'forwards'}),active.mark.animate([{width:'30px',height:'30px'},{width:'16px',height:'16px'}],{duration:580,fill:'forwards'}));
      active.animations.push(active.layer.animate([{background:getComputedStyle(active.layer).backgroundColor,opacity:1},{background:getComputedStyle(active.layer).backgroundColor,opacity:0}],{duration:420,delay:290,fill:'forwards',easing:'ease-out'}));
      regions.forEach((region,i)=>{if(region)active.animations.push(region.animate([{opacity:0,clipPath:'inset(10% 0 0 0 round 12px)',transform:'translateY(22px)'},{opacity:1,clipPath:'inset(0% 0 0 0 round 12px)',transform:'translateY(0)'}],{duration:580,delay:140+i*65,easing:'cubic-bezier(.16,1,.3,1)',fill:'backwards'}));});
      active.setTimer(finish,750);
    },delay);
  }
  document[key]={begin,settle,seen:state.seen,finish:()=>state.active?.finish()};return document[key];
}
