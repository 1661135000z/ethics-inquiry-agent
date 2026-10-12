"""Run with: python -m streamlit run app.py"""
import hmac
import hashlib
from dotenv import dotenv_values
import os
from pathlib import Path
import streamlit as st
from inquiry.core import Session, AREAS, InputError, ModelOutputError
from inquiry.providers import PROVIDERS, Client, FallbackClient, ProviderError, Limits, settings_from, session_settings
from inquiry.presentation import STYLE, relay_html, details_html
from inquiry.examples import EXAMPLES

st.set_page_config(page_title="Inquire · Audit ethics", page_icon="◈", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)


@st.cache_resource
def shared_limits():
    # Counters only. Never cache conversation content or API clients/keys.
    return Limits(40, 3600), Limits(150, 86400)


def reset():
    st.session_state.conversation = Session()
    st.session_state.draft = ""
    st.session_state.show_briefing = False
    st.session_state.example = "blank"
    st.session_state.example_source = ""
    st.session_state.workflow = ("idle", False)
    # Intentionally preserve attempt limit across New inquiry.


if "conversation" not in st.session_state: reset()
if "attempts" not in st.session_state: st.session_state.attempts = 0
if st.session_state.pop("clear_draft", False): st.session_state.draft = ""

try:
    secret_values = st.secrets.to_dict()
except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
    secret_values = {}
owner_settings = settings_from(os.environ, secret_values, dotenv_values(Path(__file__).with_name(".env")))
settings = dict(owner_settings)

with st.sidebar:
    st.markdown("### ◈ Inquire")
    language = st.selectbox("Language / 语言", ["English", "中文"], key="language")
zh = language == "中文"


def t(en, cn): return cn if zh else en


if settings.get("ACCESS_CODE"):
    with st.sidebar:
        access = st.text_input(t("Access code", "访问码"), type="password")
    if not hmac.compare_digest(access.encode(), settings["ACCESS_CODE"].encode()):
        st.title("Inquire")
        st.info(t("Enter the access code supplied by the project owner to continue.", "请输入项目负责人提供的访问码。"))
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


with st.sidebar:
    st.markdown("**AI Model Settings**")
    for service, credential in st.session_state.get("visitor_credentials", {}).items():
        settings = session_settings(settings, service, credential["key"],
            settings.get(PROVIDERS[service]["setting"]) or PROVIDERS[service]["model"], credential["free"])
    configured = [k for k, v in PROVIDERS.items() if settings.get(v["key"])]
    default = configured[0] if configured else "gemini"
    provider = st.selectbox(t("Model service", "模型服务"), list(PROVIDERS), index=list(PROVIDERS).index(default),
                            format_func=lambda k: PROVIDERS[k]["name"], key="provider")
    if provider == "openrouter":
        fixed = "nvidia/nemotron-3-super-120b-a12b:free"
        choices = [fixed, "openrouter/free"]
        configured_model = settings.get("OPENROUTER_MODEL", "")
        if configured_model and configured_model not in choices:
            choices.append(configured_model)
        selected_model = st.selectbox(t("Free model", "免费模型"), choices, key="free_model",
            format_func=lambda m: t("Nemotron 3 Super · fixed", "Nemotron 3 Super · 固定模型") if m == fixed else
                                  t("Free router · variable model", "免费路由 · 模型可能变化") if m == "openrouter/free" else m)
        settings = dict(settings, OPENROUTER_MODEL=selected_model)
    if provider != "openrouter":
        models = ["gemini-2.5-flash-lite", "gemini-2.5-flash"] if provider == "gemini" else ["glm-4.7-flash"]
        configured_model = settings.get(PROVIDERS[provider]["setting"])
        selected_model = st.selectbox(t("Model", "模型"), models,
            index=models.index(configured_model) if configured_model in models else 0, key=f"model_{provider}")
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
    st.caption(t("Test sends one fictional inquiry and uses API quota.", "测试会发送一段虚构伦理情境，消耗一次 API 额度。"))
    if st.button(t("Test Connection", "测试连接"), key="test_connection", disabled=bool(config_error), use_container_width=True):
        try:
            probe = Session()
            with st.spinner(t("Testing the inquiry workflow…", "正在测试伦理追问流程……")):
                probe.submit("Fictional scenario: I am an audit senior. My manager asks me to accept an estimate supported only by management's claim. I do not know what independent evidence exists.",
                             Client(provider, settings, budget=take_budget), language)
            st.session_state.connection_check = {"signature": signature, "model": probe.records[-1]["model"]}
            st.rerun()
        except (ProviderError, ModelOutputError, InputError) as error:
            st.session_state.connection_check = None
            st.error(str(error))
    secondary = None
    alternatives = [k for k in configured if k != provider]
    if alternatives:
        use_fallback = st.checkbox(t("Allow one free-provider fallback", "允许切换到一个免费备用服务"), value=False)
        if use_fallback:
            secondary = st.selectbox(t("Fallback service", "备用服务"), alternatives, format_func=lambda k: PROVIDERS[k]["name"])
            st.caption(t("On network/quota failure, the same conversation is sent to this service. No paid fallback.",
                         "连接或额度失败时，同一对话将发送至该服务，不会切换到付费模型。"))
    st.divider()
    st.caption(t("ONE PRINCIPLE", "聚焦一个原则"))
    st.markdown("**" + t("Objectivity", "客观性") + "**")
    st.caption(t("Explore how interests, pressure, bias and reliance on technology may influence professional judgment.",
                 "探究利益、压力、偏见与技术依赖可能如何影响职业判断。"))
    st.button(t("New inquiry", "开始新对话"), key="new_inquiry", on_click=reset, use_container_width=True)
    st.caption(t(f"Requests this session: {st.session_state.attempts}/24", f"本会话请求：{st.session_state.attempts}/24"))
    with st.expander(t("Setup & cost", "配置与费用")):
        st.write(t("Keys belong in environment variables or .streamlit/secrets.toml. Never put them in a scenario.",
                   "密钥放在环境变量或 .streamlit/secrets.toml 中，不要输入到情境里。"))
        if config_error: st.write(config_error)
        st.caption(t("Use a free-tier account. The app cannot verify your billing status. Free quotas and availability can change.",
                     "请使用免费档账号。本应用无法核实账号计费状态；免费额度和可用性可能变化。"))
        st.download_button(t("Download settings template", "下载配置模板"),
                           Path(__file__).with_name(".streamlit").joinpath("secrets.toml.example").read_text(),
                           "secrets.toml.example", mime="text/plain")

