import gsap from 'gsap';
import Flip from 'gsap/Flip';
gsap.registerPlugin(Flip);
export const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
export function enter(container:HTMLElement|null){
 if(!container||reduced())return()=>{};
 const ctx=gsap.context(()=>{
  gsap.from(container.querySelectorAll('[data-enter]'),{opacity:0,y:20,duration:.62,stagger:.055,ease:'power3.out',clearProps:'all'});
 },container);return()=>ctx.revert();
}
export async function morph(source:HTMLElement|null,target:HTMLElement|null,update:()=>void){
 if(reduced()||!source||!target){update();window.scrollTo({top:0,behavior:'instant'});return}
 const a=source.getBoundingClientRect();
 const ghost=source.cloneNode(true) as HTMLElement;
 ghost.classList.add('morph-ghost');
 ghost.removeAttribute('id');
 ghost.querySelectorAll('button').forEach(el=>{const visual=document.createElement('div');visual.className=el.className;visual.append(...Array.from(el.childNodes));el.replaceWith(visual)});
 ghost.querySelectorAll('input,select').forEach(el=>el.remove());
 Object.assign(ghost.style,{position:'fixed',left:a.left+'px',top:a.top+'px',width:a.width+'px',height:a.height+'px',margin:'0',pointerEvents:'none',zIndex:'40'});
 ghost.setAttribute('aria-hidden','true');document.body.append(ghost);
 const others=Array.from(document.querySelectorAll('.model-card,.folder-card')).filter(el=>el!==source);
 return new Promise<void>(resolve=>{
  const timeline=gsap.timeline({onComplete:()=>{ghost.remove();gsap.set(others,{clearProps:'all'});resolve()},onInterrupt:()=>{ghost.remove();resolve()}});
  const timer=window.setTimeout(()=>{timeline.progress(1);ghost.remove();resolve()},1600);
  timeline.to(others,{opacity:0,scale:.96,duration:.2,ease:'power2.out'},0)
    .to(ghost,{x:innerWidth/2-a.left-a.width/2,y:24,scale:1.025,duration:.32,ease:'power3.inOut'},.08)
    .call(()=>{update();window.scrollTo({top:0,behavior:'instant'});
      gsap.set(target,{opacity:0});
      const vars=Flip.fit(ghost,target,{getVars:true,scale:true});
      if(vars)gsap.to(ghost,{...vars,duration:.52,ease:'power4.inOut'});
      const scene=document.querySelector('.workspace');
      if(scene)gsap.fromTo(scene,{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:.6,ease:'power3.out',clearProps:'clipPath'});
    },[],.4)
    .to(ghost,{opacity:0,duration:.2},.88)
    .to(target,{opacity:1,duration:.2,clearProps:'opacity'},.9)
    .call(()=>window.clearTimeout(timer),[],1.08);
 });
}
