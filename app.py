"""Run with: python -m streamlit run app.py"""
import hmac
import os
from pathlib import Path
import streamlit as st
from inquiry.core import Session, AREAS, InputError, ModelOutputError
from inquiry.providers import PROVIDERS, Client, FallbackClient, ProviderError, Limits, settings_from
from inquiry.examples import EXAMPLES

st.set_page_config(page_title="Inquire · Audit ethics", page_icon="◈", layout="wide")
st.markdown("""<style>
.stApp { background: #f7f8fa; }
.block-container { max-width: 1240px; padding-top: 2.4rem; padding-bottom: 2rem; }
h1,h2,h3 { letter-spacing: -.025em; color: #182b3a; }
[data-testid="stSidebar"] { background: #edf1f4; border-right: 1px solid #dce3e8; }
[data-testid="stChatMessage"] { background: white; border: 1px solid #e4e9ec; border-radius: 14px; }
[data-testid="stForm"] { background: white; border-radius: 16px; }
.eyebrow { font-size: .72rem; letter-spacing: .18em; font-weight: 700; color: #177c76; margin-bottom: .5rem; }
.hero { padding-bottom: 1.1rem; border-bottom: 1px solid #dce3e8; margin-bottom: 1.3rem; }
.hero h1 { font-size: 3.3rem; margin: 0; padding: 0; }
.hero p { color: #63727d; font-size: 1.05rem; margin: .4rem 0 0; }
.step { border-left: 3px solid #177c76; padding-left: .85rem; color: #526473; font-size: .9rem; }
@media(max-width: 700px) { .block-container { padding: 1.2rem 1rem; } .hero h1 { font-size: 2.5rem; } }
</style>""", unsafe_allow_html=True)


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
    # Intentionally preserve attempt limit across New inquiry.


if "conversation" not in st.session_state: reset()
if "attempts" not in st.session_state: st.session_state.attempts = 0
if st.session_state.pop("clear_draft", False): st.session_state.draft = ""

try:
    secret_values = st.secrets.to_dict()
except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
    secret_values = {}
settings = settings_from(os.environ, secret_values)

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

with st.sidebar:
    st.caption(t("CONNECTION", "模型连接"))
    configured = [k for k, v in PROVIDERS.items() if settings.get(v["key"])]
    default = configured[0] if configured else "gemini"
    provider = st.selectbox(t("Model service", "模型服务"), list(PROVIDERS), index=list(PROVIDERS).index(default),
                            format_func=lambda k: PROVIDERS[k]["name"], key="provider")
    client = Client(provider, settings)
    config_error = None
    try:
        _, model = client.validate()
        st.success(t("Configured · ready to test", "已配置 · 待实际调用验证"))
        st.caption(model)
    except ProviderError as error:
        config_error = str(error)
        st.info(t("Connection setup needed", "需要配置模型连接"))
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

st.markdown('<div class="hero"><div class="eyebrow">ETHICS IN PRACTICE</div><h1>Inquire.</h1><p>' +
            t("Better judgment begins with a better question.", "好的判断，从一个更好的问题开始。") + '</p></div>', unsafe_allow_html=True)
conversation = st.session_state.conversation
left, right = st.columns([2.1, 1], gap="large")


def load_example():
    example = next(e for e in EXAMPLES if e["id"] == st.session_state.example)
    st.session_state.draft = example["text_zh" if st.session_state.language == "中文" else "text_en"]
    st.session_state.example_source = example["source"]


def take_budget():
    if st.session_state.attempts >= 24: return False
    hourly, daily = shared_limits()
    if not hourly.take() or not daily.take(): return False
    st.session_state.attempts += 1
    return True


with left:
    st.subheader(t("Your inquiry", "你的伦理情境"))
    st.caption(t("Describe a situation. Examine what is known. Decide what needs checking.",
                 "描述情境，梳理已知信息，发现仍需核实的事项。"))
    if not conversation.messages:
        with st.container(border=True):
            st.markdown("**" + t("Start with your own situation", "从你自己的情境开始") + "**")
            st.write(t("Who is involved, what decision is being made, and what concerns you? Leave unknown facts unknown.",
                       "谁参与其中？需要作出什么判断？你有什么顾虑？不知道的事实可以保留为未知。"))
            with st.expander(t("Or explore an optional example", "也可以选用示例（可修改）")):
                st.selectbox(t("Example", "示例"), [e["id"] for e in EXAMPLES], key="example",
                             format_func=lambda k: next(e["zh" if zh else "en"] for e in EXAMPLES if e["id"] == k))
                st.button(t("Use as a starting point", "填入输入框"), key="load_example", on_click=load_example)
                if st.session_state.example_source: st.caption(st.session_state.example_source)
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
            st.caption(t("No model request can be sent until the connection is configured. See Setup & cost in the sidebar.",
                         "模型连接配置完成后才能发送。请查看侧栏的“配置与费用”。"))
    if sent:
        if not consent:
            st.warning(t("Please confirm the data-sharing notice before sending.", "请先确认上方的数据发送说明。"))
        else:
            try:
                live = FallbackClient(Client(provider, settings, budget=take_budget),
                                      Client(secondary, settings, budget=take_budget) if secondary else None)
                with st.spinner(t("Finding the next useful question…", "正在寻找值得进一步追问的问题……")):
                    conversation.submit(st.session_state.draft, live, language)
                st.session_state.clear_draft = True
                st.session_state.show_briefing = False
                st.rerun()
            except (InputError, ModelOutputError, ProviderError) as error:
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
