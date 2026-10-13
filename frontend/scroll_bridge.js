export default function(component) {
  const {parentElement,data}=component;
  const root=parentElement.querySelector('.scroll-bridge');
  if(root._nonce===data.nonce) return;
  root._nonce=data.nonce;
  const anchors={model:'.st-key-model_entry',scenario:'.st-key-scenario_region',conversation:'.st-key-conversation_region',composer:'.st-key-composer'};
  const selector=anchors[data.target];
  if(!selector) return;
  // Scope all access to explicitly owned navigation containers. Never read inputs.
  requestAnimationFrame(() => {
    const target=document.querySelector(selector);
    if(!target) return;
    target.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});
    if(data.target==='model') {
      const opener=target.querySelector('button[data-testid="stPopoverButton"]');
      if(opener) {if(opener.getAttribute('aria-expanded')!=='true') opener.click(); opener.focus({preventScroll:true});}
    } else if(data.target==='composer') {
      const field=target.querySelector('textarea'); if(field) field.focus({preventScroll:true});
    } else {
      target.setAttribute('tabindex','-1'); target.focus({preventScroll:true});
    }
  });
}
