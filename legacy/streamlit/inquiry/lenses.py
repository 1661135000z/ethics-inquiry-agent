"""Display topics and literal user-statement counts, never ethical scores."""
from html import escape
from .core import AREAS

HELP = {
    'role': ('Clarify who is deciding, what they are responsible for and what remains unknown.', '厘清由谁作判断、承担什么职责，以及仍不确定的信息。'),
    'interests': ('Explore relationships or interests that could influence judgment.', '澄清可能影响判断的关系与利益。'),
    'pressure': ('Understand the source and effect of time, commercial or personal pressure.', '了解时间、商业或个人压力来自哪里，以及如何影响判断。'),
    'evidence': ('Identify records to verify and consider alternative explanations.', '寻找可核对的记录，并考虑其他解释。'),
    'review': ('Clarify who could review independently and what they would need to check.', '澄清谁能独立复核，以及需要检查什么。'),
    'scope': ('Connect the situation to an audit decision and objectivity.', '明确情境涉及的审计判断与客观性。'),
}
SHORT = {'role':('Role','角色'),'interests':('Interests','利益'), 'pressure':('Pressure','压力'),'evidence':('Evidence','证据'),'review':('Review','复核')}


def reported_quotes(session, area=None):
    """Return unique literal statements with their original user-turn references."""
    users = [m['content'] for m in session.messages if m.get('role') == 'user']
    found = []
    seen = set()
    for item in session.observations:
        if not isinstance(item, dict): continue
        topic, quote = item.get('area'), item.get('quote')
        if topic not in AREAS or (area and topic != area) or not isinstance(quote, str) or not quote:
            continue
        turns = [i+1 for i,text in enumerate(users) if quote in text]
        if not turns or (topic,quote) in seen: continue
        seen.add((topic,quote))
        found.append({'area':topic,'quote':quote,'turns':turns})
    return found


def area_counts(session):
    quotes = reported_quotes(session)
    return {area: sum(q['area']==area for q in quotes) for area in AREAS}


def focus_html(session, language='English'):
    zh = language == '中文'
    focus = session.focus if session.focus in HELP else 'scope'
    title = AREAS.get(focus,('Situation boundary','情境边界'))[int(zh)]
    eyebrow = '本轮探究方向' if zh else 'CURRENT INQUIRY LENS'
    return ('<div class="inquiry-lens"><span class="lens-dot" aria-hidden="true"></span>'
            '<div><span class="lens-eyebrow">'+eyebrow+'</span><strong>'+escape(title)+'</strong>'
            '<p>'+escape(HELP[focus][int(zh)])+'</p></div></div>')
