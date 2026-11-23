#!/usr/bin/env python3
"""Build the academy's self-contained A4 elevator poster.

Requires fonttools[woff] and qrcode. See print/elevator-poster/README.md.
"""

from __future__ import annotations

import argparse
import base64
from html import escape
from io import BytesIO
from pathlib import Path

import qrcode
from fontTools import subset
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "print" / "elevator-poster"
INK = "#111111"
BLUE = "#0071e3"
TEXT = [
    # x, baseline, type size, weight, copy, fill, tracking, alignment
    (124, 83, 29, 700, "필연수학학원", INK, -1.0, "start"),
    (125, 105, 13, 500, "수학은 필연입니다.", "#5c5c62", -0.25, "start"),
    (784, 83, 17, 700, "초등 · 중등 · 고등", INK, -0.4, "end"),
    (56, 225, 62, 700, "변화하는 시대,", INK, -2.5, "start"),
    (53, 313, 80, 900, "살아남는 실력.", INK, -3.8, "start"),
    (56, 377, 39, 700, "수학으로 키웁니다.", BLUE, -1.5, "start"),
    (56, 493, 25, 700, "스스로 생각하고,", INK, -0.7, "start"),
    (56, 530, 25, 700, "낯선 문제를 풀어내는 힘.", INK, -0.7, "start"),
    (56, 580, 18, 400, "공식의 이유를 이해하는 수업으로", "#56565c", -0.35, "start"),
    (56, 608, 18, 400, "처음 보는 문제 앞에서도 단단하게.", "#56565c", -0.35, "start"),
    (56, 728, 22, 700, "초등의 기초부터, 내신과 수능까지.", INK, -0.6, "start"),
    (56, 759, 17, 500, "KAIST 수리과학과 출신 원장 · KAIST 출신 선생님 다수", "#56565c", -0.25, "start"),
    (56, 786, 17, 500, "영재고 · 과학고 출신 선생님 재직", "#56565c", -0.25, "start"),
    (63, 956, 116, 900, "6", "#ffffff", -4.0, "start"),
    (139, 949, 42, 700, "층", "#ffffff", -1.0, "start"),
    (239, 911, 43, 700, "601호 · 603호", "#ffffff", -1.5, "start"),
    (241, 948, 18, 500, "해온프라자더파크", "#d2d2d7", -0.3, "start"),
    (68, 1014, 15, 500, "입학 · 상담 문의", "#d2d2d7", -0.2, "start"),
    (65, 1056, 39, 700, "032-832-2615", "#ffffff", -0.6, "start"),
    (68, 1088, 20, 500, "010-7652-2615", "#d2d2d7", 0.0, "start"),
    (724, 1109, 13, 500, "홈페이지 · 상담 안내", "#ffffff", -0.2, "middle"),
    (56, 1159, 11, 400, "인천 연수구 신송로 157-20  |  학원 설립·운영 등록 제4145호", "#6e6e73", -0.1, "start"),
    (784, 1159, 12, 700, "pymath.kr", "#6e6e73", 0.0, "end"),
]


