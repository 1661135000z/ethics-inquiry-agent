export default function(component){
  const {parentElement,data,setTriggerValue}=component;
  const root=parentElement.querySelector('.theme-switch');
  const valid=mode=>mode==='light'||mode==='dark';
  const registry=document[Symbol.for('inquire.appearance')]||(document[Symbol.for('inquire.appearance')]={});
  let stored='';try{stored=localStorage.getItem('inquire.appearance')||'';}catch{}
  const mode=valid(data.mode)?data.mode:valid(registry.mode)?registry.mode:valid(stored)?stored:window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  const apply=next=>{
    registry.mode=next;document.documentElement.dataset.inquireTheme=next;
    try{localStorage.setItem('inquire.appearance',next);}catch{}
    root.querySelectorAll('button').forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.mode===next));});
  };
  if(!root._built||root.querySelectorAll('button').length!==2){
    root.setAttribute('role','group');
    ['light','dark'].forEach(next=>{
      const button=document.createElement('button');button.type='button';button.dataset.mode=next;
      const mark=document.createElementNS('http://www.w3.org/2000/svg','svg');mark.setAttribute('viewBox','0 0 24 24');mark.setAttribute('fill','none');mark.setAttribute('aria-hidden','true');
      const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d',next==='light'?'M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z':'M19.7 15.2A8 8 0 0 1 8.8 4.3 8 8 0 1 0 19.7 15.2Z');path.setAttribute('stroke','currentColor');path.setAttribute('stroke-width','1.6');path.setAttribute('stroke-linecap','round');path.setAttribute('stroke-linejoin','round');mark.append(path);button.append(mark);root.append(button);
    });root._built=true;
  }
  root.setAttribute('aria-label',data.zh?'外观模式':'Appearance');
  document.documentElement.lang=data.zh?'zh-CN':'en';
  root.querySelectorAll('button').forEach(button=>{
    const title=button.dataset.mode==='light'?(data.zh?'浅色模式':'Light mode'):(data.zh?'深色模式':'Dark mode');button.setAttribute('aria-label',title);button.title=title;
    button.onclick=()=>{apply(button.dataset.mode);setTriggerValue('change',button.dataset.mode);};
  });
  apply(mode);
  if(data.mode!==mode&&registry.reported!==mode){registry.reported=mode;setTriggerValue('change',mode);}
}