st.markdown('<div class="hero"><div><div class="eyebrow">ETHICS IN PRACTICE</div><h1>Inquire.</h1><p>' +
            t("Better judgment begins with a better question.", "好的判断，从一个更好的问题开始。") + '</p></div><div class="hero-glyph" aria-hidden="true"><span></span><span></span><span></span></div></div>', unsafe_allow_html=True)
conversation = st.session_state.conversation


def load_example(case_id):
    example = next(e for e in EXAMPLES if e["id"] == case_id)
    st.session_state.example = case_id
    st.session_state.draft = example["text_zh" if st.session_state.language == "中文" else "text_en"]
    st.session_state.example_source = example["source"]


if not conversation.messages:
    st.caption(t("CASE SELECTION · optional, editable starting points", "案例选择 · 可选、可修改的起点"))
    with st.container(key="case_picker"):
        for i, (column, case) in enumerate(zip(st.columns(len(EXAMPLES)), EXAMPLES)):
            with column:
                selected = case["id"] == st.session_state.example
                name = case["zh" if zh else "en"].replace("Example · ", "").replace("Fictional · ", "").replace("示例 · ", "").replace("新编虚构 · ", "")
                st.button(f"{i+1:02}  {'✓' if selected else '↗'}\n\n{name}", key=f"case_{case['id']}",
                    type="primary" if selected else "secondary", on_click=load_example, args=(case["id"],), use_container_width=True)
    selected_case = next(e for e in EXAMPLES if e['id'] == st.session_state.example)
    with st.expander(t("Case details · inspect the layers", "案例详情 · 展开信息层次")):
        st.markdown(details_html(selected_case, zh), unsafe_allow_html=True)
        if selected_case['source']: st.caption(selected_case['source'])



