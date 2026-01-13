import urllib.request
import xml.etree.ElementTree as ET
import re
import urllib.parse
from datetime import datetime

# ================= CONFIG =================

MAX_HIGHLIGHTS = 8
MAX_RELEASE_NOTES = 5
MAX_VIDEOS = 5

SOURCES = [
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("The Verge AI", "https://www.theverge.com/artificial-intelligence/rss/index.xml"),
]

FALLBACK_HIGHLIGHTS = [
    ("OpenAI", "ChatGPT roadmap and platform updates", "https://openai.com/news"),
    ("Anthropic", "Claude models and agent capabilities", "https://www.anthropic.com/news"),
    ("Microsoft", "Copilot and AI platform evolution", "https://www.microsoft.com/blog"),
]

VIDEO_SUGGESTIONS = [
    ("Fireship", "AI Agents explained in 8 minutes"),
    ("Google Developers", "Google AI roadmap explained"),
    ("Anthropic", "Claude models & agents overview"),
    ("Notion", "Automating workflows with AI agents"),
    ("TechCrunch", "Breaking changes in AI APIs"),
]

RELEASE_NOTES_DATA = [
    ("12 jan 2026", "ChatGPT", "Melhorias de ditação e precisão.", "https://openai.com/news"),
    ("15 jan 2026", "ChatGPT macOS", "Funcionalidade Voice será descontinuada.", "https://openai.com"),
    ("11 jan 2026", "Claude", "Expansão para Healthcare & Life Sciences.", "https://www.anthropic.com/news"),
    ("5 jan 2026", "Claude API", "Modelo Opus 3 removido; migrar para Opus 4.5.", "https://docs.anthropic.com"),
    ("jan 2026", "Slack", "Melhorias em Huddles e workflows privados.", "https://slack.com/updates"),
]

# ================= UTILS =================

def clean(text: str) -> str:
    return re.sub(r"[<>]", "", text).strip()

def fetch_rss(url, limit=5):
    try:
        with urllib.request.urlopen(url, timeout=20) as f:
            data = f.read()
        root = ET.fromstring(data)
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            if title and link:
                items.append((clean(title), link))
        return items[:limit]
    except Exception:
        return []

# ================= HTML BUILDERS =================

def highlight_card(title, source, link):
    return f"""
    <a class="card" href="{link}" target="_blank" rel="noopener">
        <span class="tag">{source}</span>
        <h3>{title}</h3>
        <p>Atualização relevante publicada por {source}.</p>
        <span class="cta">Ler na fonte →</span>
    </a>
    """

def video_card(channel, title):
    query = urllib.parse.quote_plus(f"{channel} {title}")
    link = f"https://www.youtube.com/results?search_query={query}"
    return f"""
    <a class="card" href="{link}" target="_blank" rel="noopener">
        <strong>▶ {channel}</strong>
        <p>{title}</p>
        <span class="cta">Ver no YouTube →</span>
    </a>
    """

def release_row(date, tool, change, link):
    return f"""
    <tr>
        <td>{date}</td>
        <td>{tool}</td>
        <td>{change}</td>
        <td><a href="{link}" target="_blank" rel="noopener">Fonte</a></td>
    </tr>
    """

# ================= MAIN =================

def main():
    today = datetime.now().strftime("%d %b %Y")

    highlights = []
    links = []
    videos = []
    releases = []

    # ---- HIGHLIGHTS (RSS) ----
    for source, url in SOURCES:
        for title, link in fetch_rss(url, limit=4):
            if len(highlights) < MAX_HIGHLIGHTS:
                highlights.append(highlight_card(title, source, link))
            links.append(f"<li><a href='{link}' target='_blank'>{title}</a></li>")

    # ---- FALLBACK (garante conteúdo) ----
    for source, title, link in FALLBACK_HIGHLIGHTS:
        if len(highlights) < MAX_HIGHLIGHTS:
            highlights.append(highlight_card(title, source, link))
            links.append(f"<li><a href='{link}' target='_blank'>{title}</a></li>")

    # ---- RELEASE NOTES ----
    for row in RELEASE_NOTES_DATA[:MAX_RELEASE_NOTES]:
        releases.append(release_row(*row))

    # ---- VIDEOS ----
    for channel, title in VIDEO_SUGGESTIONS[:MAX_VIDEOS]:
        videos.append(video_card(channel, title))

    # ---- WHAT IT MEANS ----
    what_it_means = """
    <div class="card">
        <h3>Impacto prático</h3>
        <p>
        A IA está a evoluir rapidamente de chat para execução real de tarefas.
        Governança, custos e gestão de <em>breaking changes</em> tornam-se fatores
        críticos para equipas técnicas em 2026.
        </p>
    </div>
    """

    # ---- TEMPLATE ----
    with open("template.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{DATE}}", today)
    html = html.replace("{{HIGHLIGHTS}}", "\n".join(highlights))
    html = html.replace("{{WHAT_IT_MEANS}}", what_it_means)
    html = html.replace("{{RELEASE_NOTES}}", "\n".join(releases))
    html = html.replace("{{VIDEOS}}", "\n".join(videos))
    html = html.replace("{{LINKS}}", "\n".join(links))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

# ================= RUN =================

if __name__ == "__main__":
    main()
