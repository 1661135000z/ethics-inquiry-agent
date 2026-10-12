"""Compact, local product styling. No external fonts, user HTML or keys."""
from html import escape

STYLE = '''<style>
:root{--ink:#292934;--muted:#858490;--line:#e9e8ee;--accent:#6857c8;--ease:cubic-bezier(.22,1,.36,1)}
html,body,.stApp,[data-testid="stAppViewContainer"],input,textarea,button,select,p,h1,h2,h3,label,.product-bar,.product-description,[data-testid="stText"]{font-family:"InquireSans","Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif!important}
.stApp{background:#fafafa;color:var(--ink);font-size:14px}
.block-container{max-width:1600px;padding:4.2rem 2.2rem 2rem}
[data-testid="stMain"]{scroll-padding-top:64px}
[data-testid="stVerticalBlock"]{gap:.65rem}
[data-testid="stMarkdownContainer"] p,[data-testid="stText"],label{font-size:14px;line-height:1.65}
[data-testid="stCaptionContainer"] p{font-size:12px;line-height:1.5;color:#858490}
h1,h2,h3{letter-spacing:-.025em;color:var(--ink);font-weight:600!important}h1{font-size:26px!important}h2,h3{font-size:16px!important}
[data-testid="stSidebar"]{background:#f5f4f8;border-right:1px solid var(--line)}
.product-bar{display:flex;align-items:baseline;gap:16px;border-bottom:1px solid var(--line);padding:0 0 12px;margin:0 0 18px}.product-bar h1{padding:0;margin:0;font-size:26px}.product-bar h1 span{color:var(--accent)}.product-description{font-size:12px;color:#93909e}
.stButton button,.stDownloadButton button,[data-testid="stPopover"] button{min-height:34px;padding:5px 12px;border-radius:8px;font-size:13px;transition:background .18s,border-color .18s,box-shadow .18s,transform .18s var(--ease)}
.stButton button p,.stDownloadButton button p{font-size:13px}.stButton button:hover{border-color:#a89ad7;box-shadow:0 3px 8px #3c305909}.stButton button:active{transform:scale(.985)}
.st-key-model_entry{position:relative;border:1px solid var(--line);border-radius:10px;background:#fff;padding:10px 12px;margin:0 0 8px;display:flex;flex-direction:row!important;align-items:center;flex-wrap:wrap;gap:8px 14px!important}
.st-key-model_entry>.stElementContainer{width:auto!important;flex:0 1 auto}.st-key-model_entry [data-testid="stCaptionContainer"]{max-width:100%}.st-key-model_entry .stButton button[kind="primary"]{background:#6857c8;border-color:#6857c8}
[data-testid="stPopoverBody"]{font-family:"InquireSans",sans-serif;max-width:min(480px,calc(100vw - 32px));padding:16px}
.st-key-own_scenario button{min-height:34px;border:1px solid #e0daef;background:#fff!important;color:#655794!important;justify-content:flex-start;padding-left:12px;text-align:left}.st-key-own_scenario button[kind="primary"]{border-color:#b5a7dd;background:#f6f3ff!important}
.st-key-inquiry_actions [data-testid="stHorizontalBlock"]{gap:8px!important}.st-key-inquiry_actions button{font-size:12px;background:#fff}
[data-testid="stTextArea"] textarea{font-size:14px;line-height:1.65;background:white;border-radius:10px;padding:10px 12px}
[data-testid="stForm"]{border:none;padding:0;margin-top:0;background:none}
[data-testid="stCheckbox"] label p{font-size:12px;color:#817d8c;line-height:1.5}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:18px;border-bottom:1px solid var(--line)}[data-testid="stTabs"] button p{font-size:13px;font-weight:500}
[data-testid="stChatMessage"]{background:white;border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:5px}
[data-testid="stExpander"]{border-color:var(--line);border-radius:9px}[data-testid="stExpander"] summary p{font-size:12px}
.st-key-journey_rail{position:sticky;top:72px;border-left:1px solid var(--line);padding:4px 0 8px 12px;max-width:270px}
[data-testid="stHorizontalBlock"]:has(.st-key-journey_rail){flex-wrap:nowrap!important;gap:26px!important}
[data-testid="stHorizontalBlock"]:has(.st-key-journey_rail)>[data-testid="stColumn"]:first-child{flex:1 1 0!important;min-width:0!important}
[data-testid="stHorizontalBlock"]:has(.st-key-journey_rail)>[data-testid="stColumn"]:last-child{flex:0 0 260px!important;width:260px!important;min-width:260px!important;position:sticky;top:72px;align-self:flex-start}
.st-key-journey_rail{position:static}
.workflow-panel{padding:4px 0}.flow-heading{display:flex;justify-content:space-between;font-size:11px;color:#898491;margin:0 0 10px}.flow-status{color:#6c6099}.flow-track{display:flex;gap:12px;flex-wrap:wrap}.flow-step{display:flex;align-items:center;gap:5px;font-size:11px;color:#aaa5b1}.flow-step .marker{font-size:10px}.flow-step strong{font-size:11px;font-weight:500}.flow-step small{display:none}.flow-step.complete{color:#528569}.flow-step.active{color:#6857c8}.flow-step.active .marker{animation:workPulse 1.5s ease-in-out infinite}.flow-step.failed{color:#b25454}
@keyframes workPulse{50%{opacity:.4}}
@media(min-width:1000px){.st-key-conversation_region{margin-top:4px}}
@media(max-width:999px){.block-container{padding:3.8rem 1.1rem 1rem}.st-key-journey_rail{position:static;border-left:none;border-bottom:1px solid var(--line);padding:0 0 8px;max-width:none}[data-testid="stHorizontalBlock"]:has(.st-key-journey_rail){flex-direction:column-reverse;gap:12px!important}[data-testid="stHorizontalBlock"]:has(.st-key-journey_rail)>[data-testid="stColumn"]:first-child,[data-testid="stHorizontalBlock"]:has(.st-key-journey_rail)>[data-testid="stColumn"]:last-child{width:100%!important;flex:0 1 auto!important;min-width:0!important;position:static!important}}
@media(max-width:600px){.block-container{padding:3.6rem 1rem 1rem}.product-bar{gap:9px;padding-bottom:9px;margin-bottom:12px}.product-description{font-size:11px}.st-key-model_entry{gap:6px 9px!important;padding:8px 10px}.st-key-model_entry [data-testid="stCaptionContainer"] p{font-size:11px;overflow-wrap:anywhere}[data-testid="stHorizontalBlock"]{gap:10px}}

/* The welcome view is expressive; the workbench stays compact. */
.st-key-welcome_workspace{max-width:920px;margin:0 auto;padding:22px 16px 28px}
.st-key-welcome_workspace .st-key-model_entry{max-width:760px;margin:8px auto 0;background:#ffffffc9;border:1px solid #e3dfef;border-radius:16px;padding:16px 20px;box-shadow:0 10px 40px #3b265a06}
.st-key-welcome_workspace .st-key-model_entry>.stElementContainer{max-width:100%}
.st-key-model_entry{box-shadow:0 3px 16px #35255104}
.st-key-model_entry [data-testid="stCaptionContainer"] p{overflow-wrap:anywhere}
.current-situation{display:flex;gap:12px;align-items:center;padding:12px 16px;border:1px solid #e6e0f2;border-radius:12px;background:linear-gradient(100deg,#f4f0ff,#fcfbff);margin:2px 0 8px}
.current-situation span{font-size:10px;letter-spacing:.06em;color:#8e82ac}.current-situation strong{font-size:14px;color:#534378;font-weight:550}
.st-key-chat_tools{display:flex;flex-direction:row!important;gap:8px!important;align-items:center;flex-wrap:wrap}
.st-key-chat_tools>.stElementContainer{width:auto!important;flex:0 1 auto}
.st-key-chat_tools button{font-size:12px;min-height:30px;background:#faf9fc;border-color:#ebe6f3}
.st-key-transcript [data-testid="stChatMessage"]{background:linear-gradient(120deg,#ffffff,#fcfbff);box-shadow:0 3px 12px #47327304;border-color:#e9e4ef}
[data-testid="stTextArea"] textarea:focus{box-shadow:0 0 0 3px #6857c811;border-color:#a99acb}
[data-testid="stBaseButton-primary"]{background:#6857c8!important;border-color:#6857c8!important}
[data-testid="stAlert"]{border-radius:10px}
@media(min-width:1600px){.block-container{max-width:1700px;padding-left:3rem;padding-right:3rem}}
@media(max-width:600px){.st-key-welcome_workspace{padding:6px 0 12px}.st-key-welcome_workspace .st-key-model_entry{padding:12px;gap:8px!important}.current-situation{flex-direction:column;align-items:flex-start;gap:4px;padding:10px 12px}.st-key-chat_tools button p{font-size:11px}}

@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>'''

