import urllib.request
import xml.etree.ElementTree as ET
import re

SOURCES = [
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("Anthropic", "https://www.anthropic.com/news/rss.xml"),
    ("The Verge AI", "https://www.theverge.com/artificial-intelligence/rss/index.xml"),
]

def fetch_rss(url, limit=3):
    try:
        with urllib.request.urlopen(url, timeout=20) as f:
            data = f.read()
        root = ET.fromstring(data)
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            if title and link:
                items.append((title, link))
        return items[:limit]
    except Exception:
        return []

def li(text):
    return f"<li>{text}</li>"

def clean(text):
    return re.sub(r"[<>]", "", text)

def main():
    highlights = []
    links = []

    for name, url in SOURCES:
        items = fetch_rss(url)
        for title, link in items:
            highlights.append(
                li(
                    f"<strong>{clean(name)}:</strong> "
                    f"<a href='{link}' target='_blank'>{clean(title)}</a>"
                )
            )
            links.append(
                li(f"<a href='{link}' target='_blank'>{clean(title)}</a>")
            )

    if not highlights:
        highlights.append(li("Sem novidades relevantes encontradas hoje."))

    release_notes = [
        li("ChatGPT: acompanhar release notes oficiais"),
        li("Gemini: atenção a mudanças de API e billing"),
        li("Anthropic: evolução contínua dos modelos Claude"),
    ]

    what_it_means = [
        li("IA está a evoluir de chat para execução real de tarefas"),
        li("Automação exige controlo de permissões e auditoria"),
        li("Custos e breaking changes de API tornam-se críticos"),
    ]

    with open("template.html", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{HIGHLIGHTS}}", "\n".join(highlights))
    html = html.replace("{{RELEASE_NOTES}}", "\n".join(release_notes))
    html = html.replace("{{WHAT_IT_MEANS}}", "\n".join(what_it_means))
    html = html.replace("{{LINKS}}", "\n".join(links))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()

