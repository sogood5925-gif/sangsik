#!/usr/bin/env python3
"""posts/*.html 로 공개 사이트와 아티팩트를 만든다.

- 공개 사이트(GitHub Pages): index.html(첫 화면), <id>/index.html(글마다 개별 주소), 404.html,
  sitemap.xml, rss.xml, search.json — 틀은 src/page.html, 스크립트는 src/site.js
- 아티팩트: .build/artifact.html — 한 파일짜리 src/shell.html 에 글을 모두 끼운다
"""
import os, re, sys, json, html, shutil
from urllib.parse import quote
from html.parser import HTMLParser

VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'col', 'wbr'}

class TagCheck(HTMLParser):
    """열고 닫는 태그 짝이 맞는지 본다."""
    def __init__(self):
        super().__init__(); self.stack = []; self.errs = []
    def handle_starttag(self, tag, attrs):
        if tag not in VOID: self.stack.append((tag, self.getpos()[0]))
    def handle_endtag(self, tag):
        if tag in VOID: return
        if not self.stack or self.stack[-1][0] != tag:
            top = self.stack[-1] if self.stack else ('없음', 0)
            self.errs.append(f'{self.getpos()[0]}행 </{tag}> (열린 태그: <{top[0]}> {top[1]}행)')
            if any(t == tag for t, _ in self.stack):
                while self.stack and self.stack.pop()[0] != tag: pass
        else: self.stack.pop()


ROOT = os.path.dirname(os.path.abspath(__file__))
CATS = {'life', 'dis', 'nut', 'hea'}
REQ = ('data-id', 'data-cat', 'data-date', 'data-title', 'data-thumb', 'data-summary', 'data-tags')

def main():
    order = [l.strip() for l in open(os.path.join(ROOT, 'posts/order.txt'), encoding='utf-8')
             if l.strip() and not l.startswith('#')]
    if len(set(order)) != len(order):
        sys.exit('order.txt 에 중복된 글이 있어요')
    chunks, counts, errors = [], {c: 0 for c in CATS}, []
    for pid in order:
        path = os.path.join(ROOT, 'posts', pid + '.html')
        if not os.path.exists(path):
            errors.append(f'{pid}: 파일 없음'); continue
        src = open(path, encoding='utf-8').read().strip()
        head = re.match(r'<template\b([^>]*)>', src, re.S)
        if not head or not src.endswith('</template>'):
            errors.append(f'{pid}: <template> 로 감싸져 있지 않음'); continue
        attrs = dict(re.findall(r'(data-[a-z]+)="([^"]*)"', head.group(1)))
        missing = [a for a in REQ if a not in attrs]
        if missing: errors.append(f'{pid}: 속성 누락 {missing}')
        if attrs.get('data-id') != pid: errors.append(f'{pid}: data-id 불일치')
        if attrs.get('data-cat') not in CATS: errors.append(f'{pid}: 카테고리 오류')
        else: counts[attrs['data-cat']] += 1
        tc = TagCheck(); tc.feed(src); tc.close()
        errors += [f'{pid}: {e}' for e in tc.errs]
        errors += [f'{pid}: <{t}> {n}행이 닫히지 않음' for t, n in tc.stack]
        chunks.append(src)
    if errors:
        sys.exit('\n'.join(errors))
    shell = open(os.path.join(ROOT, 'src/shell.html'), encoding='utf-8').read()
    page = shell.replace('<!-- POSTS -->', '\n\n'.join(chunks))
    # 아티팩트는 문서 골격을 스스로 씌우므로 골격 줄을 뺀다
    drop = ('<!doctype html>', '<html lang="ko">', '<head>', '<meta charset="utf-8">',
            '<meta name="viewport"', '</head>', '<body>', '</body>', '</html>')
    os.makedirs(os.path.join(ROOT, '.build'), exist_ok=True)
    open(os.path.join(ROOT, '.build/artifact.html'), 'w', encoding='utf-8').write(
        '\n'.join(l for l in page.split('\n') if not l.startswith(drop)))
    css = re.search(r'<style>(.*?)</style>', shell, re.S).group(1)
    size = build_site(order, chunks, css)
    # TOPICS.md 체크 상태를 실제 글 파일과 맞춘다
    tp = os.path.join(ROOT, 'TOPICS.md')
    if os.path.exists(tp):
        done = set(order)
        t = re.sub(r'- \[[ x]\] (.*?) \(([a-z0-9-]+)\)',
                   lambda m: f'- [{"x" if m.group(2) in done else " "}] {m.group(1)} ({m.group(2)})',
                   open(tp, encoding='utf-8').read())
        open(tp, 'w', encoding='utf-8').write(t)
    print(f'글 {len(chunks)}편 · 생활정보 {counts["life"]} · 질병 {counts["dis"]} · '
          f'영양소 {counts["nut"]} · 건강상식 {counts["hea"]} · 사이트 {size//1024}KB · 아티팩트 {len(page)//1024}KB')

