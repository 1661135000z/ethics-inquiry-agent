export default function(component) {
  const {parentElement, data, setTriggerValue} = component;
  const root = parentElement.querySelector('.case-picker');
  const state = root._previewState || (root._previewState = {epoch:data.epoch, id:null, timer:null});
  if (state.epoch !== data.epoch) { state.epoch = data.epoch; state.id = null; }
  clearTimeout(state.timer);
  const cases = data.cases || [];
  if (!cases.some(item => item.id === state.id)) state.id = null;
  const make = (tag, cls, text) => { const el=document.createElement(tag); el.className=cls; if(text !== undefined) el.textContent=text; return el; };
  // Reuse nodes across unrelated reruns so hover and keyboard focus remain stable.
  if (!root._ui || root._ui.signature !== JSON.stringify(cases) || !root.querySelector('.case-row')) {
    const row=make('div','case-row'), detail=make('section','case-details');
    detail.setAttribute('aria-label','Scenario preview');
    const heading=make('h3','detail-heading'), body=make('p','detail-body'), source=make('p','detail-source');
    const inner=make('div','detail-inner'),content=make('div','detail-content'); content.append(heading,body,source);inner.append(content);detail.append(inner);
    const slots=cases.map(item => {
      const slot=make('div','case-slot'), choose=make('button','case-button');
      choose.type='button';
      const face=make('span','folder-face');
      face.append(make('span','case-title',item.title),make('span','case-subtitle',item.subtitle));
      choose.append(face);
      const preview=make('button','preview-button',data.zh ? '预览' : 'Preview'); preview.type='button'; preview.setAttribute('aria-label',`${data.zh ? '预览' : 'Preview'} ${item.title}`);
      slot.append(choose,preview); row.append(slot); return {slot,choose,preview,item};
    });
    root.replaceChildren(row,detail);
    root._ui={row,detail,heading,body,source,slots,signature:JSON.stringify(cases)};
  }
  const ui=root._ui;
  const cancel=() => clearTimeout(state.timer);
  const paint=() => {
    const item=cases.find(item => item.id === state.id), index=cases.indexOf(item);
    ui.detail.classList.toggle('is-open',Boolean(item)); ui.detail.inert=!item; ui.detail.setAttribute('aria-hidden',String(!item));
    ui.heading.textContent=item?.title || ''; ui.body.textContent=item?.text || ''; ui.source.textContent=item?.source || '';
    ui.slots.forEach(({slot,choose,preview,item},i) => {
      slot.classList.toggle('is-preview',item.id===state.id);
      slot.classList.toggle('is-adjacent',index>=0 && Math.abs(index-i)===1);
      choose.setAttribute('aria-pressed',String(item.id===data.selected));
      preview.setAttribute('aria-expanded',String(item.id===state.id));
    });
  };
  const open=id => { cancel(); if(state.id!==id){state.id=id;paint();
    if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      [ui.heading,ui.body,ui.source].forEach((el,index)=>{el.getAnimations().forEach(animation=>animation.cancel());el.animate([{opacity:0,transform:'translateY(9px)'},{opacity:1,transform:'translateY(0)'}],{duration:350,delay:index*45,fill:'backwards',easing:'cubic-bezier(.2,.8,.2,1)'});});
    }
  } };
  const close=() => { cancel(); state.id=null; paint(); };
  const later=() => { cancel(); if(!window.matchMedia('(hover: hover) and (min-width: 651px)').matches) return; state.timer=setTimeout(() => {
    const focused=parentElement.activeElement || document.activeElement;
    const active=ui.slots.find(entry => entry.item.id===state.id); const inUnion=active?.slot.matches(':hover') || ui.detail.matches(':hover'); const keyboardFocus=Boolean(focused && root.contains(focused) && focused.matches(':focus-visible')); if (!keyboardFocus && !inUnion) close();
  },120); };
  const canHover=e=>e.pointerType!=='touch' && window.matchMedia('(hover: hover) and (min-width: 651px)').matches && !document.querySelector('[data-inquire-transition]') && performance.now()>=(document[Symbol.for('inquire.publicMotion')]?.hoverAfter||0);
  ui.slots.forEach(({slot,choose,preview,item}) => {
    slot.onpointerenter=e => {if(canHover(e))open(item.id);};
    slot.onpointermove=e => {if(canHover(e)&&state.id!==item.id)open(item.id);};
    slot.onpointerleave=later;
    choose.onfocus=() => open(item.id); choose.onblur=later;
    choose.onclick=() => {
      const rect=choose.getBoundingClientRect();
      const registry=document[Symbol.for('inquire.publicMotion')]||(document[Symbol.for('inquire.publicMotion')]={});
      registry.case={left:rect.left,top:rect.top,width:rect.width,height:rect.height,title:item.title};
      setTriggerValue('choose',item.id);
    };
    preview.onclick=() => {state.id===item.id ? close() : open(item.id);};
    preview.onblur=later;
  });
  root.onpointerleave=later; ui.detail.onpointerenter=cancel; ui.detail.onpointerleave=later;
  root.onkeydown=e => {if(e.key==='Escape'){e.preventDefault();close();}};
  paint();
}
