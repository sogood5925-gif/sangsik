#!/usr/bin/env python3
"""posts/*.html 을 src/shell.html 에 끼워 index.html(공개용)과 .build/artifact.html(아티팩트용)을 만든다."""
import os, re, sys

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
        chunks.append(src)
    if errors:
        sys.exit('\n'.join(errors))
    shell = open(os.path.join(ROOT, 'src/shell.html'), encoding='utf-8').read()
    page = shell.replace('<!-- POSTS -->', '\n\n'.join(chunks))
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    # 아티팩트는 문서 골격을 스스로 씌우므로 골격 줄을 뺀다
    drop = ('<!doctype html>', '<html lang="ko">', '<head>', '<meta charset="utf-8">',
            '<meta name="viewport"', '</head>', '<body>', '</body>', '</html>')
    os.makedirs(os.path.join(ROOT, '.build'), exist_ok=True)
    open(os.path.join(ROOT, '.build/artifact.html'), 'w', encoding='utf-8').write(
        '\n'.join(l for l in page.split('\n') if not l.startswith(drop)))
    print(f'글 {len(chunks)}편 · 생활정보 {counts["life"]} · 질병 {counts["dis"]} · '
          f'영양소 {counts["nut"]} · 건강상식 {counts["hea"]} · {len(page)//1024}KB')

if __name__ == '__main__':
    main()
