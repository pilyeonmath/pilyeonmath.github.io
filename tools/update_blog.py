"""네이버 블로그 RSS에서 최신 글을 읽어 index.html의 블로그 섹션을 갱신한다.

index.html 안의 <!-- BLOG:START --> 와 <!-- BLOG:END --> 사이만 바꾼다.
검색엔진이 그대로 읽을 수 있도록 글 목록은 정적 HTML로 들어간다.

사용법: python tools/update_blog.py
"""

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

RSS_URL = "https://rss.blog.naver.com/py_math.xml"
COUNT = 3
ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
START, END = "<!-- BLOG:START -->", "<!-- BLOG:END -->"


def fetch_posts():
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as res:
        channel = ET.fromstring(res.read()).find("channel")
    posts = []
    for item in channel.findall("item")[:COUNT]:
        title = item.findtext("title", "").strip()
        title = re.sub(r"^\[필연수학학원\]\s*", "", title)
        summary = re.sub(r"<[^>]+>", " ", item.findtext("description", ""))
        summary = re.sub(r"\s+", " ", summary).strip()
        summary = re.sub(r"^안녕하세요\.\s*필연수학학원입니다\.\s*", "", summary)
        posts.append({
            "title": title,
            "link": item.findtext("link", "").split("?")[0],
            "category": item.findtext("category", "").strip() or "소식",
            "date": parsedate_to_datetime(item.findtext("pubDate")),
            "summary": summary[:90] + ("…" if len(summary) > 90 else ""),
        })
    return posts


def render(posts):
    cards = []
    for p in posts:
        d = p["date"]
        cards.append(
            f'        <a class="post reveal" href="{html.escape(p["link"])}" target="_blank" rel="noopener">\n'
            f'          <span class="k">{html.escape(p["category"])}</span>\n'
            f'          <h3>{html.escape(p["title"])}</h3>\n'
            f'          <p>{html.escape(p["summary"])}</p>\n'
            f'          <time datetime="{d:%Y-%m-%d}">{d.year}. {d.month}. {d.day}.</time>\n'
            f"        </a>"
        )
    return f"{START}\n" + "\n".join(cards) + f"\n        {END}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    posts = fetch_posts()
    if not posts:
        print("RSS에 글이 없습니다. 변경하지 않습니다.")
        return
    page = INDEX.read_text(encoding="utf-8")
    block = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not block.search(page):
        sys.exit("index.html에서 블로그 표시(BLOG:START/END)를 찾지 못했습니다.")
    updated = block.sub(lambda _: render(posts), page)
    if updated != page:
        INDEX.write_text(updated, encoding="utf-8", newline="\n")
        latest = posts[0]["date"].strftime("%Y-%m-%d")
        if SITEMAP.exists():
            sm = SITEMAP.read_text(encoding="utf-8")
            sm = re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{latest}</lastmod>", sm, count=1)
            SITEMAP.write_text(sm, encoding="utf-8", newline="\n")
        print(f"블로그 섹션을 갱신했습니다. 최신 글: {posts[0]['title']}")
    else:
        print("새 글이 없습니다.")


if __name__ == "__main__":
    main()
