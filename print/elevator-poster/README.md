# 필연수학학원 엘리베이터 포스터

- `poster-a4.pdf`: A4 세로 인쇄용. 210 × 297 mm, 1쪽.
- `poster-a4-300dpi.png`: 300 dpi 인쇄용 이미지.
- `preview.png`: 화면 확인용 이미지.
- `poster-a4.svg`: 글자를 윤곽선으로 변환한 벡터 편집 파일. 별도 글꼴 설치가 필요하지 않습니다.
- `index.html`: 글자와 글꼴을 포함한 독립형 원본. 브라우저에서 열어 확인하거나 인쇄할 수 있습니다.

## 인쇄

PDF에서 **A4 / 세로 / 실제 크기 100%**를 선택합니다. 내용은 용지 안쪽에 배치되어 있으며, 재단과 여백 없는 인쇄가 필요하지 않습니다. HTML로 인쇄할 때는 브라우저의 머리글·바닥글을 끕니다.

## 반영한 정보

- 메인 메시지: **변화하는 시대, 살아남는 실력. 수학으로 키웁니다.**
- 위치: 사용자 지시에 따라 **6층 601호 · 603호**를 사용했습니다.
- 강사진: KAIST 수리과학과 출신 원장, KAIST 출신 선생님 다수, 영재고·과학고 출신 선생님 재직.
- 학원명, 로고, 기하학 모티프, 초·중·고 과정, 원장·강사진, 상담번호, 주소, 등록번호는 저장소의 `index.html`과 `assets/logo-mark.png`를 기준으로 했습니다.
- 홈페이지 QR: `https://pymath.kr/` (4모듈 여백, 실제 크기 25 × 25 mm).
- 글꼴: 사이트와 같은 Pretendard. 포함된 글꼴 라이선스는 `FONT-LICENSE.txt`를 참고하세요.

## 수정 및 다시 만들기

`tools/build_poster.py`의 `TEXT`에서 문구·위치·크기를 수정합니다. 생성에는 Python, `fonttools[woff]`, `qrcode`와 Pretendard OTF Regular/Medium/Bold/Black이 필요합니다.

```sh
python3 tools/build_poster.py --font-dir /path/to/pretendard/fonts
```

이 명령은 HTML과 SVG를 만듭니다. PDF는 Chromium 또는 Chrome의 인쇄 기능으로 A4에 저장합니다. PNG는 최종 PDF를 300 dpi로 렌더링한 파일입니다.
