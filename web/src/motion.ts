import gsap from 'gsap';
import Flip from 'gsap/Flip';
gsap.registerPlugin(Flip);
export const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
export function enter(container:HTMLElement|null){
 if(!container||reduced()||document.documentElement.dataset.transiting)return()=>{};
 const ctx=gsap.context(()=>{gsap.from(container.querySelectorAll('[data-enter]'),{opacity:0,y:24,duration:.7,stagger:.07,ease:'power3.out',clearProps:'opacity,transform'});},container);
 return()=>ctx.revert();
}
/** A visual transition never owns an accepted response or prevents its commit. */
async function animateMorph(source:HTMLElement|null,getTarget:()=>HTMLElement|null,update:()=>void){
 if(reduced()||!source){update();window.scrollTo({top:0,behavior:'instant'});return}
 const origin=source.dataset.model?source:source.querySelector<HTMLElement>('.situation-label strong,h3')||source;
 const rect=origin.getBoundingClientRect();
 if(!rect.width||!rect.height){update();return}
 const ghost=origin.cloneNode(true) as HTMLElement,veil=document.createElement('div');
 ghost.classList.add('morph-ghost');ghost.removeAttribute('id');ghost.setAttribute('aria-hidden','true');ghost.inert=true;
 ghost.querySelectorAll('[id]').forEach(el=>el.removeAttribute('id'));
 ghost.querySelectorAll('input,select,textarea').forEach(el=>el.remove());
 ghost.querySelectorAll('button,a').forEach(el=>{const visual=document.createElement('div');visual.className=el.className;visual.append(...Array.from(el.childNodes));el.replaceWith(visual)});
 const style=getComputedStyle(origin);
 Object.assign(ghost.style,{position:'fixed',left:rect.left+'px',top:rect.top+'px',width:rect.width+'px',height:rect.height+'px',margin:'0',padding:source.dataset.model?'2px':'0',pointerEvents:'none',zIndex:'40',fontFamily:style.fontFamily,fontSize:style.fontSize,fontWeight:style.fontWeight,lineHeight:style.lineHeight,color:style.color,letterSpacing:style.letterSpacing});
 veil.className='transition-veil';veil.setAttribute('aria-hidden','true');
 veil.innerHTML='<svg viewBox="0 0 1440 850" preserveAspectRatio="xMidYMid slice"><ellipse cx="720" cy="400" rx="360" ry="180"/><ellipse cx="720" cy="400" rx="460" ry="230"/><path d="M0 460C280 460 350 180 720 180s450 280 720 280"/></svg>';
 document.body.append(veil,ghost);document.documentElement.dataset.transiting='true';
 const others=Array.from(document.querySelectorAll<HTMLElement>('.model-card,.situation-option')).filter(el=>el!==source);
 return new Promise<void>(resolve=>{
  let applied=false,finished=false,target:HTMLElement|null=null,timer:number;let timeline:gsap.core.Timeline|null=null;const animated:HTMLElement[]=[];
  const apply=()=>{if(!applied){applied=true;update()}};
  const cleanup=()=>{if(finished)return;finished=true;window.clearTimeout(timer);try{ghost.remove();veil.remove();delete document.documentElement.dataset.transiting;for(const el of [...others,...animated,...(target?[target]:[])]){el.style.removeProperty('opacity');el.style.removeProperty('transform')}}finally{resolve()}};
  timer=window.setTimeout(()=>{try{apply()}finally{timeline?.kill();cleanup()}},1800);
  try{
   timeline=gsap.timeline({onComplete:cleanup,onInterrupt:()=>{try{apply()}finally{cleanup()}}});
   gsap.set(veil,{opacity:0});gsap.set(ghost,{rotationX:0,rotationY:0});
   const lines=veil.querySelectorAll<SVGGeometryElement>('path,ellipse');lines.forEach(line=>{const length=line.getTotalLength();gsap.set(line,{strokeDasharray:length,strokeDashoffset:length})});
   timeline.to(others,{opacity:0,y:8,scale:.97,duration:.23,ease:'power2.in'},0)
    .to(veil,{opacity:1,duration:.25},0)
    .to(lines,{strokeDashoffset:0,duration:.72,stagger:.05,ease:'power3.inOut'},.05)
    .to(ghost,{x:innerWidth/2-rect.left-rect.width/2,y:source.dataset.model?Math.min(innerHeight*.35,320)-rect.top-rect.height/2:-12,scale:1.025,duration:.35,ease:'power3.inOut'},.03)
    .call(()=>{try{
      apply();window.scrollTo({top:0,behavior:'instant'});target=getTarget();
      if(target){gsap.set(target,{opacity:0});const fit=Flip.fit(ghost,target,{getVars:true,scale:true});if(fit)timeline!.to(ghost,{...fit,duration:.57,ease:'power4.inOut'},.38);timeline!.to(target,{opacity:1,duration:.23,clearProps:'opacity'},.85)}
      const scene=document.querySelector('.workspace');
      if(scene){animated.push(scene as HTMLElement,...Array.from(scene.querySelectorAll<HTMLElement>('[data-enter]')));timeline!.fromTo(scene,{opacity:0,y:25},{opacity:1,y:0,duration:.6,ease:'power3.out',clearProps:'opacity,transform'},.49);timeline!.fromTo(scene.querySelectorAll('[data-enter]'),{opacity:0,y:16},{opacity:1,y:0,duration:.55,stagger:.055,ease:'power3.out',clearProps:'opacity,transform'},.56)}
     }catch{apply();cleanup()}},[],.36)
    .to(ghost,{opacity:0,duration:.2},.82)
    .to(veil,{opacity:0,duration:.35},.92);
  }catch{try{apply()}finally{timeline?.kill();cleanup()}}
 });
}

export async function morph(source:HTMLElement|null,getTarget:()=>HTMLElement|null,update:()=>void){
 let applied=false;const commit=()=>{if(!applied){applied=true;update()}};
 try{await animateMorph(source,getTarget,commit)}catch{commit();document.querySelectorAll('.morph-ghost,.transition-veil').forEach(el=>el.remove());delete document.documentElement.dataset.transiting}
}
