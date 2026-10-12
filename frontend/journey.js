export default function(component) {
  const {parentElement,data,setTriggerValue} = component;
  const root=parentElement.querySelector('.journey');
  const steps=data.steps || [];
  const make=(tag,cls,text) => {const el=document.createElement(tag);el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  const signature=JSON.stringify(steps.map(step => ({id:step.id,title:step.title,detail:step.detail})));
  if(!root._ui || root._ui.signature!==signature) {
    const list=make('ol','journey-list'); list.setAttribute('aria-label','Inquiry progress');
    const rows=steps.map((step,i) => {
      const row=make('li','journey-step'),button=make('button','journey-button'),marker=make('span','journey-marker',String(i+1)),copy=make('span','journey-copy');
      button.type='button'; marker.setAttribute('aria-hidden','true');
      copy.append(make('span','journey-title',step.title),make('span','journey-detail',step.detail)); button.append(marker,copy);row.append(button);list.append(row);return {row,button,marker};
    });root.replaceChildren(list);root._ui={signature,rows};
  }
  root._ui.rows.forEach(({row,button,marker},i) => {
    const step=steps[i],normalized=step.state==='active'?'current':step.state,state=['complete','current','pending','locked'].includes(normalized)?normalized:'pending';
    row.dataset.state=state; marker.textContent=state==='complete'?'✓':String(i+1);
    button.disabled=state==='locked' || state==='pending';
    if(step.id===data.current)button.setAttribute('aria-current','step');else button.removeAttribute('aria-current');
    button.onclick=() => setTriggerValue('navigate',step.id);
  });
}
