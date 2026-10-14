export default function(component) {
  const {parentElement,data,setTriggerValue} = component;
  const root=parentElement.querySelector('.journey');
  const steps=data.steps || [];
  const make=(tag,cls,text) => {const el=document.createElement(tag);el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  // Copy and status updates keep the same nodes, preserving focus and true progress motion.
  const signature=JSON.stringify(steps.map(step => step.id));
  if(!root._ui || root._ui.signature!==signature || !root.querySelector('.journey-list')) {
    const list=make('ol','journey-list'); list.setAttribute('aria-label','Inquiry progress');
    const rows=steps.map((step,i) => {
      const row=make('li','journey-step'),button=make('button','journey-button'),marker=make('span','journey-marker',String(i+1)),copy=make('span','journey-copy');
      const title=make('span','journey-title',step.title),detail=make('span','journey-detail',step.detail),connector=make('span','journey-connector');
      button.type='button'; marker.setAttribute('aria-hidden','true');connector.setAttribute('aria-hidden','true');
      copy.append(title,detail);button.append(marker,copy);row.append(button);if(i<steps.length-1)row.append(connector);list.append(row);return {row,button,marker,title,detail,connector,state:null};
    });root.replaceChildren(list);root._ui={signature,rows};
  }
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  root._ui.rows.forEach((entry,i) => {
    const {row,button,marker,title,detail,connector}=entry;
    const step=steps[i],normalized=step.state==='active'?'current':step.state,state=['complete','current','pending','locked'].includes(normalized)?normalized:'pending';
    const previous=entry.state;
    title.textContent=step.title;detail.textContent=step.detail;
    row.dataset.state=state;marker.textContent=state==='complete'?'✓':String(i+1);
    connector.style.setProperty('--line-progress',state==='complete'?'1':'0');
    button.disabled=state==='locked' || state==='pending';
    if(step.id===data.current)button.setAttribute('aria-current','step');else button.removeAttribute('aria-current');
    button.onclick=() => setTriggerValue('navigate',step.id);
    if(previous!==null&&previous!==state&&!reduced){
      if(state==='complete'){
        marker.getAnimations().forEach(animation=>animation.cancel());
        marker.animate([{opacity:.4,transform:'scale(.7)'},{opacity:1,transform:'scale(1.08)',offset:.65},{opacity:1,transform:'scale(1)'}],{duration:280,easing:'cubic-bezier(.2,.8,.2,1)'});
        connector.animate([{transform:'scaleY(0)'},{transform:'scaleY(1)'}],{duration:350,easing:'cubic-bezier(.2,.8,.2,1)'});
      }
      if(state==='current'){
        button.getAnimations().forEach(animation=>animation.cancel());
        button.animate([{opacity:.5,transform:'translateY(7px)'},{opacity:1,transform:'translateY(0)'}],{duration:250,easing:'cubic-bezier(.2,.8,.2,1)'});
      }
    }
    entry.state=state;
  });
}