def relay_html(stage='idle', zh=False, failed=False):
    names=['输入检查','模型追问','输出校验','保存结果'] if zh else ['Check input','Ask model','Validate output','Save result']
    descriptions=['读取情境与上下文','请求下一条伦理问题','检查结构与引用','保留本会话探究记录'] if zh else ['Read situation and context','Request the next ethical question','Check structure and quotations','Keep this session’s inquiry record']
    stages=['input','request','validate','save']
    current=stages.index(stage) if stage in stages else 4 if stage=='done' else -1
    status=('需要处理错误' if zh else 'Needs attention') if failed else ('已完成本轮' if zh else 'Turn complete') if stage=='done' else ('等待输入' if zh else 'Waiting for input') if stage=='idle' else ('正在执行' if zh else 'In progress')
    nodes=[]
    for i,label in enumerate(names):
        state='complete' if i<current else ('failed' if failed else 'active') if i==current else ''
        marker='✓' if state=='complete' else '!' if state=='failed' else f'{i+1:02}'
        nodes.append(f'<div class="flow-step {state}"><span class="marker">{marker}</span><strong>{label}</strong><small>{descriptions[i]}</small></div>')
    return f'<div class="workflow-panel" role="status" aria-live="polite"><div class="flow-heading"><span class="flow-status">{status}</span></div><div class="flow-track">'+''.join(nodes)+'</div></div>'