# ---------------------------------------------------------------- 공개 사이트
SITE = 'https://sogood5925-gif.github.io/sangsik/'
CAT = {'life': '생활정보', 'dis': '질병', 'nut': '영양소', 'hea': '건강상식'}
ORDER = ['life', 'dis', 'nut', 'hea']
KEEP = {'posts', 'src', '.build', '.git', '__pycache__', 'stats'}   # stats: 방문 통계 페이지(빌드가 만들지만 글이 아니에요)
E = lambda t: html.escape(t, quote=True)

def parse(src):
    attrs = {k[5:]: html.unescape(v) for k, v in
             re.findall(r'(data-[a-z]+)="([^"]*)"', re.match(r'<template\b([^>]*)>', src, re.S).group(1))}
    body = re.sub(r'^<template\b[^>]*>|</template>$', '', src, flags=re.S).strip()
    text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', body))).strip()
    th = attrs['thumb'].split('|')
    return dict(id=attrs['id'], cat=attrs['cat'], title=attrs['title'], date=attrs['date'],
                iso=attrs['date'].replace('.', '-'), sum=attrs['summary'],
                tags=[t for t in attrs['tags'].split(',') if t], big=th[0], small=th[1] if len(th) > 1 else '',
                body=body, text=text, min=max(1, round(len(text.replace(' ', '')) / 500)))

def thumb(p):
    return f'<div class="thumb t-{p["cat"]}" aria-hidden="true"><b>{E(p["big"])}</b><small>{E(p["small"])}</small></div>'

def menu(posts, root, cur):
    n = lambda c: sum(1 for p in posts if p['cat'] == c)
    a = lambda h, href, label, k: (f'<a href="{href}" data-h="{h}" aria-current="{"true" if h == cur else "false"}">'
                                   f'{label}<span class="n">({k})</span></a>')
    return a('home', root or './', '전체글', len(posts)) + ''.join(
        a('cat-' + c, f'{root}#cat-{c}', CAT[c], n(c)) for c in ORDER)

def side(posts, root, cur):
    n = lambda c: sum(1 for p in posts if p['cat'] == c)
    li = lambda h, href, label, k, sub='': (f'<li{sub}><a href="{href}" data-h="{h}" aria-current="{"true" if h == cur else "false"}">'
                                            f'<span>{label}</span><span>({k})</span></a></li>')
    cats = li('home', root or './', '전체보기', len(posts)) + ''.join(
        li('cat-' + c, f'{root}#cat-{c}', CAT[c], n(c), ' class="sub"') for c in ORDER)
    recent = ''.join(f'<li><a href="{root}{p["id"]}/">{E(p["title"])}</a></li>' for p in posts[:5])
    freq = {}
    for p in posts:
        for t in p['tags']: freq[t] = freq.get(t, 0) + 1
    tags = ''.join(f'<a href="{root or "./"}?q={quote(t)}">{E(t)}</a>'
                   for t in sorted(freq, key=lambda t: -freq[t])[:24])
    return f"""      <section class="panel profile">
        <div class="avatar" aria-hidden="true">상</div>
        <b>상식첩 편집실</b>
        <p>검색하면 나오는 한 줄짜리 상식 말고, 왜 그런지까지 알 수 있는 글을 씁니다. 공공기관과 학회 자료를 기준으로 정리해요.</p>
      </section>
      <section class="panel visits" id="visits" hidden>
        <h3>방문자</h3>
        <dl><dt>오늘</dt><dd id="v-today">-</dd><dt>누적</dt><dd id="v-total">-</dd></dl>
      </section>
      <section class="panel">
        <h3>블로그 검색</h3>
        <form class="sform" role="search" action="{root or './'}">
          <input id="q" name="q" type="search" placeholder="예: 혈압, 철분, 곰팡이" aria-label="블로그 글 검색">
          <button type="submit">검색</button>
        </form>
      </section>
      <section class="panel">
        <h3>카테고리</h3>
        <ul class="catlist">{cats}</ul>
      </section>
      <section class="panel">
        <h3>최근 글</h3>
        <ul class="recent">{recent}</ul>
      </section>
      <section class="panel">
        <h3>태그</h3>
        <div class="tagcloud">{tags}</div>
      </section>"""