left, right = st.columns([2.1, 1], gap="large")
with left:
    st.subheader(t("Your inquiry", "你的伦理情境"))
    st.caption(t("Describe a situation. Examine what is known. Decide what needs checking.",
                 "描述情境，梳理已知信息，发现仍需核实的事项。"))
    if not conversation.messages:
        with st.container(border=True):
            st.markdown("**" + t("Start with your own situation", "从你自己的情境开始") + "**")
            st.write(t("Who is involved, what decision is being made, and what concerns you? Leave unknown facts unknown.",
                       "谁参与其中？需要作出什么判断？你有什么顾虑？不知道的事实可以保留为未知。"))
    for index, message in enumerate(conversation.messages):
        with st.chat_message(message["role"], avatar=":material/psychology:" if message["role"] == "assistant" else None):
            # Untrusted user/model text is never rendered as HTML or executable markdown.
            st.text(message["content"])
            if message["role"] == "assistant":
                record = conversation.records[index // 2]
                st.caption(f"{record['provider']} · {record['model']}")
                if record.get("fallback_from"):
                    st.caption(t("Fallback used from ", "已从以下服务切换：") + record["fallback_from"])
    with st.form("inquiry_form", clear_on_submit=False):
        st.text_area(t("Describe the situation or answer the last question", "描述情境，或回答上一个问题"),
                     key="draft", height=140, max_chars=4000,
                     placeholder=t("Start here. You do not need to know the answer yet.", "从这里开始。不确定或不知道的信息，也可以直接说明。"))
        consent = st.checkbox(t("This is fictional or anonymized; I agree to send this conversation to the selected model service(s).",
                                "内容为虚构或已匿名处理；我同意将对话发送给所选模型服务。"), key="consent")
        sent = st.form_submit_button(t("Ask the next question →", "开始 / 继续追问 →"), key="submit_inquiry",
                                    type="primary", disabled=bool(config_error) or conversation.turns >= 12,
                                    use_container_width=True)
        if config_error:
            st.caption(t("Configure a key in AI Model Settings before sending.",
                         "请先在侧栏 AI Model Settings 输入密钥或设置开发者配置。"))
    relay = st.empty()
    stage, failed = st.session_state.workflow
    relay.markdown(relay_html(stage, zh, failed), unsafe_allow_html=True)

    def progress(stage):
        st.session_state.workflow = (stage, False)
        relay.markdown(relay_html(stage, zh), unsafe_allow_html=True)

    if sent:
        if not consent:
            st.warning(t("Please confirm the data-sharing notice before sending.", "请先确认上方的数据发送说明。"))
        else:
            try:
                live = FallbackClient(Client(provider, settings, budget=take_budget),
                                      Client(secondary, settings, budget=take_budget) if secondary else None)
                with st.spinner(t("Finding the next useful question…", "正在寻找值得进一步追问的问题……")):
                    conversation.submit(st.session_state.draft, live, language, progress=progress)
                st.session_state.clear_draft = True
                st.session_state.show_briefing = False
                st.rerun()
            except (InputError, ModelOutputError, ProviderError) as error:
                stage = st.session_state.workflow[0]
                st.session_state.workflow = (stage, True)
                relay.markdown(relay_html(stage, zh, True), unsafe_allow_html=True)
                st.error(str(error))
    if conversation.turns >= 12:
        st.info(t("Turn limit reached. Export the record and begin a new inquiry if needed.", "已达到对话轮数上限。请先导出记录，再按需开始新对话。"))
    if st.session_state.show_briefing:
        with st.container(border=True):
            st.text(conversation.briefing(language))

with right:
    st.markdown("**" + t("INQUIRY NOTEBOOK", "探究记录") + "**")
    st.caption(t("User-reported statements, not verified evidence. These are inquiry topics, not a compliance score.",
                 "用户陈述不等于已核实的证据。以下是探究主题，不是合规评分。"))
    for key, labels in AREAS.items():
        quotes = [o["quote"] for o in conversation.observations if o["area"] == key]
        with st.expander(labels[int(zh)] + (f" · {len(quotes)}" if quotes else " · —")):
            if quotes:
                for quote in quotes: st.text(quote)
            else:
                st.caption(t("No statement extracted yet. This does not mean the issue is absent.", "尚未提取到相关陈述，不代表不存在该问题。"))
    st.divider()
    st.button(t("Prepare a review briefing", "生成人工复核简报"), key="briefing", disabled=conversation.turns < 2,
              on_click=lambda: st.session_state.update(show_briefing=True), use_container_width=True)
    st.caption(t("Available after your scenario and one follow-up answer. A briefing organizes evidence gaps; it does not decide the case.",
                 "描述情境并回答一次追问后可用。简报整理信息缺口，不替你作出结论。"))
    st.download_button(t("Download conversation", "下载对话记录"), conversation.export(language),
                       "inquire-conversation.md", mime="text/markdown", disabled=not conversation.messages,
                       use_container_width=True)
    with st.expander(t("Scope & limitations", "范围与局限")):
        st.write(t("This learning tool focuses on objectivity. AI may miss facts, misclassify statements or ask a poor question. Human review remains essential.",
                   "本学习工具聚焦客观性。AI可能遗漏事实、错误归类或提出不恰当的问题，仍需人工复核。"))
        st.write(t("No chat is intentionally saved to disk by this app. Model services process the conversation under their own policies. Download before resetting or leaving.",
                   "应用不会主动将聊天写入磁盘。模型服务按其自身政策处理对话。重置或离开前请自行下载。"))
        st.caption(t("Focus: objectivity and ethical threats. This is not an authoritative statement of current professional standards.",
                     "聚焦客观性及伦理威胁。本工具不是现行专业准则的权威解释。"))

st.divider()
st.caption(t("INQUIRE · A question-first learning tool. Professional judgment stays with people.",
             "INQUIRE · 先追问，再思考。职业判断仍由人作出。"))
