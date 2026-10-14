export default function(component) {
  const {parentElement,data}=component;
  const root=parentElement.querySelector('.copy-reply');
  const label=data.zh?'复制':'Copy',success=data.zh?'已复制':'Copied',failure=data.zh?'复制失败':'Copy unavailable';
  if(!root._button||!root._button.isConnected){const button=document.createElement('button');button.type='button';button.className='copy-button';button.textContent=label;root.replaceChildren(button);root._button=button;}
  root._button.textContent=label;
  root._button.onclick=async()=>{
    const text=String(data.text||'');
    try {
      if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(text);
      else {const area=document.createElement('textarea');area.value=text;area.readOnly=true;Object.assign(area.style,{position:'fixed',opacity:'0',pointerEvents:'none'});root.append(area);area.select();const copied=document.execCommand('copy');area.remove();root._button.focus({preventScroll:true});if(!copied)throw new Error('copy unavailable');}
      root._button.textContent=success;
    }catch {root._button.textContent=failure;}
    clearTimeout(root._timer);root._timer=setTimeout(()=>{root._button.textContent=label;},1800);
  };
}
