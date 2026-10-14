import {useEffect,useLayoutEffect,useReducer,useRef,useState} from 'react';
import {flushSync} from 'react-dom';
import gsap from 'gsap';
import {Icon} from './Icon';
import {SituationStudio} from './SituationStudio';
import {enter,morph,reduced} from './motion';
import {initialState,reducer,restoreState,publicSnapshot,type Snapshot} from './state';
import {json,inquiry,type Config,type Provider,type Case} from './api';
import staticCases from './cases.json';

const fallback:Config={providers:[{id:'gemini',models:['gemini-3.5-flash-lite','gemini-3.1-flash-lite','gemini-2.5-flash-lite','gemini-2.5-flash'],configured:false,free_confirmed:false},{id:'zhipu',models:['glm-4.7-flash'],configured:false,free_confirmed:false},{id:'openrouter',models:['openrouter/free'],configured:false,free_confirmed:false}],cases:staticCases,principle:'objectivity'};
const names:Record<string,string>={gemini:'Gemini',zhipu:'GLM',openrouter:'OpenRouter'};
const focusNames:Record<string,string>={scope:'探究范围',role:'角色与判断',interests:'关系与利益',pressure:'压力与激励',evidence:'证据与解释',review:'独立复核'};

export default function App(){
 const [state,dispatch]=useReducer(reducer,null,()=>{try{return restoreState(sessionStorage.getItem('inquire.workspace.v1'))}catch{return initialState()}});
 const [config,setConfig]=useState<Config>(fallback);
 const [configLoading,setConfigLoading]=useState(true),[configError,setConfigError]=useState('');
 const [settings,setSettings]=useState(false),[selected,setSelected]=useState<string|null>(null),[connecting,setConnecting]=useState(false),[connectionError,setConnectionError]=useState('');
 const [keys,setKeys]=useState<Record<string,string>>({}),[access,setAccess]=useState(''),[free,setFree]=useState<Record<string,boolean>>({}),[consent,setConsent]=useState(false);
 const [credentialModes,setCredentialModes]=useState<Record<string,'developer'|'personal'>>({});
 const [preview,setPreview]=useState<string|null>(null),[copyStatus,setCopyStatus]=useState(-1),[ready,setReady]=useState(false),[transitioning,setTransitioning]=useState(false),[recoveryError,setRecoveryError]=useState('');
 const [resetting,setResetting]=useState(false);
 const container=useRef<HTMLDivElement>(null),badge=useRef<HTMLButtonElement>(null),caseTitle=useRef<HTMLHeadingElement>(null),composer=useRef<HTMLTextAreaElement>(null),controller=useRef<AbortController|null>(null),closePreview=useRef<number|undefined>(undefined),newest=useRef<HTMLDivElement>(null);
 const zh=state.language==='中文',t=(cn:string,en:string)=>zh?cn:en;
 const p=config.providers.find(p=>p.id===state.provider)||fallback.providers[0];
 const credentialMode=credentialModes[state.provider]||(keys[state.provider]?.trim()?'personal':p.configured?'developer':'personal');
 const messages=state.snapshot.session.messages, busy=!!state.activeRequest;
 const locked=busy||resetting||connecting||transitioning;
 useEffect(()=>{
  let alive=true;
  json<Config>('/api/config').then(c=>{if(alive){setConfig(c);setConfigError('')}}).catch(()=>{if(alive)setConfigError('无法读取后台模型配置。请重试；你的对话不会被清除。')}).finally(()=>{if(alive)setConfigLoading(false)});
  json<Snapshot>('/api/session',{}).then(s=>{if(alive){dispatch({type:'RESTORE',snapshot:s});setReady(true)}}).catch(e=>{if(alive)setRecoveryError(e.message)});
  return()=>{alive=false};
 },[]);
 async function reloadConfiguration(){
  if(configLoading)return;setConfigLoading(true);setConfigError('');
  try{setConfig(await json<Config>('/api/config'))}catch{setConfigError('无法读取后台模型配置。请重试；你的对话不会被清除。')}finally{setConfigLoading(false)}
 }
 useEffect(()=>{try{sessionStorage.setItem('inquire.workspace.v1',JSON.stringify(publicSnapshot(state)))}catch{};document.documentElement.dataset.theme=state.theme;document.documentElement.lang=zh?'zh-CN':'en'},[state,zh]);
 useLayoutEffect(()=>enter(container.current),[state.screen]);
 useLayoutEffect(()=>{
  if(!newest.current||!messages.length)return;
  if(!reduced())gsap.fromTo(newest.current,{opacity:0,y:10},{opacity:1,y:0,duration:.35,ease:'power2.out'});
  newest.current.scrollIntoView({behavior:reduced()?'instant':'smooth',block:'nearest'});
 },[messages.length,state.snapshot.version]);
 useEffect(()=>()=>{controller.current?.abort();window.clearTimeout(closePreview.current)},[]);

 function chooseProvider(provider:Provider){
  if(locked)return;
  dispatch({type:'MODEL',provider:provider.id,model:provider.default_model||provider.models[0]});setSelected(provider.id);setConnectionError('');setConsent(false);
  if(state.screen!=='welcome')setSettings(true);
 }
 function credentials(){return {provider:state.provider,model:state.model,api_key:credentialMode==='personal'?keys[state.provider]||'':'',free_confirmed:free[state.provider]===true,access_code:credentialMode==='developer'?access:'',language:state.language}}
 async function connect(){
  if(locked)return;setConnecting(true);setConnectionError('');
  try{
   if(credentialMode==='developer'&&!access){throw new Error(t('请输入你在后台 ACCESS_CODE 中设置的值，不是模型 API Key。','Enter the value you set for ACCESS_CODE, not a model API key.'))}
   if(credentialMode==='personal'&&!keys[state.provider]?.trim()){throw new Error(t('请输入所选模型服务的 API Key。','Enter the selected provider’s API key.'))}
   await json('/api/connect',credentials());
   setSettings(false);setConsent(false);
   if(state.screen==='welcome'){
    setTransitioning(true);
    const card=document.querySelector(`[data-model="${state.provider}"]`) as HTMLElement;
    await morph(card,badge.current,()=>flushSync(()=>dispatch({type:'CONFIRM'})));
    setTransitioning(false);
   }else dispatch({type:'CONFIRM'});
  }catch(e){setConnectionError(e instanceof Error?e.message:'连接未完成。')}
  finally{setConnecting(false)}
 }
 async function send(operation:'submit'|'switch'|'regenerate'='submit'){
  if(locked||!ready||!state.verified||!consent)return;
  const id=crypto.randomUUID(),abort=new AbortController();controller.current=abort;
  dispatch({type:'REQUEST',id});
  const source=document.querySelector(`[data-case="${state.caseId}"]`) as HTMLElement;
  try{
   const snapshot=await inquiry({...credentials(),text:state.draft,case_id:state.caseId,consent,version:state.snapshot.version,request_id:id,operation},abort.signal,stage=>dispatch({type:'STAGE',id,stage}));
   const complete=()=>flushSync(()=>dispatch({type:'COMPLETE',id,snapshot,preserveDraft:operation==='regenerate'}));
   if(state.screen==='cases'){
    setTransitioning(true);
    // A persistent top-level heading is the target across the scene change.
    await morph(source,caseTitle.current,complete);setTransitioning(false);
   }else complete();
  }catch(e){dispatch({type:'FAIL',id,message:e instanceof Error?e.message:'请求未完成。'})}
  finally{controller.current=null}
 }
 async function recover(){
  if(locked)return;
  try{const snapshot=await json<Snapshot>('/api/session',{});dispatch({type:'RESTORE',snapshot});setReady(true);setRecoveryError('')}catch(e){setRecoveryError(e instanceof Error?e.message:'恢复失败。')}
 }
 async function restart(){
  if(locked)return;setResetting(true);
  try{const snapshot=await json<Snapshot>('/api/session',{new:true});dispatch({type:'NEW',snapshot});setConsent(false);setPreview(null)}catch(e){setRecoveryError(e instanceof Error?e.message:'新会话创建失败。')}
  finally{setResetting(false)}
 }
 function beginSelection(){if(locked)return;dispatch({type:'SELECT_AGAIN'});setConsent(false)}
 function selectCase(c:Case){if(locked)return;dispatch({type:'CASE',id:c.id,text:zh?c.text_zh:c.text_en});setPreview(null);composer.current?.focus()}
 function reveal(id:string){window.clearTimeout(closePreview.current);setPreview(id)}
 function hide(){closePreview.current=window.setTimeout(()=>setPreview(null),120)}
 function tilt(e:React.PointerEvent<HTMLElement>){if(e.pointerType!=='mouse'||reduced())return;const b=e.currentTarget.getBoundingClientRect();e.currentTarget.style.setProperty('--rx',`${-(e.clientY-b.top-b.height/2)/b.height*5}deg`);e.currentTarget.style.setProperty('--ry',`${(e.clientX-b.left-b.width/2)/b.width*5}deg`);e.currentTarget.style.setProperty('--mx',`${e.clientX-b.left}px`);e.currentTarget.style.setProperty('--my',`${e.clientY-b.top}px`)}
 function resetTilt(e:React.PointerEvent<HTMLElement>){e.currentTarget.style.setProperty('--rx','0deg');e.currentTarget.style.setProperty('--ry','0deg')}
 async function copy(text:string,index:number){try{await navigator.clipboard.writeText(text);setCopyStatus(index);setTimeout(()=>setCopyStatus(-1),1600)}catch{dispatch({type:'FAIL',id:state.activeRequest||'',message:'复制不可用，请选中文字复制。'})}}
 const currentCase=config.cases.find(c=>c.id===(messages.length?state.snapshot.case_id:state.caseId));
 const title=currentCase?.id!=='blank'&&currentCase?(zh?currentCase.zh:currentCase.en).replace(/^(Example · |Fictional · |示例 · |新编虚构 · )/,''):t('你的探究情境','Your inquiry');

 const modelForm=<div className="model-form" data-enter>
  <div className="form-head"><div><span className="micro">{names[state.provider]} / CONNECTION</span><h3>{t('连接你的模型','Connect your model')}</h3></div><span className="status-dot"/>
  </div>
  {p.configured&&<div className="credential-choice" role="group" aria-label={t('连接方式','Connection method')}>{(['developer','personal'] as const).map(mode=><button key={mode} aria-pressed={credentialMode===mode} className={credentialMode===mode?'active':''} disabled={locked} onClick={()=>{setCredentialModes({...credentialModes,[state.provider]:mode});dispatch({type:'MODEL',provider:state.provider,model:state.model});setConsent(false);setConnectionError('')}}>{mode==='developer'?t('使用后台配置','Use saved configuration'):t('使用自己的密钥','Use my own API key')}</button>)}</div>}
  <div className="form-fields"><label>{t('模型','Model')}<select value={state.model} onChange={e=>{dispatch({type:'MODEL',provider:state.provider,model:e.target.value});setConnectionError('')}} disabled={locked}>{p.models.map(m=><option key={m}>{m}</option>)}</select></label>
  {credentialMode==='personal'?<label>API Key <span>{t('所选模型服务的密钥 · 仅当前页面使用','Provider key · this page only')}</span><input type="password" value={keys[state.provider]||''} autoComplete="off" spellCheck={false} maxLength={512} onChange={e=>{setKeys({...keys,[state.provider]:e.target.value});dispatch({type:'MODEL',provider:state.provider,model:state.model});setConsent(false);setConnectionError('')}} placeholder={t('输入此平台的 API Key','Enter this provider’s API key')} disabled={locked}/></label>:
   <label>{t('开发者访问码','Developer access code')}<span>{t('后台 ACCESS_CODE 的值，不是 API Key','The ACCESS_CODE value, not an API key')}</span><input type="password" value={access} onChange={e=>{setAccess(e.target.value);dispatch({type:'MODEL',provider:state.provider,model:state.model});setConsent(false);setConnectionError('')}} autoComplete="off" placeholder={t('输入你设置的 ACCESS_CODE','Enter your ACCESS_CODE')} disabled={locked}/></label>}</div>
  {credentialMode==='personal'&&<label className="check"><input type="checkbox" checked={free[state.provider]||false} onChange={e=>setFree({...free,[state.provider]:e.target.checked})}/>{t('确认此账户与模型具备免费档资格','This account and model are eligible for the free tier')}</label>}
  <div className="form-actions"><p>{t('连接测试只发送一个虚构情境，不改变你的对话。','The connection test sends a fictional situation and leaves your inquiry unchanged.')}</p><button className="primary" onClick={connect} disabled={connecting||transitioning}>{connecting?<><span className="processing"/>{t('正在连接','Connecting')}</>:<>{t('测试连接并继续','Test connection & continue')}<Icon name="arrow"/></>}</button></div>
  {connectionError&&<div className="error" role="alert">{connectionError}<button onClick={()=>chooseProvider(config.providers.find(p=>p.id===(state.provider==='gemini'?'zhipu':'gemini'))!)}>{t('切换模型服务','Switch provider')}<Icon name="arrow" size={14}/></button></div>}
 </div>;

 const composerSurface=<div className="composer-surface" data-enter>
     <div className="composer-head"><strong>{state.screen==='cases'?t('描述你的情境','Describe the situation'):t('继续回答','Continue your inquiry')}</strong><span>{state.draft.length}/4,000</span></div>
     {state.screen==='chat'&&!state.draft&&<div className="starters">{[t('我掌握的信息是……','What I know is…'),t('我还不能确定……','I am not yet sure…'),t('可以核对的资料是……','The records I could check are…')].map(text=><button key={text} onClick={()=>{dispatch({type:'DRAFT',text});composer.current?.focus()}} disabled={locked}>{text}</button>)}</div>}
     <textarea ref={composer} aria-label={t('情境或追问回答','Situation or follow-up answer')} value={state.draft} onChange={e=>dispatch({type:'DRAFT',text:e.target.value})} placeholder={state.screen==='cases'?t('描述需要作出的判断，以及你掌握的信息或疑虑。','Describe the decision, what you know, and what concerns you.'):t('说说你知道什么，以及仍有哪些不确定。','Share what you know and what remains uncertain.')} maxLength={4000} disabled={locked} onKeyDown={e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();send(state.selecting?'switch':'submit')}}}/>
     {state.error&&<div className="error" role="alert">{state.error}<button onClick={recover}>{t('恢复已保存对话','Restore saved inquiry')}</button></div>}
     {!state.verified&&<button className="connection-needed" onClick={()=>setSettings(true)}>{t('确认模型连接后继续，原对话保持不变。','Confirm a model connection to continue; your inquiry is preserved.')}<Icon name="arrow" size={14}/></button>}
     <div className="composer-footer"><label className="check"><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)} disabled={locked}/>{t('仅发送虚构或匿名内容至所选服务','Send fictional or anonymized content to the selected service')}</label><button className="primary send" onClick={()=>send(state.selecting?'switch':'submit')} disabled={locked||!state.verified||!state.draft.trim()||!consent||!ready||transitioning}>{busy?<><span className="processing"/>{t('正在探究','Processing')}</>:<>{state.screen==='cases'?(state.selecting?t('以此开始新对话','Begin a new inquiry'):t('开始探究','Begin inquiry')):t('发送回答','Send answer')}<span className="arrow-island"><Icon name="arrow" size={16}/></span></>}</button></div>
     <details className="execution" open={!!state.error||busy}><summary><span className={busy?'live-dot':''}/>{busy?t('正在执行','Working'):t('执行详情','Execution details')}<span>{t('只展示真实处理阶段','Actual execution stages only')}</span></summary><ol>{['input','request','validate','commit'].map((stage,i)=><li className={state.stage===stage?'active':state.stage==='done'?'done':''} key={stage}><span>{state.stage==='done'?<Icon name="check" size={12}/>:String(i+1).padStart(2,'0')}</span>{[t('检查输入','Check input'),t('请求模型','Request model'),t('校验追问与引用','Validate question & quotes'),t('提交会话记录','Commit inquiry')][i]}</li>)}</ol></details>
    </div>;

 return <div className={`app ${state.screen==='welcome'?'is-welcome':state.screen==='cases'?'is-studio':'is-chat'}`} ref={container}>
  <div className="ambient" aria-hidden="true"><svg viewBox="0 0 1200 800"><path d="M-80 660C200 660 360 340 600 340S1000 660 1280 660"/><path d="M-80 630C200 630 360 300 600 300S1000 630 1280 630"/><path d="M-80 600C200 600 360 260 600 260S1000 600 1280 600"/></svg></div>
  <header className="topbar"><a className="brand" href="#" onClick={e=>e.preventDefault()} aria-label="Inquire"><span className="brand-mark"><i/><i/><i/></span>inquire<span className="brand-period">.</span></a>
   <button ref={badge} className={`model-badge ${!state.onboarded?'concealed':''}`} onClick={()=>{setSettings(v=>!v);setSelected(state.provider)}} disabled={locked}><span className="status-dot"/>{names[state.provider]}<span className="badge-model">{state.model}</span><Icon name="settings" size={15}/></button>
   <div className="top-actions"><button className="text-button language" onClick={()=>dispatch({type:'LANGUAGE',language:zh?'English':'中文'})}>{zh?'EN':'中文'}</button><button className="icon-button" aria-label={state.theme==='dark'?'切换浅色模式':'切换深色模式'} onClick={()=>dispatch({type:'THEME',theme:state.theme==='dark'?'light':'dark'})}><Icon name={state.theme==='dark'?'sun':'moon'}/></button></div>
  </header>
  {config.test_mode&&<div className="test-banner">{t('本地测试演示 · 使用明确标注的模拟回复，不是实时模型','Local test fixture · simulated replies, not a live model')}</div>}
  {configError&&<div className="error" role="alert">{t(configError,'Could not load saved model configuration. Retry without clearing your inquiry.')}<button onClick={reloadConfiguration} disabled={configLoading}>{t('重试配置','Retry configuration')}</button></div>}
  {state.screen==='welcome'?<main className="welcome">
   <div className="welcome-copy" data-enter><span className="eyebrow"><span className="fine-line"/>{t('一个更好的问题，始于探究','A better question starts with inquiry')}</span><h1>{t('判断之前，','Before judgment,')}<br/><span>{t('先问清楚。','ask a better question.')}</span></h1><p>{t('选择一个模型，展开你的伦理情境。','Choose a model. Open your ethical inquiry.')}</p></div>
   <div className={`models ${selected?'has-selection':''}`}>
    {config.providers.filter(p=>p.id!=='openrouter').map((provider,i)=><article key={provider.id} data-model={provider.id} data-enter className={`model-card ${selected===provider.id?'selected':''}`} onPointerMove={tilt} onPointerLeave={resetTilt}>
     <div className="card-bezel"><button className="model-main" onClick={()=>chooseProvider(provider)} disabled={connecting||transitioning||configLoading} aria-expanded={selected===provider.id}><div className="card-top"><span className="provider-symbol">{provider.id==='gemini'?<Icon name="spark" size={30}/>:<span className="glm-symbol"><i/><i/><i/></span>}</span><span className="model-availability">{configLoading?t('正在读取配置','Loading configuration'):provider.configured?t('开发者配置可用','Developer configured'):t('使用自己的密钥','Bring your own key')}</span></div><div className="provider-title">{names[provider.id]}<span>0{i+1}</span></div><p>{provider.id==='gemini'?t('Google 的语言模型','Google language models'):t('智谱 · 国内模型服务','Zhipu · domestic model service')}</p><div className="model-cta"><span>{selected===provider.id?t('正在配置','Configure connection'):t('选择并连接','Choose & connect')}</span><span className="arrow-island"><Icon name="arrow"/></span></div></button></div>
    </article>)}
   </div>
   {selected&&modelForm}
   <p className="welcome-boundary" data-enter>{t('专注客观性 · 通过持续追问帮助你思考，判断由人作出。','Focused on objectivity · inquiry supports thought; judgment stays human.')}</p>
   <button className="text-button optional-provider" onClick={()=>chooseProvider(config.providers.find(p=>p.id==='openrouter')||fallback.providers[2])} disabled={connecting}>{t('其他免费服务 · OpenRouter','Other free providers · OpenRouter')}</button>
  </main>:<main className="workspace">
   <section className="working-area">
    {settings&&<div className="settings-surface"><div className="settings-toolbar"><div className="segment">{config.providers.map(pr=><button key={pr.id} className={pr.id===state.provider?'active':''} onClick={()=>chooseProvider(pr)} disabled={connecting}>{names[pr.id]}</button>)}</div><button className="icon-button" aria-label="关闭模型设置" onClick={()=>setSettings(false)}><Icon name="close"/></button></div>{modelForm}</div>}
    <div className="workspace-heading" data-enter><div><span className="eyebrow">{state.screen==='cases'?t('展开你的探究','Open your inquiry'):t('持续探究','An ongoing inquiry')}</span><h2 ref={caseTitle}>{state.screen==='cases'?<>{t('每个判断，','Every judgment,')}<br/><span>{t('都从情境开始。','begins with context.')}</span></>:title}</h2></div>{messages.length>0&&<div className="conversation-actions"><button className="secondary" onClick={beginSelection} disabled={locked}><Icon name="folder"/>{t('重新选择情境','Choose another')}</button><button className="secondary" onClick={restart} disabled={locked}><Icon name="plus"/>{t('新对话','New inquiry')}</button></div>}</div>
    {recoveryError&&<div className="error" role="alert">{recoveryError}<button onClick={recover}>{t('恢复连接','Restore connection')}</button></div>}
    {state.screen==='cases'?<div className="case-scene">
     {state.selecting&&<div className="selection-notice">{t('当前对话保留，新的情境通过首轮回复校验后才会替换。','Your current inquiry stays until the new situation receives a valid response.')}<button disabled={locked} onClick={()=>dispatch({type:'CANCEL_SELECT'})}>{t('取消切换','Cancel')}</button></div>}
     <SituationStudio cases={config.cases.filter(c=>c.id!=='blank')} zh={zh} selected={state.caseId} preview={preview} locked={locked} onSelect={selectCase} onCustom={()=>{dispatch({type:'CASE',id:'blank',text:''});composer.current?.focus()}} reveal={reveal} hide={hide} toggle={id=>setPreview(preview===id?null:id)}>{composerSurface}</SituationStudio>
    </div>:<>
     <nav className="work-tabs" aria-label={t('探究内容','Inquiry views')}>{(['chat','notes','review'] as const).map((view,i)=><button key={view} className={state.view===view?'active':''} onClick={()=>dispatch({type:'VIEW',view})}>{[t('对话','Conversation'),t('用户陈述','Reported statements'),t('人工复核','Human review')][i]}{view==='notes'&&<span>{state.snapshot.session.observations.length}</span>}</button>)}</nav>
     {state.view==='chat'?<div className="transcript">{messages.map((m,i)=><div key={`${i}-${m.content}`} ref={i===messages.length-1?newest:undefined} className={`message ${m.role}`}><div className="message-marker">{m.role==='assistant'?<span className="brand-mark"><i/><i/><i/></span>:<span>{t('你','You')}</span>}</div><div className="message-body"><span className="message-author">{m.role==='assistant'?'Inquire':t('用户陈述','Your statement')}<small>{String(Math.floor(i/2)+1).padStart(2,'0')}</small></span><p>{m.content}</p>{m.role==='assistant'&&<div className="reply-tools"><button onClick={()=>copy(m.content,i)}><Icon name={copyStatus===i?'check':'copy'} size={14}/>{copyStatus===i?t('已复制','Copied'):t('复制','Copy')}</button>{i===messages.length-1&&<button onClick={()=>send('regenerate')} disabled={locked||!state.verified||!consent}><Icon name="refresh" size={14}/>{t('重新生成','Regenerate')}</button>}</div>}</div></div>)}</div>:state.view==='notes'?<div className="notes-grid">{Object.entries(focusNames).filter(([area])=>area!=='scope').map(([area,label])=><article key={area}><span className="micro">{area}</span><h3>{zh?label:area}</h3>{state.snapshot.session.observations.filter(o=>o.area===area).length?state.snapshot.session.observations.filter(o=>o.area===area).map((o,i)=><blockquote key={i}>{o.quote}<cite>{t('来自用户第','User turn ')}{messages.filter(m=>m.role==='user').findIndex(m=>m.content.includes(o.quote))+1}{zh?'轮':''}</cite></blockquote>):<p className="muted">{t('尚未提取相关陈述，不代表相关事实不存在。','No statement extracted; this does not show the issue is absent.')}</p>}</article>)}</div>:<div className="review-surface"><Icon name="note" size={32}/><h3>{t('为人工判断整理资料','Prepare for human review')}</h3><p>{t('保留原话、未知事项与模型来源。所有陈述均来自用户，尚未核实；简报不构成伦理许可或审计结论。','Preserve quotations, uncertainties and model provenance. Statements are user-reported and unverified; the briefing is not ethical clearance or an audit conclusion.')}</p><a className={`primary ${messages.filter(m=>m.role==='user').length<2?'disabled':''}`} href={`/api/review?language=${encodeURIComponent(state.language)}`} aria-disabled={messages.filter(m=>m.role==='user').length<2} onClick={e=>{if(messages.filter(m=>m.role==='user').length<2)e.preventDefault()}}><Icon name="export"/>{t('下载人工复核简报','Download review packet')}</a><small>{t('完成至少两轮后可生成，无需额外模型调用。','Available after two turns, without an additional model call.')}</small></div>}
    </>}
    {state.screen==='chat'&&state.view==='chat'&&composerSurface}
   </section>
   <aside className="journey" aria-label={t('探究流程','Inquiry journey')} data-enter><span className="micro">{t('你的探究','Your journey')}</span><ol>{[t('选择模型','Choose model'),t('展开情境','Open situation'),t('持续对话','Continue inquiry')].map((label,i)=>{const done=i===0?state.onboarded:i===1?messages.length>0:false;const active=i===(!state.verified?0:state.screen==='cases'?1:2);return <li key={i} className={`${done?'complete':''} ${active?'current':''}`}><button disabled={locked||(i===2&&!messages.length)} onClick={()=>{if(i===0)setSettings(true);if(i===1&&messages.length)beginSelection();if(i===2&&state.selecting)dispatch({type:'CANCEL_SELECT'})}}><span className="journey-node">{done?<Icon name="check" size={16}/>:String(i+1).padStart(2,'0')}</span><span><strong>{label}</strong><small>{i===0?names[state.provider]:i===1?(messages.length?title:t('示例或你的情境','Example or your own')):messages.length?t(`已接受 ${Math.floor(messages.length/2)} 轮` ,`${Math.floor(messages.length/2)} accepted turns`):t('追问而非裁决','Inquiry, not a verdict')}</small></span>{active&&<span className="live-dot"/>}</button></li>})}</ol><div className="journey-foot"><span>{t('客观性','Objectivity')}</span><p>{t('保留未知，核对证据。判断由人作出。','Preserve uncertainty. Verify evidence. Judgment stays human.')}</p>{messages.length>0&&<a className="text-button" href={`/api/export?language=${encodeURIComponent(state.language)}`}><Icon name="export" size={15}/>{t('导出对话','Export inquiry')}</a>}<small>{state.snapshot.attempts}/24 {t('请求尝试','request attempts')}</small></div></aside>
  </main>}
  <footer><span>Inquire / {t('伦理探究','Ethics inquiry')}</span><span>{t('信息不足，是继续提问的起点。','Uncertainty is a starting point for the next question.')}</span></footer>
 </div>;
}
