# 생활 상식첩

생활정보·질병·영양소·건강상식을 한 주제씩 깊이 있게 다루는 블로그형 정적 사이트.
100편(카테고리당 25편) 작성 완료. 진행 상황은 `TOPICS.md`.

## 공개
- GitHub Pages: 저장소를 Public 으로 바꾸고 Settings → Pages → Branch 를 이 브랜치의 `/ (root)` 로 지정하면 `index.html` 이 https://sogood5925-gif.github.io/sangsik/ 에 공개된다. `.nojekyll` 이 있어 그대로 서빙된다.
- 아티팩트: 페이지의 공유 메뉴에서 '링크가 있는 모든 사람'으로 바꾸면 공개된다.
- 댓글: utterances(GitHub Issues). 글마다 `post-<id>` 제목의 이슈에 댓글이 쌓인다. 쓰는 사람은 GitHub 로그인이 필요하다.
  저장소가 Public 이고 https://github.com/apps/utterances 앱이 이 저장소에 설치돼 있어야 동작한다. 삭제·관리는 저장소 Issues 에서 한다.
- 방문자 카운터: 사이드바 '방문자' 패널에 오늘·누적 표시. Abacus 카운터 API(`SITE.counter`, 키 `sangsik-total`, `sangsik-d-YYYYMMDD`). 브라우저당 하루 1회(localStorage) 센다. 불러오지 못하면 패널이 숨는다.
- 댓글과 카운터는 `src/shell.html` 의 `SITE` 설정을 쓰고 `*.github.io` 에서만 켜진다. 아티팩트에서는 CSP 때문에 외부 스크립트가 막혀 댓글 자리에 공개 사이트 링크만 보인다.

## 구조
- `posts/<id>.html` — 글 한 편. `<template>` 한 개로 감싼다.
- `posts/order.txt` — 글 순서(오래된 글이 위). 새 글은 맨 아래에 추가.
- `src/shell.html` — 블로그 틀(메뉴, 목록, 글 보기, 사이드바). `<!-- POSTS -->` 자리에 글이 들어간다.
- `python3 build.py` — 검사 후 `index.html`(공개용 전체 문서)과 `.build/artifact.html`(아티팩트용) 생성.
  글을 추가하거나 고친 뒤에는 반드시 빌드해서 `index.html` 을 함께 커밋한다.
- 아티팩트 주소: https://claude.ai/artifact/177b1rbKTWKaL9jiVGnnUt (`.build/artifact.html` 을 이 url 로 게시)

## 글 머리 속성 (모두 필수)
```html
<template data-id="iron" data-cat="nut" data-date="2026.09.29"
  data-title="철분 총정리: ..."
  data-thumb="큰글자|작은글자"
  data-summary="목록에 보일 2~3문장 요약"
  data-tags="철분,빈혈,...">
```
- `data-cat`: life(생활정보) · dis(질병) · nut(영양소) · hea(건강상식)
- `data-thumb`: 썸네일에 들어갈 그 주제만의 숫자나 기호 (예: `5°C|냉장 기준`, `140/90|고혈압 기준`). 큰 글자는 6자 안팎.
- `data-date`: 실제 작성한 날짜.

## 글 형식
순서: `p.lead` 도입 → `div.box.sum` "이 글의 핵심" → `h2` 본문 섹션 8~11개 → `h2 자주 묻는 질문`(`dl.qa`) → `h2 참고 자료`(`ul.refs`).
- 쓸 수 있는 요소: `h2`, `h3`, `p`, `ul/ol`, `strong`(형광 밑줄), `div.box.sum|note|warn` + `span.h` 제목,
  `div.tbl > table`(+`caption` 에 출처), `td.num`(숫자 칸), `dl.qa`.
- 분량: 읽는 데 6~8분(본문 공백 제외 3,000~4,500자 안팎). 표 2개 이상, 체크리스트나 실천 목록 1개 이상.
- 말투: 해요체. 가르치려 들지 않고 친절하게. 짧고 분명한 문장.
- 건강 글에는 사이트가 자동으로 면책 문구를 붙인다. 응급 신호는 `box.warn` 으로.

## 정확성 원칙 (외부 공개용이므로 가장 중요)
- 수치·기준은 공공기관·학회 자료(식약처, 질병관리청, 보건복지부·한국영양학회 섭취기준, 각 학회 진료지침, WHO, NIH 등)에 근거하고 표 `caption` 이나 참고 자료에 출처를 적는다.
- 확실하지 않은 숫자는 쓰지 않거나 범위·"약"으로 표현하고, 기관마다 기준이 다르면 다르다고 적는다.
- 해마다 바뀌는 금액(요금 단가, 지원금 등)은 구체 금액 대신 구조와 확인 방법을 쓴다.
- 특정 상품·브랜드를 권하지 않는다. 치료를 대신하는 듯한 표현, 과장된 효능 표현을 쓰지 않는다.
- 약은 성분명으로 쓰고, 복용 변경은 의사·약사와 상의하라고 안내한다.
