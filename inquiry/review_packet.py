"""Offline, printable human-review packet built only from committed session data."""

from html import escape

from inquiry.core import AREAS, Session
from inquiry.analysis import analysis_markdown


_STYLE = """:root { color-scheme: light; --ink: #242622; --muted: #67695f; --line: #deded3; --accent: #a43c2d; }
* { box-sizing: border-box; }
html { background: #f3f2ec; color: var(--ink); }
body { margin: 0; font-family: 'Noto Sans', 'Noto Sans CJK SC', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 15px; line-height: 1.65; }
.paper { max-width: 1000px; margin: 36px auto; padding: 54px 64px; background: #fffefa; border: 1px solid var(--line); }
.masthead { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 2px solid var(--ink); gap: 20px; }
.brand { font-size: 25px; font-weight: 750; letter-spacing: -.8px; }
.brand::before { content: ''; display: inline-block; width: 9px; height: 9px; background: var(--accent); border-radius: 50%; margin-right: 10px; vertical-align: middle; }
.eyebrow { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.4px; color: var(--muted); }
h1 { font-size: clamp(30px, 4vw, 44px); line-height: 1.2; letter-spacing: -1.2px; margin: 34px 0 14px; font-weight: 650; }
.intro { color: var(--muted); max-width: 680px; margin-top: 0; }
.boundary { border-left: 3px solid var(--accent); background: #f6f0e9; padding: 16px 20px; margin: 26px 0; }
.boundary p { margin: 0; }
.print-help { color: var(--muted); font-size: 12px; margin: 18px 0 32px; }
section { margin-top: 32px; }
.section-head { display: flex; align-items: baseline; gap: 14px; padding-top: 22px; border-top: 1px solid var(--line); margin-bottom: 16px; }
.number { color: var(--accent); font-size: 12px; font-weight: 700; letter-spacing: 1px; }
h2 { margin: 0; font-size: 22px; font-weight: 650; line-height: 1.3; }
h3 { margin: 0 0 12px; font-size: 16px; line-height: 1.4; font-weight: 650; }
.source-label { color: var(--muted); font-size: 11px; letter-spacing: .4px; margin: 0 0 6px; }
.verbatim { white-space: pre-wrap; overflow-wrap: anywhere; word-break: normal; margin: 0; }
.context { background: #f5f5ef; padding: 20px 22px; border: 1px solid var(--line); }
.follow-up { margin-top: 18px; padding: 18px 22px; border-left: 2px solid var(--ink); }
.areas { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.area { border: 1px solid var(--line); padding: 20px; min-width: 0; }
.area:last-child { grid-column: 1 / -1; }
blockquote { margin: 14px 0 0; border-left: 2px solid #bebeb0; padding-left: 14px; }
.unknown { color: var(--muted); font-size: 13px; margin-bottom: 0; }
.next-steps { background: #eef0e8; padding: 20px 22px; }
.transcript-item { padding: 18px 0; border-bottom: 1px solid var(--line); }
.transcript-item:last-child { border-bottom: none; }
.transcript-item.assistant { padding-left: 20px; border-left: 2px solid var(--line); margin-top: 8px; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 12px; table-layout: fixed; }
th, td { text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); padding: 11px 8px; overflow-wrap: anywhere; white-space: pre-wrap; }
th { background: #f0f1e9; font-weight: 650; }
th:first-child { width: 9%; }
th:nth-child(4) { width: 29%; }
th:last-child { width: 17%; }
.footer { border-top: 2px solid var(--ink); margin-top: 34px; padding-top: 16px; color: var(--muted); font-size: 11px; }
@media (max-width: 680px) { .paper { margin: 0; padding: 28px 22px; border: 0; } .areas { grid-template-columns: 1fr; } .masthead { align-items: start; } }
@page { size: A4; margin: 16mm 17mm; }
@media print {
  html, body { background: #fff; color: #000; font-size: 10pt; }
  .paper { max-width: none; margin: 0; padding: 0; border: 0; background: #fff; }
  .print-help { display: none; }
  h1 { font-size: 28pt; }
  h2 { font-size: 16pt; }
  .section-head, h3, .source-label { break-after: avoid; }
  .area, .boundary, .follow-up, .next-steps { break-inside: avoid; }
  .areas { display: block; }
  .area { margin-bottom: 10px; }
  .verbatim { orphans: 3; widows: 3; }
  .table-wrap { overflow: visible; }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
  th, td { font-size: 8pt; }
  section { margin-top: 22px; }
  .footer { break-inside: avoid; }
}
"""


def _text(value):
    """All session-derived data enters the document as text, never markup."""
    return escape(str(value), quote=True)


