import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# =========================
# CONFIGURAÇÃO
# =========================

MAX_HIGHLIGHTS = 5
MAX_RELEASE_NOTES = 5
MAX_VIDEOS = 5

SOURCES = [
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("Anthropic", "https://www.anthropic.com/news/rss.xml"),
    ("The Verge AI", "https://www.theverge.com/artificial-intelligence/rss/index.xml"),
]

VIDEO_SUGGESTIONS = [
    ("Fireship", "AI Agents explained in 8 minutes"),
    ("Google Developers", "Google AI roadmap explained"),
    ("Anthropic", "Claude models & agents overview"),
    ("Notion", "Automating workflows with AI agents"),
    ("TechCrunch", "Breaking changes in AI APIs"),
]

# =========================
# UTILITÁRIOS
# =========================

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

# =========================
# GERADORES DE HTML
# =========================

def card(title, content, link=None, tag=None):
    tag_html = f"<span class='tag'>{tag}</span>" if tag else ""
    link_html = f"<a href='{link}' target='_blank'>Ler mais →</a>" if link else ""
    return f"""
    <div class="card">
        {tag_html}
        <h3>{title}</h3>
        <p>{content}</p>
        {link_html}
    </div>
    """

def video_card(channel, title):
    return f"""
    <div class="card">
        <strong>▶ {clean(channel)}</strong><br>
        {clean(title)}
    </div>
    """

def table_row(date, tool, change):
    return f"""
    <tr>
        <td>{date}</td>
        <td>{tool}</td>
        <td>{change}</td>
    </tr>
    """

# =========================
# MAIN
# =========================

def main():
    today = datetime.now().strftime("%d %b %Y")

    highlights_html = []
    release_rows = []
    links_html = []

    # -------- HIGHLIGHTS + LINKS --------
    for source, url in SOURCES:
        items = fetch_rss(url, limit=2)
        for title, link in items:
            if len(highlights_html) < MAX_HIGHLIGHTS:
                highlights_html.append(
                    card(
                        title=title,
                        content=f"Atualização relevante publicada por {source}.",
                        link=link,
                        tag=source
                    )
                )
            links_html.append(
                f"<li><a href='{link}' target='_blank'>{title}</a></li>"
            )

    if not highlights_html:
        highlights_html.append(
            card("Sem novidades relevantes", "Não foram encontradas notícias relevantes hoje.")
        )

    # -------- RELEASE NOTES --------
    release_notes_data = [
        ("12 jan 2026", "ChatGPT", "Melhorias de ditação e precisão."),
        ("15 jan 2026", "ChatGPT macOS", "Funcionalidade Voice será descontinuada."),
        ("11 jan 2026", "Claude", "Expansão para Healthcare & Life Sciences."),
        ("5 jan 2026", "Claude API", "Modelo Opus 3 removido; migrar para Opus 4.5."),
        ("jan 2026", "Slack", "Melhorias em Huddles e workflows privados."),
    ]

    for row in release_notes_data[:MAX_RELEASE_NOTES]:
        release_rows.append(table_row(*row))

    # -------- WHAT IT MEANS --------
    what_it_means_html = card(
        "Impacto prático",
        """
        A IA está a mover-se rapidamente de chat para execução real de tarefas.
        Governança, custos e gestão de breaking changes tornam-se fatores críticos
        para equipas técnicas em 2026.
        """
    )

    # -------- VIDEOS --------
    videos_html = []
    for channel, title in VIDEO_SUGGESTIONS[:MAX_VIDEOS]:
        videos_html.append(video_card(channel, title))

    # -------- TEMPLATE --------
    with open("template.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{DATE}}", today)
    html = html.replace("{{HIGHLIGHTS}}", "\n".join(highlights_html))
    html = html.replace("{{WHAT_IT_MEANS}}", what_it_means_html)
    html = html.replace("{{RELEASE_NOTES}}", "\n".join(release_rows))
    html = html.replace("{{VIDEOS}}", "\n".join(videos_html))
    html = html.replace("{{LINKS}}", "\n".join(links_html))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

# =========================

if __name__ == "__main__":
    main()
