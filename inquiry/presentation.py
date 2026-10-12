"""Local, dependency-free motion inspired by Hairline. No user content or keys in HTML."""
from html import escape

STYLE = '''<style>
:root{--ink:#242630;--muted:#737780;--line:#e4e5ea;--accent:#6558ce;--ease:cubic-bezier(.22,1,.36,1)}
.stApp{background:#fafafa;color:var(--ink)}
.block-container{max-width:1260px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em;color:var(--ink)}
[data-testid="stSidebar"]{background:#f3f3f6;border-right:1px solid var(--line)}
[data-testid="stChatMessage"],[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:16px}
[data-testid="stChatMessage"]{animation:enter .35s var(--ease)}
.stButton button,.stDownloadButton button{transition:background .2s,border-color .2s,box-shadow .2s}
.stButton button:hover,.stDownloadButton button:hover{border-color:var(--accent);box-shadow:0 3px 12px #24263009}
.hero{display:flex;justify-content:space-between;align-items:center;padding:0 0 1.4rem;border-bottom:1px solid var(--line);margin-bottom:1.6rem}
.hero h1{font-size:3.8rem;margin:0;padding:0}.hero p{color:var(--muted);font-size:1.04rem;margin:.3rem 0}
.eyebrow{font-size:.68rem;letter-spacing:.18em;color:var(--accent);font-weight:600}
.hero-glyph{width:74px;height:74px;position:relative;margin-right:15px;flex-shrink:0}
.hero-glyph span{position:absolute;width:46px;height:46px;border:1px solid #a6a2bd;border-radius:9px;transform:rotate(-28deg) skew(8deg);left:12px;background:#fafafa}
.hero-glyph span:nth-child(1){top:20px}.hero-glyph span:nth-child(2){top:12px}.hero-glyph span:nth-child(3){top:4px;animation:settle .9s var(--ease) both}
/* Native buttons retain real Python callbacks and keyboard activation. Stable columns are hit areas. */
.st-key-case_picker{padding:20px 8px 8px;margin-bottom:8px}
.st-key-case_picker [data-testid="stHorizontalBlock"]{gap:10px!important;overflow:visible}
.st-key-case_picker [data-testid="stColumn"]{position:relative;perspective:700px;padding-top:12px}
.st-key-case_picker [data-testid="stColumn"]:before{content:'';position:absolute;left:8px;top:4px;width:48%;height:20px;background:#eeeef3;border:1px solid #dedee7;border-radius:8px 8px 0 0}
.st-key-case_picker button{position:relative;min-height:128px;width:100%;border:1px solid #dcdce5;border-radius:6px 12px 12px 12px;background:linear-gradient(155deg,#fff,#f5f5fa);color:var(--ink);text-align:left;align-items:flex-start;justify-content:flex-start;padding:17px 12px;box-shadow:0 5px 14px #20213406;transition:transform .65s var(--ease),box-shadow .4s,border-color .25s;white-space:pre-line}
.st-key-case_picker button>div{white-space:normal;overflow:visible;text-overflow:clip;width:100%}.st-key-case_picker button [data-testid="stMarkdownContainer"]{display:block;white-space:normal;overflow:visible}.st-key-case_picker button p{display:block!important;white-space:normal;font-size:.87rem;line-height:1.5;margin:0}.st-key-case_picker button p:first-child{font-size:.68rem;color:#8b849e;margin-bottom:10px}
.st-key-case_picker button[kind="primary"]{border-color:#8174da;background:#f0edff;color:#473699;box-shadow:inset 0 0 0 1px #8174da33,0 8px 22px #6558ce10}
.st-key-case_picker [data-testid="stColumn"]:hover button,.st-key-case_picker button:focus-visible{transform:translateY(-12px) rotateX(5deg);box-shadow:0 16px 24px #29233f12}
.st-key-case_picker [data-testid="stColumn"]:has(+ [data-testid="stColumn"]:hover) button{transform:translateY(-4px) rotate(-1deg);transition-delay:.035s}
.st-key-case_picker [data-testid="stColumn"]:hover + [data-testid="stColumn"] button{transform:translateY(-4px) rotate(1deg);transition-delay:.035s}
.exploded{position:relative;padding:12px 0 4px;margin-bottom:1rem}
.exploded .layer{position:relative;margin-top:-4px;border:1px solid var(--line);border-radius:10px;background:white;padding:12px 16px;transition:transform .5s var(--ease),margin .5s var(--ease);box-shadow:0 3px 10px #20213404}
.exploded:hover .layer,.exploded:focus-within .layer{margin-top:7px;transform:translateX(var(--offset))}
.exploded .layer small{color:var(--accent);font-size:.65rem;letter-spacing:.1em}.exploded .layer p{color:#666978;font-size:.85rem;line-height:1.5;margin:3px 0 0}
.workflow-panel{background:#fff;border:1px solid #e4e3eb;border-radius:20px;padding:20px 22px;margin:0 0 26px;box-shadow:0 8px 28px #24263004}
.flow-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;font-size:12px;font-weight:600;letter-spacing:.08em}.flow-status{font-size:11px;letter-spacing:0;font-weight:500;background:#f3f2f8;color:#767187;border-radius:20px;padding:5px 10px}
.flow-track{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.flow-step{position:relative;border:1px solid #eae9ef;background:#fafafb;border-radius:12px;padding:15px;min-height:108px;transition:background .35s,border-color .35s,transform .4s var(--ease)}
.flow-step .marker{display:inline-flex;width:28px;height:28px;align-items:center;justify-content:center;border-radius:9px;background:#eeedf3;color:#888295;font-size:11px;margin-bottom:10px}.flow-step strong{display:block;font-size:13px;font-weight:600}.flow-step small{display:block;font-size:11px;color:#8a8793;margin-top:5px;line-height:1.5}
.flow-step.active{border-color:#b3a8ed;background:#f3f0ff;box-shadow:0 0 0 3px #6558ce07}.flow-step.active .marker{color:white;background:var(--accent);animation:pulse 1.3s ease-in-out infinite}.flow-step.complete{border-color:#d4e4dc;background:#f6faf8}.flow-step.complete .marker{color:#387558;background:#e1f0e7}.flow-step.failed{border-color:#e6b8b8;background:#fff8f8}.flow-step.failed .marker{color:#a64545;background:#f6dfdf}
.st-key-own_scenario{border:1px solid #dcd7f0;border-radius:16px;padding:14px 18px;background:linear-gradient(110deg,#f0edfc,#fff);margin-bottom:16px}.st-key-own_scenario button{min-height:54px;text-align:left;justify-content:flex-start;border:0!important;background:transparent!important;box-shadow:none!important;color:#52458d!important;font-size:18px!important}.st-key-own_scenario button p{font-size:18px;font-weight:600}.st-key-own_scenario [data-testid="stCaptionContainer"]{padding-left:8px}
.st-key-case_picker{padding:18px 0 12px}.st-key-case_picker [data-testid="stHorizontalBlock"]{gap:16px!important}.st-key-case_picker [data-testid="stColumn"]:before{width:45%;height:26px;left:0;top:0;background:#e9e6f4;border-color:#dcd7ea}.st-key-case_picker [data-testid="stColumn"]:after{content:'';position:absolute;inset:22px 6px 0;border:1px solid #e2dfec;border-radius:12px;background:#f0eef6;z-index:0;transform:rotate(2deg);pointer-events:none;transition:transform .6s var(--ease)}.st-key-case_picker [data-testid="stColumn"]:hover:after{transform:translateY(-5px) rotate(4deg)}
.st-key-case_picker button{z-index:1;min-height:176px;padding:20px 17px;border-radius:5px 14px 14px 14px;transition:transform .65s cubic-bezier(.16,1.25,.36,1),box-shadow .4s,border-color .25s}.st-key-case_picker button p:nth-child(2){font-size:17px;line-height:1.4;margin-bottom:12px}.st-key-case_picker button p:last-child{font-size:11px;color:#878293}.st-key-case_picker [data-testid="stColumn"]:hover button{transform:translateY(-16px) rotateX(7deg) rotate(-1deg);box-shadow:0 20px 30px #29233f16}
.exploded .layer{padding:16px 20px;border-radius:14px;transition:transform .6s cubic-bezier(.16,1.15,.36,1),margin .5s var(--ease)}.exploded .layer:nth-child(2){background:#faf9ff}.exploded .layer:nth-child(3){background:#f5f3fc}.exploded:hover .layer,.exploded:focus-within .layer{margin-top:10px;transform:translateX(var(--offset))}
@keyframes pulse{50%{box-shadow:0 0 0 5px #6558ce18;opacity:.5}}@keyframes enter{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}@keyframes settle{from{opacity:0;transform:translateY(-8px) rotate(-28deg) skew(8deg)}to{opacity:1;transform:rotate(-28deg) skew(8deg)}}
@media(max-width:700px){.block-container{padding:1.2rem 1rem}.hero h1{font-size:2.8rem}.st-key-case_picker [data-testid="stHorizontalBlock"]{flex-wrap:wrap}.st-key-case_picker [data-testid="stColumn"]{min-width:140px!important;flex:1 1 40%!important}.st-key-case_picker button{min-height:100px}.hero-glyph{width:60px}.flow-track{grid-template-columns:repeat(2,1fr)}.workflow-panel{padding:16px}.flow-step{padding:12px}.st-key-case_picker button{min-height:170px}.st-key-case_picker button p:nth-child(2){font-size:15px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}.st-key-case_picker button{transform:none!important}}
</style>'''


