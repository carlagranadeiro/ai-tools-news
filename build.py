import urllib.request
import xml.etree.ElementTree as ET
import re
import urllib.parse
from datetime import datetime

# ================= CONFIG =================

MAX_HIGHLIGHTS = 5
MAX_RELEASE_NOTES = 5
MAX_VIDEOS = 8

SOURCES = [
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("The Verge AI", "https://www.theverge.com/artificial-intelligence/rss/index.xml"),
]

VIDEO_SUGGESTIONS = [
    ("Fireship", "AI Agents explained in 7 minutes"),
    ("Google Developers", "Google AI roadmap explained"),
    ("Anthropic", "Claude models & agents overview"),
    ("Notion", "Automating workflows with AI agents"),
    ("TechCrunch", "Breaking changes in AI APIs"),
]

RELEASE_NOTES_DATA = [
    ("12 jan 2026", "ChatGPT", "✍️ Melhorias claras de edição e precisão.", "https://openai.com/news"),
    ("15 jan 2026", "ChatGPT macOS", "🛑 Funcionalidade Voice será removida.", "https://openai.com"),
    ("11 jan 2026", "Claude", "🧬 Expansão para Healthcare & Life Sciences.", "https://www.anthropic.com/news"),
    ("5 jan 2026", "Claude API", "⚠️ Opus 3 removido → migrar para Opus 4.5.", "https://docs.anthropic.com"),
    ("jan 2026", "Slack", "💬 Melhorias visuais em Huddles.", "https://slack.com/updates"),
]

# ================= UTILS =================

def clean(text):
    return re.sub(r"[<>]", "", text).strip()

def fetch_rss(url, limit=4):
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
        <span class="tag">🚀 {source}</span>
        <h3>{title}</h3>
        <p><strong>NOTÍCIA IMPORTANTE</strong> — fonte: {source}</p>
        <span class="cta">👉 Abrir artigo</span>
    </a>
    """

def video_card(channel, title):
    query = urllib.parse.quote_plus(f"{channel} {title}")
    link = f"https://www.youtube.com/results?search_query={query}"
    return f"""
    <a class="card" href="{link}" target="_blank" rel="noopener">
        <h3>🎥 {channel}</h3>
        <p>{title}</p>
        <span class="cta">▶ Ver no YouTube</span>
    </a>
    """

def release_row(date, tool, change, link):
    return f"""
    <tr>
        <td>{date}</td>
        <td>🧩 {tool}</td>
        <td>{change}</td>
        <td><a href="{link}" target="_blank">Fonte</a></td>
    </tr>
    """

# ================= MAIN =================

def main():
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")

    highlights = []
    videos = []
    releases = []
    links = []

    # ---- HIGHLIGHTS ----
    for source, url in SOURCES:
        for title, link in fetch_rss(url):
            if len(highlights) < MAX_HIGHLIGHTS:
                highlights.append(highlight_card(title, source, link))
            links.append(f"<li><a href='{link}' target='_blank'>{title}</a></li>")

    # ---- RELEASE NOTES ----
    for row in RELEASE_NOTES_DATA:
        releases.append(release_row(*row))

    # ---- VIDEOS ----
    for channel, title in VIDEO_SUGGESTIONS:
        videos.append(video_card(channel, title))

    # ---- WHAT IT MEANS (DEBUG VISUAL) ----
    what_it_means = f"""
    <div class="card" style="background:rgba(122,162,255,0.15)">
        <h3>🧠 Impacto prático (DEBUG)</h3>
        <p>
        Esta página foi <strong>gerada automaticamente às {timestamp}</strong>.
        Se estás a ver este texto, o <code>build.py</code> está ativo e o pipeline funciona.
        </p>
    </div>
    """

    with open("template.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{HIGHLIGHTS}}", "\n".join(highlights))
    html = html.replace("{{WHAT_IT_MEANS}}", what_it_means)
    html = html.replace("{{RELEASE_NOTES}}", "\n".join(releases))
    html = html.replace("{{VIDEOS}}", "\n".join(videos))
    html = html.replace("{{LINKS}}", "\n".join(links))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
