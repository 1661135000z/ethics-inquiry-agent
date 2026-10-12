export default function(component) {
  const {parentElement,data,setTriggerValue}=component;
  const root=parentElement.querySelector('.welcome');
  const make=(tag,cls,text)=>{const el=document.createElement(tag);el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  const zh=Boolean(data.zh);
  const models=[
    {id:'gemini',name:'Gemini',glyph:'✦',label:zh?'Google · 灵活推理':'Google · Flexible reasoning',detail:zh?'从审计情境出发，展开清晰、连贯的询问。':'Explore the audit scenario with clear, connected questions.'},
    {id:'zhipu',name:'GLM',glyph:'◈',label:zh?'智谱 · 中文交流':'Zhipu · Chinese conversation',detail:zh?'用自然的中文追问，逐步厘清证据与判断。':'Follow the evidence through a natural Chinese conversation.'},
    {id:'openrouter',name:'OpenRouter',glyph:'◎',label:zh?'可选 · 免费模型路由':'Optional · Free model routing',detail:zh?'通过已有配置连接免费模型。':'Connect to free models using your existing configuration.'}
  ];
  const signature=String(zh);
  if(!root._ui||root._ui.signature!==signature){
    const intro=make('div','welcome-intro');
    intro.append(make('p','welcome-eyebrow',zh?'审计询问 · 练习空间':'AUDIT INQUIRY · PRACTICE SPACE'),make('h2','welcome-heading',zh?'让每一次追问，都更进一步。':'A better question opens the next door.'),make('p','welcome-description',zh?'选择你的模型伙伴，再带着一个情境开始对话。':'Choose your model partner, then bring a scenario into the conversation.'));
    const grid=make('div','model-grid');grid.setAttribute('role','group');grid.setAttribute('aria-label',zh?'选择模型服务':'Choose a model provider');
    const cards=models.map(model=>{
      const button=make('button','model-card');button.type='button';button.dataset.provider=model.id;
      const top=make('span','model-top'),mark=make('span','model-glyph',model.glyph),status=make('span','model-status');mark.setAttribute('aria-hidden','true');top.append(mark,status);
      const name=make('span','model-name',model.name),label=make('span','model-label',model.label),detail=make('span','model-detail',model.detail),action=make('span','model-action');
      button.append(top,name,label,detail,action);grid.append(button);return {button,status,action,model};
    });
    root.replaceChildren(intro,grid);root._ui={signature,cards};
    if(!root._entered&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      root._entered=true;[intro,...cards.map(entry=>entry.button)].forEach((el,i)=>el.animate([{opacity:0,transform:'translateY(16px)'},{opacity:1,transform:'translateY(0)'}],{duration:500,delay:i*75,easing:'cubic-bezier(.2,.8,.2,1)',fill:'backwards'}));
    }
  }
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  root._ui.cards.forEach(({button,status,action,model})=>{
    const selected=model.id===data.selected,ready=Boolean(data.ready?.[model.id]);
    if(selected){const rect=button.getBoundingClientRect();const registry=document[Symbol.for('inquire.publicMotion')]||(document[Symbol.for('inquire.publicMotion')]={});registry.model={left:rect.left,top:rect.top,width:rect.width,height:rect.height,title:model.name};}
    button.setAttribute('aria-pressed',String(selected));status.textContent=ready?(zh?'已配置':'Configured'):(zh?'待配置':'Set up');status.dataset.ready=String(ready);
    action.textContent=selected?(zh?'当前选择 ✓':'Selected ✓'):(zh?'选择模型 ↗':'Choose model ↗');
    button.onclick=()=>{
      const rect=button.getBoundingClientRect();
      const registry=document[Symbol.for('inquire.publicMotion')]||(document[Symbol.for('inquire.publicMotion')]={});
      registry.model={left:rect.left,top:rect.top,width:rect.width,height:rect.height,title:model.name};
      setTriggerValue('choose',model.id);
    };
    button.onpointermove=e=>{if(reduced||e.pointerType==='touch')return;const rect=button.getBoundingClientRect();const x=(e.clientX-rect.left)/rect.width-.5,y=(e.clientY-rect.top)/rect.height-.5;button.style.setProperty('--rx',`${-y*7}deg`);button.style.setProperty('--ry',`${x*8}deg`);button.style.setProperty('--shine-x',`${(x+.5)*100}%`);};
    button.onpointerleave=()=>{button.style.setProperty('--rx','0deg');button.style.setProperty('--ry','0deg');};
  });
}