def build_review_packet(session: Session, language="English") -> str:
    """Return self-contained HTML for human review; no network calls or mutation.

    The same two-user-turn threshold and explanatory boundary as ``briefing``
    apply. Quotes are retained only when present verbatim in a user message.
    Missing provenance remains missing rather than being inferred.
    """
    briefing = session.briefing(language)  # Uses the existing minimum-turn rule.
    zh = language == "中文"

    def label(english, chinese):
        return chinese if zh else english

    def section_head(number, title):
        return f'<div class="section-head"><span class="number">{number:02}</span><h2>{title}</h2></div>'

    # These fixed boundary/next-step passages are sourced from Session.briefing,
    # so this export does not introduce a second set of ethical instructions.
    briefing_parts = briefing.split("\n\n")
    boundary = briefing_parts[1]
    next_steps = briefing_parts[-1]
    user_messages = []
    for message in session.messages:
        if message["role"] == "user":
            user_messages.append((len(user_messages) + 1, message["content"]))
    original = user_messages[0][1]
    latest_question = next((m["content"] for m in reversed(session.messages) if m["role"] == "assistant"), None)

    groups = []
    for key, labels in AREAS.items():
        quotes = []
        seen = set()
        for observation in session.observations:
            if not isinstance(observation, dict) or observation.get("area") != key:
                continue
            quote = observation.get("quote")
            if not isinstance(quote, str) or not quote or quote in seen:
                continue
            sources = [str(turn) for turn, content in user_messages if quote in content]
            if not sources:
                continue
            seen.add(quote)
            attribution = label("User-reported excerpt · User turn ", "用户陈述原文 · 用户轮次 ") + ", ".join(sources)
            quotes.append(f'<blockquote><p class="source-label">{_text(attribution)}</p><p class="verbatim">{_text(quote)}</p></blockquote>')
        unknown = label(
            "Unknown / no statement extracted. Check the full transcript; this is not evidence that the issue is absent.",
            "尚未提取到相关陈述；请核对完整对话，不代表不存在相关事实。",
        )
        body = "".join(quotes) if quotes else f'<p class="unknown">{_text(unknown)}</p>'
        groups.append(f'<article class="area"><h3>{_text(labels[int(zh)])}</h3>{body}</article>')

    transcript = []
    turn = 0
    for message in session.messages:
        role = message["role"]
        if role == "user":
            turn += 1
        if role == "user":
            speaker = label("User-reported statement", "用户陈述")
        elif role == "assistant":
            speaker = label("Assistant follow-up question", "助手追问")
        else:
            speaker = _text(role)
        role_class = "assistant" if role == "assistant" else "user"
        turn_label = label("Turn ", "轮次 ")
        transcript.append(f'<article class="transcript-item {role_class}"><p class="source-label">{turn_label}{turn} · {speaker}</p><p class="verbatim">{_text(message["content"])}</p></article>')

    fields = ("turn", "provider", "model", "time", "regenerations")
    columns = (label("Turn", "轮次"), label("Provider", "服务提供方"), label("Model", "模型"), label("Recorded time", "记录时间"), label("Regenerations", "重新生成次数"))
    missing = label("Not recorded", "未记录")
    rows = []
    for record in session.records:
        cells = "".join(f'<td>{_text(record[field] if field in record and record[field] is not None else missing)}</td>' for field in fields)
        rows.append(f"<tr>{cells}</tr>")
    if rows:
        provenance = '<div class="table-wrap"><table><thead><tr>' + "".join(f'<th scope="col">{column}</th>' for column in columns) + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>'
    else:
        provenance = f'<p class="unknown">{label("No model provenance records available.", "暂无模型来源记录。")}</p>'

    semantic = ('<section><h2>'+label("Five-dimensional context and guidance", "五维信息与初步建议")+'</h2><p class="verbatim">'+_text(analysis_markdown(session.analysis,language))+'</p></section>') if session.analysis.get("facts") else ""
    title = label("Human-review briefing", "人工复核简报")
    question = _text(latest_question) if latest_question is not None else label("No follow-up question recorded.", "尚未记录追问。")
    return f'''<!doctype html>
<html lang="{'zh-CN' if zh else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Inquire — {title}</title>
<style>{_STYLE}</style>
</head>
<body>
<main class="paper">
<header class="masthead"><div class="brand">Inquire</div><div class="eyebrow">{label("Objectivity · Educational inquiry", "客观性 · 学习探究")}</div></header>
<h1>{title}</h1>
<p class="intro">{label("A record of the situation, the questions raised, and the statements available for an independent human review.", "整理情境、追问与已提供的陈述，供独立人工复核参考。")}</p>
<aside class="boundary"><p>{_text(boundary)}</p></aside>
<p class="print-help">{label("Save this HTML file for offline review. Use your browser’s Print command (Ctrl+P / ⌘P) to print or save as PDF.", "可保存此 HTML 文件供离线复核。使用浏览器的打印功能（Ctrl+P / ⌘P）打印或另存为 PDF。")}</p>
<section>{section_head(1, label("Situation and current question", "情境与当前追问"))}
<div class="context"><p class="source-label">{label("Original scenario · User-reported", "最初情境 · 用户陈述")}</p><p class="verbatim">{_text(original)}</p></div>
<div class="follow-up"><p class="source-label">{label("Current follow-up · Assistant-generated", "当前追问 · 助手生成")}</p><p class="verbatim">{question}</p></div>
</section>
<section>{section_head(2, label("User-reported excerpts by inquiry area", "按探究主题整理的用户原文"))}
<p class="intro">{label("Literal excerpts from user messages. Unknowns remain unknown; an extracted statement is not a completed check or a cleared issue.", "摘录保留用户消息的原文。未知仍是未知；提取到陈述不代表已完成检查或已排除相关问题。")}</p>
<div class="areas">{''.join(groups)}</div></section>
{semantic}
<section>{section_head(3, label("Human next steps", "人工下一步"))}<div class="next-steps"><p class="verbatim">{_text(next_steps)}</p></div></section>
<section>{section_head(4, label("Full conversation transcript", "完整对话记录"))}{''.join(transcript)}</section>
<section>{section_head(5, label("Model provenance", "模型来源记录"))}
<p class="intro">{label("Recorded generation metadata, in record order. Missing values are not inferred. The transcript contains the retained questions; earlier regenerated wording is not stored.", "按原记录顺序列出生成信息，不推断缺失值。对话中保留的是当前问题；先前被重新生成替换的措辞未保存。")}</p>{provenance}</section>
<footer class="footer">Inquire · {label("Focus: objectivity. Educational use only. Human judgment and verification remain necessary.", "聚焦客观性，仅供学习使用，仍须人工判断与核实。")}</footer>
</main>
</body>
</html>'''