def home_main(posts):
    items = ''.join(
        f'<li data-id="{p["id"]}" data-cat="{p["cat"]}"><a class="item" href="{p["id"]}/">'
        f'<div class="item-text"><span class="item-cat k-{p["cat"]}">{CAT[p["cat"]]}</span>'
        f'<span class="item-title">{E(p["title"])}</span><span class="item-sum">{E(p["sum"])}</span>'
        f'<span class="item-meta">{p["date"]} · 읽는 데 약 {p["min"]}분<span class="item-views" hidden></span></span></div>{thumb(p)}</a></li>\n'
        for p in posts)
    return (f'<div class="listhead"><h2 id="listtitle">전체글</h2><span id="listcount">{len(posts)}개의 글</span></div>\n'
            f'<ul class="postlist" id="postlist">\n{items}</ul>\n'
            '<p class="nohit" id="nohit" hidden>찾는 글이 없어요. 다른 낱말로 검색해 보세요.</p>\n'
            '<nav class="pager" id="pager" aria-label="페이지" hidden></nav>')

def post_main(p, posts):
    k = [0]
    def sec(m):
        k[0] += 1
        return f'<h2 id="sec{k[0]}">'
    body = re.sub(r'<h2>', sec, p['body'])
    heads = re.findall(r'<h2 id="(sec\d+)">(.*?)</h2>', body, re.S)
    toc = ''.join(f'<li><a href="#{i}">{E(html.unescape(re.sub("<[^>]+>", "", h)))}</a></li>' for i, h in heads)
    tags = ''.join(f'<span>#{E(t)}</span>' for t in p['tags'])
    dis = ('' if p['cat'] == 'life' else
           '<p class="disclaim">이 글은 일반적인 건강 정보를 정리한 것으로 개인의 진단이나 치료를 대신하지 않아요. '
           '증상이 있거나 약을 복용 중이라면 의사·약사와 상의하세요.</p>\n')
    rel = [x for x in posts if x['cat'] == p['cat'] and x is not p][:5]
    rel = ''.join(f'<li><a href="../{x["id"]}/">{E(x["title"])}</a></li>' for x in rel)
    i = posts.index(p)
    def pn(j, label):
        if 0 <= j < len(posts):
            o = posts[j]
            return f'<a href="../{o["id"]}/"><small>{label}</small><span>{E(o["title"])}</span></a>'
        return '<span></span>'
    return f"""<article class="post">
<a class="crumb k-{p['cat']}" href="../#cat-{p['cat']}">{CAT[p['cat']]}</a>
<h1 class="post-title">{E(p['title'])}</h1>
<div class="byline"><b>상식첩 편집실</b><span><time datetime="{p['iso']}">{p['date']}</time></span><span>읽는 데 약 {p['min']}분</span><span class="views" id="views" data-id="{p['id']}" hidden>조회 <b id="vcount">-</b></span></div>
<nav class="toc" aria-label="목차"><p>목차</p><ol>{toc}</ol></nav>
<div class="body">
{body}
</div>
<div class="tags">{tags}</div>
{dis}<div class="actions"><button type="button" class="like" data-id="{p['id']}" aria-pressed="false">♡ 공감하기</button></div>
</article>
<section class="comments" aria-label="댓글"><h3>댓글</h3>
<p class="cnote" id="cnote">GitHub 계정으로 로그인하면 댓글을 남길 수 있어요. 다른 분의 건강 상태에 대한 진단이나 처방은 답해 드리기 어려워요.</p>
<div id="cbox" data-term="post-{p['id']}"></div></section>
<section class="related"><h3>‘{CAT[p['cat']]}’ 카테고리의 다른 글</h3><ul>{rel}</ul></section>
<nav class="pn" aria-label="이전 글과 다음 글">{pn(i + 1, '이전 글')}{pn(i - 1, '다음 글')}</nav>"""

