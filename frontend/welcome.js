export default function(component) {
  const {parentElement,data,setTriggerValue}=component;
  const root=parentElement.querySelector('.welcome');
  const make=(tag,cls,text)=>{const el=document.createElement(tag);el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  const svg=(tag,attrs={})=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([key,value])=>el.setAttribute(key,value));return el;};
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const zh=Boolean(data.zh);
  // All illustration geometry is local, literal SVG. Provider copy remains plain text.
  const providerMark=id=>{
    const mark=svg('svg',{viewBox:'0 0 32 32',fill:'none','aria-hidden':'true',focusable:'false'});
    if(id==='gemini'){
      mark.append(svg('path',{d:'M16 3C17.8 11.2 20.8 14.2 29 16C20.8 17.8 17.8 20.8 16 29C14.2 20.8 11.2 17.8 3 16C11.2 14.2 14.2 11.2 16 3Z',fill:'currentColor'}));
    }else if(id==='zhipu'){
      mark.append(svg('path',{d:'M16 3 29 16 16 29 3 16Z',stroke:'currentColor','stroke-width':'1.5'}),svg('path',{d:'M16 9 23 16 16 23 9 16Z',fill:'currentColor'}));
    }else{
      mark.append(svg('path',{d:'M6 16H14M14 16 23 7M14 16 23 25',stroke:'currentColor','stroke-width':'1.8','stroke-linecap':'round'}));
      [[5,16],[25,6],[25,26]].forEach(([cx,cy])=>mark.append(svg('circle',{cx,cy,r:'3',fill:'currentColor'})));
    }
    return mark;
  };
  const actionMark=()=>{const mark=svg('svg',{viewBox:'0 0 16 16',fill:'none','aria-hidden':'true',focusable:'false'});const path=svg('path',{'stroke':'currentColor','stroke-width':'1.5','stroke-linecap':'round','stroke-linejoin':'round'});mark.append(path);return {mark,path};};
  const inquiryArt=()=>{
    const frame=make('div','inquiry-art');frame.setAttribute('aria-hidden','true');
    const drawing=svg('svg',{viewBox:'0 0 420 180',fill:'none',focusable:'false'});
    const defs=svg('defs'),gradient=svg('linearGradient',{id:'inquiry-glass',x1:'189',y1:'19',x2:'330',y2:'163',gradientUnits:'userSpaceOnUse'});
    gradient.append(svg('stop',{'stop-color':'#d6e7ff','stop-opacity':'.7'}),svg('stop',{offset:'.56','stop-color':'#eee8ff','stop-opacity':'.35'}),svg('stop',{offset:'1','stop-color':'#b6aceb','stop-opacity':'.6'}));defs.append(gradient);drawing.append(defs);
    const plane=svg('g',{'class':'art-plane'});
    plane.append(svg('path',{d:'M30 150H393M52 27H379',stroke:'#e7e3ef','stroke-width':'1'}),svg('path',{d:'M358 15V166M91 10V164',stroke:'#e7e3ef','stroke-dasharray':'2 6'}));
    const papers=svg('g',{'class':'art-papers'});
    papers.append(svg('rect',{x:'64',y:'27',width:'91',height:'118',rx:'5',transform:'rotate(-10 109 86)',fill:'#e8e3f4',stroke:'#d6cce8'}),svg('rect',{x:'77',y:'31',width:'91',height:'118',rx:'5',transform:'rotate(3 123 90)',fill:'#fff',stroke:'#cec4e4'}),svg('path',{d:'M94 53H124M94 65H147M94 74H140M94 84H148M94 115H123M94 124H142',stroke:'#b6a8cf','stroke-width':'2','stroke-linecap':'round'}),svg('rect',{x:'93',y:'96',width:'47',height:'8',rx:'2',fill:'#dce7fc'}));
    const trace=svg('g',{'class':'art-trace'});
    trace.append(svg('path',{d:'M141 100H174C191 100 187 63 213 63H273C292 63 292 105 314 105H377','class':'art-draw',pathLength:'1',stroke:'#8875c6','stroke-width':'1.4','stroke-linecap':'round'}),svg('circle',{cx:'141',cy:'100',r:'3',fill:'#7660b4'}),svg('circle',{cx:'377',cy:'105',r:'3',fill:'#7660b4'}));
    const lens=svg('g',{'class':'art-lens'});
    lens.append(svg('circle',{cx:'265',cy:'88',r:'70',fill:'url(#inquiry-glass)',stroke:'#b8a8d8','stroke-width':'1.2'}),svg('circle',{cx:'265',cy:'88',r:'59',stroke:'#fff','stroke-width':'2'}),svg('circle',{cx:'265',cy:'88',r:'46',stroke:'#ae9ad0','stroke-width':'.8','stroke-dasharray':'2 5'}),svg('path',{d:'M305 139 334 169',stroke:'#b4a2d2','stroke-width':'7','stroke-linecap':'round'}),svg('path',{d:'M305 139 334 169',stroke:'#f6f2ff','stroke-width':'3','stroke-linecap':'round'}),svg('path',{d:'M244 41A51 51 0 0 1 300 49',stroke:'#fff','stroke-width':'3','stroke-linecap':'round'}));
    const focus=svg('g',{'class':'art-focus'});
    focus.append(svg('rect',{x:'239',y:'61',width:'52',height:'52',rx:'15',fill:'#fff','fill-opacity':'.9',stroke:'#b9a9d8'}),svg('path',{d:'M258 78C258 69 273 69 273 78C273 84 265 84 265 91',stroke:'#6c55aa','stroke-width':'2.6','stroke-linecap':'round'}),svg('circle',{cx:'265',cy:'99',r:'1.7',fill:'#6c55aa'}));
    const annotation=svg('g',{'class':'art-annotation'});
    annotation.append(svg('rect',{x:'327',y:'32',width:'52',height:'25',rx:'12.5',fill:'#e9efcf',stroke:'#c9d48f'}),svg('path',{d:'M344 44 349 49 361 39',stroke:'#62703a','stroke-width':'1.5','stroke-linecap':'round','stroke-linejoin':'round'}),svg('path',{d:'M182 25V35M177 30H187',stroke:'#879d50','stroke-width':'1.4','stroke-linecap':'round'}),svg('circle',{cx:'191',cy:'133',r:'3',fill:'#a0b767'}));
    drawing.append(plane,papers,trace,lens,focus,annotation);frame.append(drawing);
    return frame;
  };
  const models=[
    {id:'gemini',name:'Gemini',label:zh?'Google · Gemini 系列':'Google · Gemini models',detail:zh?'使用已配置的 Gemini 模型开展询问练习。':'Practice audit inquiry with your configured Gemini model.'},
    {id:'zhipu',name:'GLM',label:zh?'智谱 · GLM 系列':'Zhipu · GLM models',detail:zh?'使用已配置的 GLM 模型开展询问练习。':'Practice audit inquiry with your configured GLM model.'},
    {id:'openrouter',name:'OpenRouter',label:zh?'可选 · 免费模型路由':'Optional · Free model routing',detail:zh?'使用已有的 OpenRouter 配置。':'Use your existing OpenRouter configuration.'}
  ];
  const signature=String(zh);
  if(!root._ui||root._ui.signature!==signature){
    const intro=make('div','welcome-intro'),copy=make('div','welcome-copy'),heading=make('h2','welcome-heading');
    heading.append(make('span','heading-line',zh?'循着证据，':'Follow the evidence.'),make('span','heading-line heading-emphasis',zh?'问得更深入。':'Find the next question.'));
    copy.append(make('p','welcome-eyebrow',zh?'审计询问 / 练习空间':'AUDIT INQUIRY / PRACTICE SPACE'),heading,make('p','welcome-description',zh?'选择模型服务，开启你的审计询问练习。':'Choose a provider to begin your audit inquiry practice.'));
    const art=inquiryArt();intro.append(copy,art);
    const grid=make('div','model-grid');grid.setAttribute('role','group');grid.setAttribute('aria-label',zh?'选择模型服务':'Choose a model provider');
    const cards=models.map(model=>{
      const button=make('button','model-card');button.type='button';button.dataset.provider=model.id;
      const top=make('span','model-top'),mark=make('span','model-glyph'),status=make('span','model-status');mark.append(providerMark(model.id));top.append(mark,status);
      const name=make('span','model-name',model.name),label=make('span','model-label',model.label),detail=make('span','model-detail',model.detail),action=make('span','model-action'),actionText=make('span','model-action-text'),actionIcon=actionMark();
      action.append(actionText,actionIcon.mark);button.append(top,name,label,detail,action);grid.append(button);return {button,status,actionText,actionPath:actionIcon.path,model};
    });
    root.replaceChildren(intro,grid);root._ui={signature,cards,art};
    if(!root._entered&&!reduced){
      root._entered=true;root.classList.add('welcome-entered');
      [copy,art,...cards.map(entry=>entry.button)].forEach((el,i)=>el.animate([{opacity:0,transform:'translateY(12px)'},{opacity:1,transform:'translateY(0)'}],{duration:560,delay:i*60,easing:'cubic-bezier(.2,.8,.2,1)',fill:'backwards'}));
      art.querySelectorAll('.art-draw').forEach(path=>path.animate([{strokeDasharray:'1',strokeDashoffset:'1'},{strokeDasharray:'1',strokeDashoffset:'0'}],{duration:1100,delay:180,easing:'cubic-bezier(.2,.8,.2,1)',fill:'backwards'}));
    }
  }
  const art=root._ui.art;
  art.onpointermove=e=>{if(reduced||e.pointerType==='touch')return;const rect=art.getBoundingClientRect();art.style.setProperty('--art-x',`${((e.clientX-rect.left)/rect.width-.5)*8}px`);art.style.setProperty('--art-y',`${((e.clientY-rect.top)/rect.height-.5)*6}px`);};
  art.onpointerleave=()=>{art.style.setProperty('--art-x','0px');art.style.setProperty('--art-y','0px');};
  root._ui.cards.forEach(({button,status,actionText,actionPath,model})=>{
    const selected=model.id===data.selected,ready=Boolean(data.ready?.[model.id]);
    if(selected){const rect=button.getBoundingClientRect();const registry=document[Symbol.for('inquire.publicMotion')]||(document[Symbol.for('inquire.publicMotion')]={});registry.model={left:rect.left,top:rect.top,width:rect.width,height:rect.height,title:model.name};}
    button.setAttribute('aria-pressed',String(selected));status.textContent=ready?(zh?'已配置':'Configured'):(zh?'待配置':'Set up');status.dataset.ready=String(ready);
    actionText.textContent=selected?(zh?'当前选择':'Selected'):(zh?'选择模型':'Choose model');
    actionPath.setAttribute('d',selected?'M3 8 6.5 11.5 13 5':'M4 12 12 4M4 4H12V12');
    button.onclick=()=>{
      const rect=button.getBoundingClientRect();
      const registry=document[Symbol.for('inquire.publicMotion')]||(document[Symbol.for('inquire.publicMotion')]={});
      registry.model={left:rect.left,top:rect.top,width:rect.width,height:rect.height,title:model.name};
      setTriggerValue('choose',model.id);
    };
    button.onpointermove=e=>{if(reduced||e.pointerType==='touch')return;const rect=button.getBoundingClientRect();const x=(e.clientX-rect.left)/rect.width-.5,y=(e.clientY-rect.top)/rect.height-.5;button.style.setProperty('--rx',`${-y*3}deg`);button.style.setProperty('--ry',`${x*4}deg`);button.style.setProperty('--shine-x',`${(x+.5)*100}%`);};
    button.onpointerleave=()=>{button.style.setProperty('--rx','0deg');button.style.setProperty('--ry','0deg');};
  });
}
