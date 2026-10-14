"""Compact, local product styling. No external fonts, user HTML or keys."""
from html import escape
from pathlib import Path

STYLE = '''<style>
:root{--ink:#292934;--muted:#858490;--line:#e9e8ee;--accent:#6857c8;--ease:cubic-bezier(.22,1,.36,1)}
html,body,.stApp,[data-testid="stAppViewContainer"],input,textarea,button,select,p,h1,h2,h3,label,.product-bar,.product-description,[data-testid="stText"]{font-family:"InquireSans","Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif!important}
.stApp{background:#f8f9fc;color:var(--ink);font-size:14px}
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
.st-key-welcome_workspace{max-width:940px;margin:0 auto;padding:6px 16px 16px}
.st-key-welcome_workspace .st-key-model_entry{max-width:760px;margin:2px auto 0;background:#ffffffc9;border:1px solid #e3dfef;border-radius:16px;padding:12px 16px;box-shadow:0 10px 40px #3b265a06}
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


/* A consistent, quiet workbench vocabulary. */
.product-bar{margin-bottom:14px}.product-description{letter-spacing:.005em}
.st-key-model_entry{border-color:#e3e4ee;border-radius:12px;background:#ffffffec}
.st-key-conversation_region:focus,.st-key-scenario_region:focus,.st-key-composer:focus{outline:none}.section-heading{display:flex;align-items:center;gap:10px;margin:0 0 3px}.section-heading>span{font-size:10px;color:#9290ac;font-variant-numeric:tabular-nums}.section-heading h2{font-size:16px;margin:0;padding:0;color:#33364b;font-weight:550!important}
.st-key-own_scenario button{background:linear-gradient(110deg,#ffffff,#f6f7fd)!important;border-color:#e1e3ef;color:#514e79!important;min-height:38px;border-radius:9px}
.st-key-own_scenario button[kind="primary"]{border-color:#b4abd4;background:#f3f1fa!important}
.current-situation{border-color:#e2e3ef;background:linear-gradient(100deg,#f3f2f9,#f8f9fd);padding:10px 14px;border-radius:10px}.current-situation span{color:#9692ad}.current-situation strong{font-weight:550}
.inquiry-lens{display:flex;gap:10px;align-items:center;padding:10px 12px;margin:2px 0 5px;background:#f6f7fb;border:1px solid #e6e7f0;border-radius:10px}.lens-dot{flex:none;width:7px;height:7px;border-radius:50%;background:#799188;box-shadow:0 0 0 4px #7991880b}.lens-eyebrow{font-size:9px;letter-spacing:.06em;color:#838aa0;margin-right:8px}.inquiry-lens strong{font-size:12px;font-weight:600;color:#4b5070}.inquiry-lens p{font-size:11px;line-height:1.5;color:#8b8fa1;margin:4px 0 0}
.st-key-composer{padding:12px 14px;background:#fff;border:1px solid #dedeea;border-radius:13px;box-shadow:0 5px 20px #33315805;gap:8px!important;transition:border-color .2s,box-shadow .2s}.st-key-composer:focus-within{border-color:#b5acd5;box-shadow:0 0 0 3px #7364aa08,0 5px 20px #33315805}
.composer-heading{display:flex;align-items:center;justify-content:space-between;gap:12px}.composer-heading strong{font-size:12px;font-weight:550;color:#62617a}.composer-heading span{font-size:10px;color:#9e9bb0}
.st-key-composer [data-testid="stTextArea"] textarea{background:#fff;border-radius:8px;font-size:14px;padding:8px 10px;line-height:1.65}.st-key-composer [data-testid="stTextArea"] [data-baseweb="textarea"]{background:#fff;border-color:#f1f0f6!important;border-radius:8px}.st-key-composer [data-testid="stCheckbox"] label p{font-size:11px}.st-key-composer [data-testid="stForm"]{padding:0;border:none}
.st-key-composer [data-testid="stFormSubmitButton"] button{min-height:35px;background:linear-gradient(110deg,#645ac6,#756bcc)!important;border:none!important;box-shadow:0 3px 8px #6352bb15}.st-key-composer [data-testid="stFormSubmitButton"] button:hover{box-shadow:0 4px 15px #6352bb25;filter:brightness(1.04)}.st-key-composer [data-testid="stFormSubmitButton"] button:disabled{background:#efedf5!important;color:#a29aaf!important;box-shadow:none}
.st-key-transcript [data-testid="stChatMessage"]{box-shadow:none;background:#fff;border-color:#e5e6ef;border-radius:11px;padding:11px 13px}.st-key-transcript [data-testid="stChatMessageAvatarUser"]{background:#e7e8f1;color:#727795}.st-key-transcript [data-testid="stChatMessageAvatarAssistant"]{background:#f0edf8;color:#6b60a3}
.notebook-heading{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:12px 0 8px}.notebook-heading h2{font-size:16px;margin:0;padding:0}.notebook-heading p{font-size:11px;margin:6px 0 0;color:#9292a3}.notebook-total{display:flex;align-items:baseline;gap:7px}.notebook-total strong{font-size:25px;font-weight:500;letter-spacing:-.04em;color:#6e638b}.notebook-total span{font-size:10px;color:#9794a4}
[class*="st-key-notes_"]{padding:12px 13px;border:1px solid #e7e7ef;border-radius:10px;background:#fff;gap:8px!important}.note-group-title{display:flex;align-items:center;justify-content:space-between;font-size:12px;color:#565974}.note-group-title strong{font-weight:550}.note-group-title>span{font-size:10px;color:#9292a9;background:#f4f4f8;padding:2px 7px;border-radius:5px}.statement-card{border-left:2px solid #d7d0eb;padding:5px 11px;background:#faf9fd}.statement-card p{font-size:13px;line-height:1.8;margin:0;color:#4c4c60;overflow-wrap:anywhere}.statement-card>span{display:block;margin-top:6px;font-size:10px;color:#9c95ac}
.briefing-intro{padding:18px 20px;margin:6px 0 12px;border:1px solid #dfe3e8;background:linear-gradient(120deg,#f6f8f4,#f9fafc);border-radius:12px}.briefing-intro>span{font-size:10px;letter-spacing:.06em;color:#84927c}.briefing-intro h2{font-size:19px!important;margin:9px 0;padding:0;color:#454d48}.briefing-intro p{font-size:12px;line-height:1.8;margin:0;color:#858d87}.st-key-briefing_document{padding:16px 20px;border:1px solid #e6e7ed;border-radius:10px;background:#fff}
@media(max-width:600px){.composer-heading{align-items:flex-start;flex-direction:column;gap:4px}.st-key-composer{padding:10px}.inquiry-lens{padding:9px 10px}.lens-eyebrow{display:block;margin-bottom:3px}.inquiry-lens p{font-size:10px}.notebook-heading{gap:8px}.notebook-heading h2{font-size:14px!important}.notebook-total{flex-direction:column;gap:0;align-items:flex-end}.briefing-intro{padding:14px}.briefing-intro h2{font-size:17px!important}}

@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>'''

def appearance_styles():
    # Read local tokens on every render so appearance updates do not need a reload.
    return STYLE.replace("</style>", (Path(__file__).resolve().parents[1] / "frontend/theme_tokens.css").read_text() + "</style>")

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