def relay_html(stage='idle', zh=False, failed=False):
    names = ['输入检查','模型追问','输出校验','保存结果'] if zh else ['Check input','Ask model','Validate output','Save result']
    descriptions = ['读取情境与上下文','请求下一条伦理问题','检查结构与引用','保留本会话探究记录'] if zh else ['Read situation and context','Request the next ethical question','Check structure and quotations','Keep this session’s inquiry record']
    steps = ['input','request','validate','save']
    current = steps.index(stage) if stage in steps else (4 if stage=='done' else -1)
    status = ('需要处理错误' if zh else 'Needs attention') if failed else ('已完成本轮' if zh else 'Turn complete') if stage=='done' else ('等待输入' if zh else 'Waiting for input') if stage=='idle' else ('正在执行' if zh else 'In progress')
    nodes=[]
    for i,label in enumerate(names):
        state='complete' if i<current else ('failed' if failed else 'active') if i==current else ''
        marker='✓' if state=='complete' else '!' if state=='failed' else f'{i+1:02}'
        nodes.append(f'<div class="flow-step {state}"><span class="marker">{marker}</span><strong>{label}</strong><small>{descriptions[i]}</small></div>')
    heading = '探究执行流程' if zh else 'INQUIRY WORKFLOW'
    return f'<div class="workflow-panel" role="status" aria-live="polite"><div class="flow-heading">{heading}<span class="flow-status">{status}</span></div><div class="flow-track">'+''.join(nodes)+'</div></div>'


def details_html(example, zh=False):
    own=example['id']=='blank'
    rows=[('CONTEXT / 情境', '由你描述参与者、待作判断与顾虑。' if own and zh else 'Describe the people, decision and concern.' if own else example['text_zh' if zh else 'text_en']),
          ('INQUIRY / 探究', '围绕客观性追问缺失事实、证据与独立复核。' if zh else 'Explore missing facts, evidence and independent review through the lens of objectivity.'),
          ('HUMAN REVIEW / 人工复核', '案例可修改，选择后不会自动发送。判断仍由人作出。' if zh else 'Edit before sending. Selection never submits a request. Judgment stays with people.')]
    return '<div class="exploded" tabindex="0" role="group" aria-label="Case information layers">'+''.join(f'<div class="layer" style="--offset:{i*3}px"><small>{label}</small><p>{escape(text)}</p></div>' for i,(label,text) in enumerate(rows))+'</div>'