def stats_main(plist):
    seg = lambda gid, label, items: (f'<div class="seg" id="{gid}" role="group" aria-label="{label}">' +
                                     ''.join(f'<button type="button" data-k="{k}">{v}</button>' for k, v in items) + '</div>')
    periods = [('today', '오늘'), ('yday', '어제'), ('month', '이번 달'), ('lmonth', '지난 달'), ('total', '누적')]
    cats = [('all', '전체')] + [(c, CAT[c]) for c in ORDER]
    return f"""<div class="listhead"><h2>방문 통계</h2><span>한국 시간 기준</span></div>
<div class="stats">
<p class="st-off" id="st-off" hidden>방문 통계를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.</p>
<section><h3>방문자</h3>
<div class="tiles"><div><span>오늘</span><b id="s-today">-</b></div><div><span>어제</span><b id="s-yday">-</b></div><div><span>누적</span><b id="s-total">-</b></div></div>
</section>
<section><h3>어디서 들어왔을까</h3>
{seg('src-p', '기간', periods)}
<p class="st-sum" id="src-sum" aria-live="polite"></p>
<ol class="bars" id="src-bars"></ol>
<p class="st-help">방문자가 그날 처음 연 페이지의 직전 주소로 나눠요. 카카오톡·네이버 앱처럼 앱 안에서 연 경우는 앱 표시로 구별해요.
직전 주소를 보내지 않는 앱이나 주소를 직접 입력·즐겨찾기로 들어온 경우는 ‘직접 방문’으로 세요. 검색어는 알 수 없어요.</p>
</section>
<section><h3>글별 조회수</h3>
{seg('pv-cat', '카테고리', cats)}
<p class="st-sum" id="pv-state" aria-live="polite"></p>
<div class="tbl"><table class="pvt"><thead><tr><th class="num">순위</th><th>글</th><th class="num">조회</th></tr></thead><tbody id="pv-body"></tbody></table></div>
<p class="st-more"><button type="button" id="pv-more" hidden>더 보기</button></p>
<p class="st-help">같은 브라우저에서 같은 글은 하루에 한 번만 세요.</p>
</section>
<section><h3>검색어 확인</h3>
<p>어떤 검색어로 들어왔는지는 검색엔진이 알려 줘요.</p>
<ul class="st-links">
<li><a href="https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fsogood5925-gif.github.io%2Fsangsik%2F" target="_blank" rel="noopener">구글 서치 콘솔 → 실적(검색어·클릭 수)</a></li>
<li><a href="https://searchadvisor.naver.com/console/board" target="_blank" rel="noopener">네이버 서치어드바이저 → 리포트(검색 유입)</a></li>
</ul>
</section>
<section><h3>내 방문 빼기</h3>
<p id="me-note"></p>
<button type="button" class="me-btn" id="me-btn"></button>
</section>
</div>
<script type="application/json" id="plist">{plist}</script>"""

