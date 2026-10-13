export default function(component) {
  const {data}=component;
  const anchors={model:'.st-key-model_entry',scenario:'.st-key-scenario_region',conversation:'.st-key-conversation_region',composer:'.st-key-composer'};
  const selector=anchors[data.target];
  if(!selector||!Number.isSafeInteger(data.nonce))return;
  const seen=document[Symbol.for('inquire.navigation')]||(document[Symbol.for('inquire.navigation')]=new Set());
  const event=`${data.target}:${data.nonce}`;if(seen.has(event))return;seen.add(event);
  if(seen.size>128)seen.delete(seen.values().next().value);
  requestAnimationFrame(()=>{
    const target=document.querySelector(selector);if(!target)return;
    target.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});
    if(data.target==='composer'){
      const field=target.querySelector('textarea');if(field)field.focus({preventScroll:true});
    }else{target.setAttribute('tabindex','-1');target.focus({preventScroll:true});}
  });
}
