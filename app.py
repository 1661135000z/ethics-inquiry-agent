"""Run with: python -m streamlit run app.py"""
import hmac
import hashlib
from html import escape
from dataclasses import fields
from dotenv import dotenv_values
import os
from pathlib import Path
import streamlit as st
from inquiry.core import Session, AREAS, InputError, ModelOutputError
from inquiry.ui_state import Workspace
from inquiry.providers import PROVIDERS, Client, FallbackClient, ProviderError, Limits, settings_from, session_settings, GEMINI_MODELS
from inquiry.presentation import STYLE, relay_html
from inquiry.components import render_cases, render_journey, render_scroll, render_message_motion, render_welcome, render_transition, render_resume, render_copy
from inquiry.resume import ResumeStore
from inquiry.examples import EXAMPLES

st.set_page_config(page_title="Inquire · Audit ethics", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
st.markdown(STYLE, unsafe_allow_html=True)
font_sheet = Path(__file__).parent / "static/fonts/font.css"
if font_sheet.exists():
    font_css = font_sheet.read_text().replace("url('", "url('app/static/fonts/")
    st.markdown("<style>" + font_css + "</style>", unsafe_allow_html=True)

@st.cache_resource
def shared_limits():
    # Only anonymous counters, never user content or keys.
    return Limits(40, 3600), Limits(150, 86400)

if "workspace" not in st.session_state:
    # Upgrade an existing browser session without discarding its conversation.
    previous = st.session_state.get("conversation")
    ws = Workspace(conversation=previous if previous is not None else Session())
    if ws.conversation.messages:
        ws.phase = "chat"
        ws.onboarded = True
        ws.initial_text = ws.conversation.messages[0]["content"]
        ws.case_id = st.session_state.get("example", "blank")
        ws.draft = st.session_state.get("draft", "")
    st.session_state.workspace = ws
ws = st.session_state.workspace
# Reconstruct declared product fields when updating an already-open session.
def upgrade_workspace(workspace):
    defaults = Workspace()
    upgraded = Workspace(**{f.name: getattr(workspace, f.name, getattr(defaults, f.name)) for f in fields(Workspace)})
    if upgraded.conversation.messages: upgraded.onboarded = True
    return upgraded
ws = upgrade_workspace(ws)
st.session_state.workspace = ws

@st.cache_resource
def resume_store():
    return ResumeStore(ttl=7200, max_entries=128)

def resume_ready():
    if not st.session_state.get("resume_ready"):
        st.session_state.resume_ready = True
        st.session_state.resume_token = resume_store().issue(st.session_state.workspace)

def restore_workspace():
    token = st.session_state.get("resume_v2", {}).get("restore", "")
    restored = resume_store().get(token)
    if restored is not None:
        restored = upgrade_workspace(restored)
        st.session_state.workspace = restored
        st.session_state.resume_token = token
        if restored.provider_id in PROVIDERS:
            st.session_state.provider = restored.provider_id
            st.session_state.model_preferences = {restored.provider_id: restored.model_id}
        if restored.language_id in {"English", "中文"}:
            st.session_state.language = restored.language_id
        st.session_state.attempts = restored.request_count
        st.session_state.pop("draft", None)
    else:
        st.session_state.resume_token = resume_store().issue(st.session_state.workspace)
    st.session_state.resume_ready = True

render_resume(st.session_state.get("resume_token", ""), restore_workspace, resume_ready)
if not st.session_state.get("resume_ready"):
    st.caption("Inquire · …")
    st.stop()

def save_workspace():
    ws.provider_id = st.session_state.get("provider", ws.provider_id)
    ws.language_id = st.session_state.get("language", ws.language_id)
    ws.request_count = st.session_state.get("attempts", ws.request_count)
    # Public model identifiers only; no credentials or consent enter recovery.
    ws.model_id = globals().get("selected_model", "") or st.session_state.get("model_preferences", {}).get(ws.provider_id, "") or st.session_state.get(f"model_{ws.provider_id}_current", "") or st.session_state.get("free_model", "")
    if not resume_store().save(st.session_state.resume_token, ws):
        st.session_state.resume_token = resume_store().issue(ws)

# A refresh restores only inquiry data, never visitor credentials or consent.
ws = st.session_state.workspace
if "attempts" not in st.session_state: st.session_state.attempts = 0
# Stable diagnostic aliases: these contain no credentials.
st.session_state.conversation = ws.conversation
st.session_state.example = ws.case_id
st.session_state.workflow = ws.workflow

try:
    secret_values = st.secrets.to_dict()
except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
    secret_values = {}
owner_settings = settings_from(os.environ, secret_values, dotenv_values(Path(__file__).with_name(".env")))
settings = dict(owner_settings)
with st.sidebar:
    st.markdown("**Inquire**")
    language = st.selectbox("Language / 语言", ["English", "中文"], key="language")
zh = language == "中文"
def t(en, cn): return cn if zh else en

if settings.get("ACCESS_CODE"):
    with st.sidebar:
        access = st.text_input(t("Access code", "访问码"), type="password")
    if not hmac.compare_digest(access.encode(), settings["ACCESS_CODE"].encode()):
        st.title("Inquire")
        st.info(t("Enter the shared access code in the sidebar.", "请在侧栏输入共享访问码。"))
        st.stop()

def take_budget():
    if st.session_state.attempts >= 24: return False
    hourly, daily = shared_limits()
    if not hourly.take() or not daily.take(): return False
    st.session_state.attempts += 1
    return True

def remember_key(provider):
    st.session_state.setdefault("visitor_credentials", {})[provider] = {
        "key": st.session_state.get(f"api_key_{provider}", ""),
        "free": st.session_state.get(f"free_confirm_{provider}", False),
    }

def forget_keys():
    st.session_state.visitor_credentials = {}
    for name in list(st.session_state):
        if name.startswith("api_key_") or name.startswith("free_confirm_"):
            del st.session_state[name]
    st.session_state.connection_check = None

def remember_model(service, widget_key):
    st.session_state.setdefault("model_preferences", {})[service] = st.session_state.get(widget_key, "")
    st.session_state.consent = False

def changed_service():
    st.session_state.consent = False

# The permanent workspace draft survives widget cleanup when navigating between views.
def sync_draft():
    value = st.session_state.get("draft", "")
    if ws.phase == "select": ws.pending_text = value
    else: ws.draft = value

def sync_widget():
    st.session_state.draft = ws.pending_text if ws.phase == "select" else ws.draft

def choose_case(case_id):
    case = next((e for e in EXAMPLES if e["id"] == case_id), None)
    if case is None: return
    ws.choose(case_id, case["text_zh" if st.session_state.language == "中文" else "text_en"])
    sync_widget()
    st.session_state.consent = False

def transition(kind, title=""):
    st.session_state.transition_nonce = st.session_state.get("transition_nonce", 0) + 1
    st.session_state.transition_request = (kind, st.session_state.transition_nonce, title)

def confirm_model(signature):
    first = not ws.onboarded
    ws.confirm_model(signature)
    st.session_state.pop("scroll_request", None)
    if first:
        transition("model", PROVIDERS[st.session_state.provider]["name"].split(" · ")[0])

def on_welcome_event():
    service = st.session_state.get("welcome_v2", {}).get("choose")
    if service not in PROVIDERS: return
    st.session_state.provider = service
    st.session_state.consent = False
    st.session_state.scroll_request = ("model", st.session_state.get("scroll_nonce", 0) + 1)
    st.session_state.scroll_nonce = st.session_state.scroll_request[1]

def fill_suggestion(text):
    ws.draft = text
    sync_widget()

def on_case_event():
    choose_case(st.session_state.get("case_picker_v2", {}).get("choose"))

def reselect():
    if ws.phase != "select" and "draft" in st.session_state:
        ws.draft = st.session_state.draft
    ws.enter_selection()
    sync_widget()
    st.session_state.consent = False

def cancel_selection():
    ws.cancel_selection()
    sync_widget()
    st.session_state.consent = False

def new_conversation():
    ws.new_conversation()
    sync_widget()
    st.session_state.consent = False

def on_navigation():
    target = st.session_state.get("journey_v2", {}).get("navigate")
    if target not in {"model", "scenario", "conversation"}: return
    if target == "scenario": reselect()
    st.session_state.scroll_request = (target, st.session_state.get("scroll_nonce", 0) + 1)
    st.session_state.scroll_nonce = st.session_state.scroll_request[1]

st.session_state.ui_render_sequence = st.session_state.get("ui_render_sequence", 0) + 1
st.markdown('<div class="product-bar" data-render-sequence="' + str(st.session_state.ui_render_sequence) + '"><h1>Inquire<span>.</span></h1><span class="product-description">' +
            t("Audit ethics · question first", "审计伦理 · 先追问，再思考") + '</span></div>', unsafe_allow_html=True)
if ws.onboarded:
    main, rail = st.columns([4.6, 1], gap="large")
else:
    main, rail = st.container(key="welcome_workspace"), None
with main:
    if not ws.onboarded:
        configured_services = {k: bool(settings.get(v["key"])) for k,v in PROVIDERS.items()}
        selected_service = st.session_state.get("provider") or next((k for k in PROVIDERS if configured_services[k]), "gemini")
        render_welcome(selected_service, configured_services, zh, on_welcome_event)
    with st.container(key="model_entry"):
        with st.popover(t("Model settings", "模型设置"), icon=":material/tune:", key="model_settings", width="content"):
            for service, credential in st.session_state.get("visitor_credentials", {}).items():
                settings = session_settings(settings, service, credential["key"],
                    settings.get(PROVIDERS[service]["setting"]) or PROVIDERS[service]["model"], credential["free"])
            configured = [k for k, v in PROVIDERS.items() if settings.get(v["key"])]
            default = configured[0] if configured else "gemini"
            provider = st.selectbox(t("Model service", "模型服务"), list(PROVIDERS), index=list(PROVIDERS).index(default),
                                    format_func=lambda k: PROVIDERS[k]["name"], key="provider", on_change=changed_service)
            if provider == "openrouter":
                fixed = "nvidia/nemotron-3-super-120b-a12b:free"
                choices = [fixed, "openrouter/free"]
                configured_model = settings.get("OPENROUTER_MODEL", "")
                if configured_model and configured_model not in choices:
                    choices.append(configured_model)
                preferred = st.session_state.get("model_preferences", {}).get(provider, fixed)
                selected_model = st.selectbox(t("Free model", "免费模型"), choices, index=choices.index(preferred) if preferred in choices else 0, key="free_model", on_change=remember_model, args=(provider,"free_model"),
                    format_func=lambda m: t("Nemotron 3 Super · fixed", "Nemotron 3 Super · 固定模型") if m == fixed else
                                          t("Free router · variable model", "免费路由 · 模型可能变化") if m == "openrouter/free" else m)
                settings = dict(settings, OPENROUTER_MODEL=selected_model)
            if provider != "openrouter":
                models = list(GEMINI_MODELS) if provider == "gemini" else ["glm-4.7-flash"]
                configured_model = st.session_state.get("model_preferences", {}).get(provider) or settings.get(PROVIDERS[provider]["setting"])
                selected_model = st.selectbox(t("Model", "模型"), models,
                    index=models.index(configured_model) if configured_model in models and (provider in st.session_state.get("model_preferences", {}) or not configured_model.startswith("gemini-2.5-")) else 0, key=f"model_{provider}_current", on_change=remember_model, args=(provider,f"model_{provider}_current"))
                if provider == "gemini":
                    st.caption(t("2.5 models are retained for existing eligible projects; new projects should start with Flash-Lite 3.5.", "2.5系列仅保留给已有访问资格的项目；新项目默认使用3.5 Flash-Lite。"))
            with st.expander(t("Use your own API key", "使用自己的 API Key")):
                visitor_key = st.text_input(t("Session API key", "本会话 API Key"), type="password", key=f"api_key_{provider}",
                    value=st.session_state.get("visitor_credentials", {}).get(provider, {}).get("key", ""),
                    on_change=remember_key, args=(provider,),
                    help=t("Used only in this session. Leave empty to use the developer configuration.", "只用于当前会话；留空时使用开发者配置。"))
                free_confirmed = False
                if provider in {"gemini", "zhipu"}:
                    free_confirmed = st.checkbox(t("My key is eligible for the selected free-tier model", "我的密钥具有所选模型的免费档资格"), key=f"free_confirm_{provider}",
                        value=st.session_state.get("visitor_credentials", {}).get(provider, {}).get("free", False), on_change=remember_key, args=(provider,))
                st.button(t("Clear session keys", "清除会话密钥"), key="clear_api_keys", on_click=forget_keys)
                st.caption(t("Never paste a key into the scenario. Developer keys are never displayed.", "不要把密钥放进情境中。开发者密钥不会显示在页面上。"))
            settings = session_settings(settings, provider, visitor_key, selected_model, free_confirmed)
            st.caption(t("Key source: current session" if visitor_key else "Key source: developer configuration", "密钥来源：当前会话" if visitor_key else "密钥来源：开发者配置"))
            signature = hashlib.sha256((provider + selected_model + settings.get(PROVIDERS[provider]["key"], "") + settings.get(provider.upper()+"_FREE_TIER_CONFIRMED", "")).encode()).hexdigest()
            client = Client(provider, settings)
            config_error = None
            try:
                _, model = client.validate()
                if (st.session_state.get("connection_check") or {}).get("signature") == signature:
                    st.success(t("Connection verified · inquiry test passed", "连接已验证 · 伦理追问测试通过"))
                else:
                    st.info(t("Configured · ready to test", "已配置 · 待实际调用验证"))
                st.caption(model)
            except ProviderError as error:
                config_error = str(error)
                st.info(t("Connection setup needed", "需要配置模型连接"))
                st.caption(config_error)
            if provider == "gemini":
                st.caption(t("Connection tests first read the model list, then send one fictional inquiry.", "连接测试先读取可用模型列表，再发送一次虚构伦理追问。"))
                if st.button(t("Check available models", "检查可用模型"), key="check_models", disabled=bool(config_error)):
                    try:
                        names = Client(provider, settings, budget=take_budget).available_models()
                        st.session_state.gemini_available = {"signature": signature, "names": names}
                    except ProviderError as error:
                        st.error(str(error))
                available = st.session_state.get("gemini_available", {})
                if available.get("signature") == signature:
                    st.caption(t("Available approved models: ", "当前密钥可访问的已核准模型：") + (", ".join(available['names']) or t("None; check account and endpoint eligibility.", "暂无，请检查账号及接口资格。")))
            else:
                st.caption(t("Test sends one fictional inquiry and uses API quota.", "测试会发送一段虚构伦理情境，消耗一次 API 额度。"))
            if st.button(t("Test Connection", "测试连接"), key="test_connection", disabled=bool(config_error), use_container_width=True):
                try:
                    probe = Session()
                    with st.spinner(t("Testing the inquiry workflow…", "正在测试伦理追问流程……")):
                        if provider == "gemini":
                            names = Client(provider, settings, budget=take_budget).available_models()
                            st.session_state.gemini_available = {"signature": signature, "names": names}
                            if selected_model not in names:
                                raise ProviderError("Selected model not available to this key / 当前密钥无法访问所选模型。可用：" + (", ".join(names) or "none / 暂无"), "model_unavailable")
                        probe.submit("Fictional scenario: I am an audit senior. My manager asks me to accept an estimate supported only by management's claim. I do not know what independent evidence exists.",
                                     Client(provider, settings, budget=take_budget), language)
                    st.session_state.connection_check = {"signature": signature, "model": probe.records[-1]["model"]}
                    confirm_model(signature)
                    save_workspace()
                    st.rerun()
                except (ProviderError, ModelOutputError, InputError) as error:
                    st.session_state.connection_check = None
                    st.error(str(error))
            secondary = None
            alternatives = [k for k in configured if k != provider]
            if alternatives:
                use_fallback = st.checkbox(t("Allow one free-provider fallback", "允许切换到一个免费备用服务"), value=False,key="allow_fallback",on_change=changed_service)
                if use_fallback:
                    secondary = st.selectbox(t("Fallback service", "备用服务"), alternatives, format_func=lambda k: PROVIDERS[k]["name"],key="fallback_provider",on_change=changed_service)
                    st.caption(t("On network/quota failure, the same conversation is sent to this service. No paid fallback.",
                                 "连接或额度失败时，同一对话将发送至该服务，不会切换到付费模型。"))

        model_ready = not config_error and ws.confirmed_model == signature
        model_name = PROVIDERS[provider]["name"].split(" · ")[0]
        if not model_ready and not config_error:
            st.button(t(f"Use {model_name}", f"使用 {model_name}"), key="confirm_model", type="primary",
                      on_click=confirm_model, args=(signature,))
        badge = t("Connection verified", "连接已验证") if (st.session_state.get("connection_check") or {}).get("signature") == signature else t("Configured", "已配置")
        st.caption(t("Choose a service to begin.", "选择模型服务开始。") if config_error else f"{model_name} · {selected_model} · {badge}")
        if config_error:
            st.caption(t("Open Model settings to configure a connection.", "打开模型设置，配置连接。"))

    if not ws.onboarded:
        save_workspace()
        request=st.session_state.get("scroll_request")
        if request: render_scroll(request[0],request[1])
        st.stop()

    conversation = ws.conversation
    if conversation.messages:
        with st.container(key="inquiry_actions"):
            c1,c2 = st.columns(2)
            with c1: st.button(t("Choose another situation", "重新选择情境"), key="choose_scenario", on_click=reselect, width="stretch")
            with c2: st.button(t("New conversation", "开始新对话"), key="main_new_inquiry", on_click=new_conversation, width="stretch",
                              help=t("Clear this conversation; retain the initial situation and model. Download first if needed.", "清空对话，保留初始情境与模型；需要时先下载记录。"))
    if ws.phase != "chat":
        with st.container(key="scenario_region"):
            if ws.phase == "select":
                st.caption(t("Preview a new situation. Your current conversation stays until a new reply succeeds.", "预览新情境；当前对话会保留到新情境的有效回复返回。"))
                st.button(t("Cancel · return to conversation", "取消 · 返回当前对话"), key="cancel_selection", on_click=cancel_selection)
            own = (ws.pending_case if ws.phase == "select" else ws.case_id) == "blank"
            with st.container(key="own_scenario"):
                st.button(t("Write my own situation", "自行输入情境"), key="case_blank",
                          type="primary" if own else "secondary", on_click=choose_case, args=("blank",), width="stretch")
            subtitles = [t("Relationships & fees", "关系与收费"),t("Design & review", "设计与复核"),t("AI & evidence", "AI与证据"),t("Incentives & claims", "激励与陈述")]
            cases = [{"id":e["id"], "title":e["zh" if zh else "en"].split(" · ")[-1],"subtitle":subtitles[i],
                      "text":e["text_zh" if zh else "text_en"],"source":t("Original fictional scenario", "原创虚构情境") if e["id"] in {"dashboard","vendor"} else t("Hypothetical scenario", "假设情境")} for i,e in enumerate(EXAMPLES[1:])]
            render_cases(cases, ws.pending_case if ws.phase == "select" else ws.case_id, ws.epoch, on_case_event, zh=zh)

    with st.container(key="conversation_region"):
        if conversation.messages and ws.phase != "select":
            case_label = next((e["zh" if zh else "en"].split(" · ")[-1] for e in EXAMPLES if e["id"] == ws.case_id), t("Your situation", "自定义情境"))
            st.markdown('<div class="current-situation"><span>' + t("CURRENT SITUATION", "当前情境") + '</span><strong>' + escape(case_label) + '</strong></div>',unsafe_allow_html=True)
        tabs = st.tabs([t("Conversation", "对话"),t("Inquiry notebook", "探究记录"),t("Review briefing", "复核简报")]) if conversation.messages else [st.container(),st.container(),st.container()]
        with tabs[0]:
            if ws.phase == "select" and conversation.messages:
                with st.expander(t("Current conversation · preserved", "当前对话 · 已保留")):
                    for message in conversation.messages: st.text(message["content"])
            else:
                with st.container(key="transcript", height=310 if len(conversation.messages)>2 else "content", border=False, autoscroll=True if len(conversation.messages)>2 else None):
                    for index,message in enumerate(conversation.messages):
                        with st.chat_message(message["role"],avatar=":material/psychology:" if message["role"] == "assistant" else None):
                            st.text(message["content"])
                            if message["role"] == "assistant":
                                record=conversation.records[index//2]
                                st.caption(f"{record['provider']} · {record['model']}" + (t(" · fallback from ", " · 备用切换自 ")+record['fallback_from'] if record.get('fallback_from') else ""))
                                render_copy(message["content"], f"copy_{ws.epoch}_{index}", zh=zh)
            if conversation.messages and ws.phase == "chat":
                with st.container(key="chat_tools"):
                    st.button(t("Regenerate last question", "重新生成上一条追问"), key="regenerate", disabled=not model_ready, help=t("Uses one request; keeps your latest answer and all prior turns.", "使用一次请求；保留最新回答与之前对话。"))
                    with st.popover(t("Help me respond", "回答思路")):
                        st.caption(t("These fill an editable draft; they do not invent facts or send automatically.", "只填入可编辑草稿，不自动发送。请补充真实或虚构案例中的事实。"))
                        suggestions = [t("I do not know yet. The person or record that could verify this is…", "目前尚不确定。能够核实这一点的人或记录是……"), t("The evidence supporting this is…; an alternative explanation is…", "支持这一点的证据是……；另一种可能解释是……"), t("An independent reviewer could check…; their relationship to this decision is…", "独立复核人员可以检查……；其与本次判断的关系是……")]
                        for i, text in enumerate(suggestions):
                            st.button(text,key=f"suggestion_{i}",on_click=fill_suggestion,args=(text,))
            if "draft" not in st.session_state: sync_widget()
            st.text_area(t("Situation or follow-up answer", "情境或追问回答"), key="draft", height=110,max_chars=4000,
                         on_change=sync_draft, placeholder=t("Describe the decision and what concerns you…", "描述需要作出的判断，以及你的顾虑……"),label_visibility="collapsed")
            consent=st.checkbox(t("Fictional/anonymized content; send to the selected service(s).", "内容为虚构或已匿名处理；同意发送至所选模型服务。"),key="consent")
            with st.form("inquiry_form"):
                sent=st.form_submit_button(t("Start a new inquiry with this situation", "以此开始新对话") if ws.phase=="select" else t("Ask the next question", "开始 / 继续追问"),
                    key="submit_inquiry",type="primary",disabled=bool(config_error) or not model_ready or (conversation.turns>=12 and ws.phase!="select"),width="stretch")
            if not model_ready:
                st.caption(t("Choose and confirm your model above to continue.", "先在上方选择并确认模型。"))
            execution = st.expander(t("Execution details", "执行详情"),expanded=ws.workflow[1])
            with execution:
                relay = st.empty()
                relay.markdown(relay_html(*[ws.workflow[0], zh, ws.workflow[1]]), unsafe_allow_html=True)
            error_slot = st.empty()
            if conversation.turns>=12 and ws.phase!="select":
                st.caption(t("Turn limit reached. Export and start a new conversation.", "已到轮数上限，请导出后开始新对话。"))
        if conversation.messages:
            with tabs[1]:
                st.caption(t("User statements, not verified evidence.", "用户陈述，不是已核实的证据。"))
                for area,labels in AREAS.items():
                    quotes=[o["quote"] for o in conversation.observations if o["area"]==area]
                    with st.expander(labels[int(zh)] + (f" · {len(quotes)}" if quotes else " · —")):
                        if quotes:
                            for quote in quotes: st.text(quote)
                        else: st.caption(t("Nothing extracted yet; check the full conversation.", "尚无提取陈述，请核对完整对话。"))
            with tabs[2]:
                st.button(t("Prepare review briefing", "生成人工复核简报"),key="briefing",disabled=conversation.turns<2,
                          on_click=lambda: setattr(ws,"show_briefing",True))
                if ws.show_briefing and conversation.turns>=2: st.text(conversation.briefing(language))
                else: st.caption(t("Available after your situation and one follow-up answer.", "描述情境并回答一次追问后可用。"))
        if conversation.messages:
            st.download_button(t("Download conversation", "下载对话记录"),conversation.export(language),"inquire-conversation.md",mime="text/markdown",key="download_conversation")

# Journey state is derived from actual model confirmation, input and accepted replies.
model_ready = not config_error and ws.confirmed_model == signature
current=ws.current_step(signature,not bool(config_error))
scenario_ready = current == "conversation"
steps=[
    {"id":"model","title":t("Choose model", "选择模型"),"detail":model_name if model_ready else t("Service & connection", "服务与连接"),"state":"complete" if model_ready else "active"},
    {"id":"scenario","title":t("Choose situation", "选择情境"),"detail":t("Example or your own", "示例或自定义"),"state":"complete" if scenario_ready else "active" if current=="scenario" else "pending"},
    {"id":"conversation","title":t("Conversation in progress", "对话中") if conversation.messages and ws.phase!="select" else t("Start conversation", "开始对话"),"detail":t(f"{conversation.turns} turn" + ("s" if conversation.turns != 1 else ""),f"{conversation.turns}轮") if conversation.messages and ws.phase!="select" else "", "state":"active" if current=="conversation" else "pending"},
]
if rail is not None:
    with rail:
        with st.container(key="journey_rail"):
            render_journey(steps,on_navigation)

with st.sidebar:
    st.caption(t("Focus: objectivity", "聚焦客观性"))
    st.caption(t(f"Requests: {st.session_state.attempts}/24", f"请求：{st.session_state.attempts}/24"))
    with st.expander(t("Scope & cost", "范围与费用")):
        st.write(t("Human review is essential. This tool asks questions, not ethical clearances or audit opinions.", "本工具用于伦理追问，不提供伦理许可或审计意见，仍需人工复核。"))
        st.caption(t("Use fictional/anonymized data. Provider policies and free quotas apply. Download before resetting.", "仅使用虚构或匿名内容；遵循模型服务政策和免费额度，重置前按需下载。"))
        st.download_button(t("Settings template", "配置模板"),Path(__file__).parent.joinpath(".streamlit/secrets.toml.example").read_text(),"secrets.toml.example",mime="text/plain")

regenerate = bool(st.session_state.get("regenerate", False)) and bool(conversation.messages) and ws.phase == "chat"
if sent or regenerate:
    sync_draft()
    if not consent:
        error_slot.warning(t("Confirm data sharing before sending.", "请先确认数据发送说明。"))
    elif not model_ready:
        error_slot.warning(t("Confirm the model before sending.", "请先确认模型。"))
    else:
        def progress(stage):
            relay.markdown(relay_html(stage,zh),unsafe_allow_html=True)
        try:
            live=FallbackClient(Client(provider,settings,budget=take_budget),Client(secondary,settings,budget=take_budget) if secondary else None)
            with error_slot.container():
                with st.spinner(t("Preparing the next question…", "正在准备下一条问题……")):
                    first_reply = not ws.conversation.messages or ws.phase == "select"
                    if regenerate:
                        ws.regenerate(live,language,progress=progress)
                    else:
                        ws.submit(ws.pending_text if ws.phase=="select" else ws.draft,live,language,progress=progress)
                    if first_reply:
                        transition("conversation", t("Your inquiry", "你的探究"))
            record = ws.conversation.records[-1]
            if record['provider'] == provider and not record.get('fallback_from'):
                st.session_state.connection_check = {'signature': signature, 'model': record['model']}
            # Schedule widget update before it is rendered on the next run.
            if not regenerate: st.session_state.pop("draft",None)
            save_workspace()
            st.rerun()
        except (InputError,ModelOutputError,ProviderError) as error:
            if isinstance(error,ProviderError) and error.code == "auth": ws.confirmed_model=""
            relay.markdown(relay_html(ws.workflow[0],zh,True),unsafe_allow_html=True)
            error_slot.error(str(error))
            st.session_state.workflow=ws.workflow
            # Public expander API must be expanded on the next render.
            st.session_state.last_error=str(error)
            st.rerun()

if st.session_state.get("last_error"):
    error_slot.error(st.session_state.pop("last_error"))
transition_request = st.session_state.get("transition_request")
if transition_request:
    render_transition(*transition_request)
save_workspace()
render_message_motion(ws.epoch, 0 if ws.phase == "select" else len(ws.conversation.messages))
request=st.session_state.get("scroll_request")
if request: render_scroll(request[0],request[1])
st.session_state.conversation=ws.conversation
st.session_state.example=ws.case_id
st.session_state.workflow=ws.workflow