def build_site(order, chunks, css):
    tpl = open(os.path.join(ROOT, 'src/page.html'), encoding='utf-8').read()
    js = open(os.path.join(ROOT, 'src/site.js'), encoding='utf-8').read().strip()
    posts = [parse(c) for c in chunks][::-1]          # 최신 글이 위로
    ids = {p['id'] for p in posts}
    if ids & KEEP: sys.exit(f'글 아이디가 폴더 이름과 겹쳐요: {ids & KEEP}')

    def render(path, **v):
        out = tpl
        for k in ('TITLE', 'DESC', 'URL', 'OGTYPE', 'OGTITLE', 'ROOT', 'HEAD', 'CSS', 'BLOGNAME', 'MENU', 'MAIN', 'SIDE', 'JS'):
            out = out.replace('{{' + k + '}}', v.get(k, ''))
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, 'w', encoding='utf-8').write(out)
        return len(out)

    desc = '생활정보, 질병, 영양소, 건강상식 100편을 한 주제씩 깊이 있게 정리한 블로그'
    common = dict(CSS=css, JS=js)
    size = render('index.html', TITLE='생활 상식첩', DESC=E(desc), URL=SITE, OGTYPE='website', OGTITLE='생활 상식첩',
                  ROOT='', BLOGNAME='<h1 class="blogname"><a href="./">생활 상식첩</a></h1>',
                  MENU=menu(posts, '', 'home'), MAIN=home_main(posts), SIDE=side(posts, '', 'home'), **common)
    for p in posts:
        url = SITE + p['id'] + '/'
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'Article', 'headline': p['title'],
                         'description': p['sum'], 'datePublished': p['iso'], 'dateModified': p['iso'],
                         'author': {'@type': 'Organization', 'name': '상식첩 편집실'},
                         'publisher': {'@type': 'Organization', 'name': '생활 상식첩'},
                         'mainEntityOfPage': url, 'inLanguage': 'ko', 'keywords': ','.join(p['tags'])},
                        ensure_ascii=False).replace('</', '<\\/')
        render(f'{p["id"]}/index.html', TITLE=E(p['title'] + ' | 생활 상식첩'), DESC=E(p['sum']), URL=url,
               OGTYPE='article', OGTITLE=E(p['title']), ROOT='../',
               HEAD=(f'<meta name="keywords" content="{E(",".join(p["tags"]))}">\n'
                     f'<meta property="article:published_time" content="{p["iso"]}">\n'
                     f'<script type="application/ld+json">{ld}</script>\n'),
               BLOGNAME='<p class="blogname"><a href="../">생활 상식첩</a></p>',
               MENU=menu(posts, '../', 'cat-' + p['cat']), MAIN=post_main(p, posts),
               SIDE=side(posts, '../', 'cat-' + p['cat']), **common)
    # 없는 주소: GitHub Pages 가 어느 깊이에서나 보여 주므로 절대 주소로 링크한다
    render('404.html', TITLE='페이지를 찾을 수 없어요 | 생활 상식첩', DESC=E(desc), URL=SITE, OGTYPE='website',
           OGTITLE='생활 상식첩', ROOT='/sangsik/', HEAD='<meta name="robots" content="noindex">\n',
           BLOGNAME='<p class="blogname"><a href="/sangsik/">생활 상식첩</a></p>',
           MENU=menu(posts, '/sangsik/', None),
           MAIN=('<div class="listhead"><h2>페이지를 찾을 수 없어요</h2></div>'
                 '<p class="nohit">주소가 바뀌었거나 없는 글이에요. <a href="/sangsik/">첫 화면</a>에서 찾아보세요.</p>'),
           SIDE=side(posts, '/sangsik/', None), **common)
    # 방문 통계: 검색에 노출하지 않고 메뉴에도 넣지 않는 주인용 페이지. 스크립트는 src/stats.js
    plist = json.dumps([{'id': p['id'], 't': p['title'], 'c': p['cat']} for p in posts],
                       ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    render('stats/index.html', TITLE='방문 통계 | 생활 상식첩', DESC='생활 상식첩 방문 통계', URL=SITE + 'stats/',
           OGTYPE='website', OGTITLE='방문 통계', ROOT='../', HEAD='<meta name="robots" content="noindex,nofollow">\n',
           BLOGNAME='<p class="blogname"><a href="../">생활 상식첩</a></p>', MENU=menu(posts, '../', None),
           MAIN=stats_main(plist), SIDE=side(posts, '../', None), CSS=css,
           JS=open(os.path.join(ROOT, 'src/stats.js'), encoding='utf-8').read().strip())
    # 지난 빌드에서 만들었지만 지금은 없는 글 폴더를 지운다
    for d in os.listdir(ROOT):
        f = os.path.join(ROOT, d, 'index.html')
        if d not in ids and d not in KEEP and os.path.isfile(f) and 'content="sangsik-build"' in open(f, encoding='utf-8').read(600):
            shutil.rmtree(os.path.join(ROOT, d))
    json.dump({p['id']: ' '.join([p['title'], p['sum'], ' '.join(p['tags']), p['text']]).lower() for p in posts},
              open(os.path.join(ROOT, 'search.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    last = max(p['iso'] for p in posts)
    urls = [(SITE, last)] + [(SITE + p['id'] + '/', p['iso']) for p in posts]
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'<url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n' for u, d in urls) + '</urlset>\n')
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    rfc = lambda iso: format_datetime(datetime.fromisoformat(iso + 'T09:00:00').replace(tzinfo=timezone(timedelta(hours=9))))
    open(os.path.join(ROOT, 'rss.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        f'<title>생활 상식첩</title><link>{SITE}</link><description>{E(desc)}</description><language>ko</language>\n' +
        ''.join(f'<item><title>{E(p["title"])}</title><link>{SITE}{p["id"]}/</link><guid>{SITE}{p["id"]}/</guid>'
                f'<description>{E(p["sum"])}</description><category>{CAT[p["cat"]]}</category><pubDate>{rfc(p["iso"])}</pubDate></item>\n'
                for p in posts) + '</channel></rss>\n')
    return size

if __name__ == '__main__':
    main()