def encoded(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def build(font_dir: Path) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    font_files = {400: "Regular", 500: "Medium", 700: "Bold", 900: "Black"}
    fonts = {
        weight: TTFont(font_dir / f"Pretendard-{name}.otf")
        for weight, name in font_files.items()
    }
    font_css = []
    for weight, name in font_files.items():
        font = TTFont(font_dir / f"Pretendard-{name}.otf")
        options = subset.Options()
        options.flavor = "woff2"
        sub = subset.Subsetter(options=options)
        sub.populate(text="".join(t[4] for t in TEXT if t[3] == weight))
        sub.subset(font)
        # Subsets are derivatives; respect the source's reserved font names.
        font_names = {
            1: "PY Poster Sans",
            2: name,
            3: f"PYPosterSans-{name}-PosterSubset",
            4: f"PY Poster Sans {name}",
            6: f"PYPosterSans-{name}",
            16: "PY Poster Sans",
            17: name,
        }
        for record in font["name"].names:
            if record.nameID in font_names:
                record.string = font_names[record.nameID].encode(record.getEncoding())
        font.flavor = "woff2"
        buf = BytesIO()
        font.save(buf)
        font_css.append(
            "@font-face {font-family:PYPosterSans;"
            f"font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff2;base64,{encoded(buf.getvalue())}) format('woff2');}}"
        )

    logo = encoded((ROOT / "assets" / "logo-mark.png").read_bytes())
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    qr.add_data("https://pymath.kr/")
    qr.make(fit=True)
    qr_matrix = qr.get_matrix()
    qr_size = len(qr_matrix)
    qr_path = " ".join(
        f"M{x} {y}h1v1h-1z"
        for y, row in enumerate(qr_matrix)
        for x, on in enumerate(row)
        if on
    )

    # The site's right triangle and incircle, with mathematically exact bisectors.
    side = 244
    radius = side * (2 - 2**0.5) / 2
    ix, iy = 538 + radius, 680 - radius
    diagonal_hit = 538 + side / 2
    bisector_hit = 538 + side * (2**0.5 - 1)
    geometry = f"""
    <g id="geometry" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M538 436V680H782Z" stroke="{INK}" stroke-width="2.2"/>
      <path d="M538 666H552V680" stroke="{INK}" stroke-width="1.2"/>
      <g stroke="#a6a6ac" stroke-width="1.2" stroke-dasharray="3 6">
        <path d="M538 436L{bisector_hit:.4f} 680"/>
        <path d="M782 680L538 {680-side*(2**0.5-1):.4f}"/>
        <path d="M538 680L{diagonal_hit:.4f} {680-side/2:.4f}"/>
      </g>
      <circle cx="{ix:.4f}" cy="{iy:.4f}" r="{radius:.4f}" stroke="{BLUE}" stroke-width="2.8"/>
      <circle cx="{ix:.4f}" cy="{iy:.4f}" r="5" fill="{BLUE}" stroke="white" stroke-width="2"/>
      <g fill="{INK}" stroke="white" stroke-width="1.5">
        <circle cx="538" cy="436" r="4"/><circle cx="538" cy="680" r="4"/><circle cx="782" cy="680" r="4"/>
      </g>
    </g>"""
    base = f"""
    <rect width="840" height="1188" fill="#ffffff"/>
    <image x="54" y="53" width="59" height="59" href="data:image/png;base64,{logo}"/>
    <path d="M56 139H784" stroke="#d2d2d7" stroke-width="1"/>
    {geometry}
    <rect x="40" y="816" width="760" height="312" fill="{INK}"/>
    <path d="M68 981H772" stroke="#454548" stroke-width="1"/>
    <a href="https://pymath.kr/" aria-label="필연수학학원 홈페이지">
      <svg x="674" y="993" width="100" height="100" viewBox="0 0 {qr_size} {qr_size}">
        <rect width="{qr_size}" height="{qr_size}" fill="white"/>
        <path d="{qr_path}" fill="{INK}"/>
      </svg>
    </a>"""

    editable = []
    outlined = []
    for x, y, size, weight, content, color, tracking, anchor in TEXT:
        font = fonts[weight]
        cmap = font.getBestCmap()
        glyphs = font.getGlyphSet()
        upm = font["head"].unitsPerEm
        scale = size / upm
        advances = [glyphs[cmap[ord(ch)]].width * scale for ch in content]
        width = sum(advances) + tracking * (len(content) - 1)
        offset = {"start": 0, "middle": width / 2, "end": width}[anchor]
        left = x - offset
        assert left >= 40 and left + width <= 800, (content, left, width)
        editable.append(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" letter-spacing="{tracking}" text-anchor="{anchor}">{escape(content)}</text>'
        )
        paths = []
        for ch, advance in zip(content, advances):
            pen = SVGPathPen(glyphs)
            glyphs[cmap[ord(ch)]].draw(pen)
            if commands := pen.getCommands():
                paths.append(
                    f'<path transform="translate({left:.5f} {y}) scale({scale:.8f} {-scale:.8f})" d="{commands}"/>'
                )
            left += advance + tracking
        outlined.append(f'<g fill="{color}" aria-label="{escape(content)}"><title>{escape(content)}</title>{"".join(paths)}</g>')

    svg_open = '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 840 1188" role="img" aria-labelledby="poster-title poster-desc">'
    svg_title = '<title id="poster-title">필연수학학원 — 변화하는 시대, 살아남는 실력.</title><desc id="poster-desc">수학으로 키웁니다. 초등·중등·고등. 6층 601호·603호. 상담 032-832-2615.</desc>'
    source_svg = svg_open + svg_title + "<style>" + "".join(font_css) + "text{font-family:PYPosterSans,sans-serif;font-kerning:none}</style>" + base + "".join(editable) + "</svg>"
    outline_svg = svg_open + svg_title + base + "".join(outlined) + "</svg>"
    (OUT / "poster-a4.svg").write_text(outline_svg, encoding="utf-8")
    html = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>필연수학학원 | 엘리베이터 A4 포스터</title>
<meta name="robots" content="noindex,nofollow">
<style>
*{box-sizing:border-box}html,body{margin:0;padding:0}body{background:#e7e7e9}
main{width:210mm;height:297mm;margin:28px auto;box-shadow:0 5px 35px #0002;background:white}
main>svg{display:block;width:100%;height:100%}
aside{max-width:210mm;margin:24px auto;font:14px/1.6 system-ui,sans-serif;color:#444}
aside a{color:inherit}aside button{font:inherit;padding:8px 14px;margin-right:12px;cursor:pointer;background:#111;color:white;border:0}
@page{size:A4 portrait;margin:0}
@media print{html,body{width:210mm;height:297mm;background:white;-webkit-print-color-adjust:exact;print-color-adjust:exact}main{margin:0;box-shadow:none;break-inside:avoid}aside{display:none}}
@media screen and (max-width:850px){main{width:calc(100vw - 24px);height:auto;aspect-ratio:210/297;margin:12px}aside{margin:12px}}
</style></head><body>
<aside><button type="button" onclick="window.print()">A4 인쇄</button><a href="poster-a4.pdf">인쇄용 PDF</a> · A4 세로 / 실제 크기 100% / 머리글·바닥글 없음</aside>
<main>""" + source_svg + "</main></body></html>"
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"Created {OUT / 'index.html'}")
    print(f"Created {OUT / 'poster-a4.svg'} (outlined type, no font dependency)")
    print(f"QR: https://pymath.kr/ — {qr_size} modules including 4-module quiet zone")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=Path.home() / "Library" / "Fonts")
    args = parser.parse_args()
    build(args.font_dir)
