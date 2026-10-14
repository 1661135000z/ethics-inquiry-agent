export default function(component) {
  const {parentElement,data}=component;
  const root=parentElement.querySelector('.message-motion');
  const previous=root._seen;
  const start=previous && previous.epoch===data.epoch ? previous.count : data.count;
  root._seen={epoch:data.epoch,count:data.count};
  if(data.count<=start || window.matchMedia('(prefers-reduced-motion:reduce)').matches) return;
  requestAnimationFrame(() => {
    const transcript=document.querySelector('.st-key-transcript');
    if(!transcript) return;
    const messages=transcript.querySelectorAll('[data-testid="stChatMessage"]');
    for(let i=start;i<Math.min(data.count,messages.length);i++) {
      messages[i].animate([{opacity:0,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}],{duration:200,easing:'ease-out'});
    }
  });
}
