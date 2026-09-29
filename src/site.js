(function(){
  /* 공개 사이트 설정: 댓글(utterances, GitHub 이슈)과 방문자 수는 GitHub Pages 에서만 켜요 */
  var SITE={url:'https://sogood5925-gif.github.io/sangsik/', repo:'sogood5925-gif/sangsik', counter:'https://abacus.jasoncameron.dev/', counterNs:'sogood5925-gif.github.io'};
  var ON_SITE=/(^|\.)github\.io$/.test(location.hostname);
  var CAT={life:'생활정보',dis:'질병',nut:'영양소',hea:'건강상식'}, PER=10;
  function $(id){return document.getElementById(id);}
  function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
  function put(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function mark(h){[].forEach.call(document.querySelectorAll('[data-h]'),function(a){a.setAttribute('aria-current',a.dataset.h===h?'true':'false');});}

  /* 예전 주소(#post-아이디)로 들어오면 글 주소로 옮겨요 */
  var old=location.hash.match(/^#post-([a-z0-9-]+)$/);
  if(old && $('postlist') && $('postlist').querySelector('[data-id="'+old[1]+'"]')){location.replace(old[1]+'/');return;}

  /* 방문자 수: 한 브라우저는 하루에 한 번만 세요(한국 시간 기준). 불러오지 못하면 칸을 숨겨요 */
  if(ON_SITE){
    var day=new Date(Date.now()+9*36e5).toISOString().slice(0,10).replace(/-/g,'');
    var verb=get('sangsik-visit')===day?'get':'hit';
    var num=function(k){return fetch(SITE.counter+verb+'/'+SITE.counterNs+'/sangsik-'+k)
      .then(function(r){if(r.status===404)return 0; if(!r.ok)throw r.status; return r.json().then(function(j){return j.value;});});};
    Promise.all([num('d-'+day),num('total')]).then(function(v){
      $('v-today').textContent=Number(v[0]).toLocaleString('ko-KR');
      $('v-total').textContent=Number(v[1]).toLocaleString('ko-KR');
      $('visits').hidden=false;
      put('sangsik-visit',day);
    }).catch(function(){});
  }

  /* 글 보기: 공감 버튼과 댓글 */
  var lk=document.querySelector('.like');
  if(lk){var key='like-'+lk.dataset.id;
    var dl=function(){var on=get(key)==='1';lk.textContent=on?'♥ 공감했어요':'♡ 공감하기';lk.setAttribute('aria-pressed',on?'true':'false');};
    lk.addEventListener('click',function(){put(key,get(key)==='1'?'0':'1');dl();});dl();}
  var cbox=$('cbox');
  if(cbox){
    if(ON_SITE){var sc=document.createElement('script');
      sc.src='https://utteranc.es/client.js';sc.async=true;sc.setAttribute('crossorigin','anonymous');
      sc.setAttribute('repo',SITE.repo);sc.setAttribute('issue-term',cbox.dataset.term);sc.setAttribute('theme','preferred-color-scheme');
      cbox.appendChild(sc);}
    else{var n=$('cnote'), a=document.createElement('a');
      n.textContent='댓글은 공개 사이트에서 남길 수 있어요. ';
      a.href=document.querySelector('link[rel=canonical]').href;a.textContent='이 글을 공개 사이트에서 열기';n.appendChild(a);}
  }

  /* 첫 화면: 카테고리(#cat-…)·검색(?q=)에 맞춰 목록을 거르고 10개씩 나눠 보여요 */
  var pl=$('postlist');
  if(!pl) return;
  var items=[].slice.call(pl.children), page=1, hay=null;
  function show(list,title){
    $('listtitle').textContent=title; $('listcount').textContent=list.length+'개의 글';
    $('nohit').hidden=list.length>0;
    var pages=Math.ceil(list.length/PER); page=Math.min(page,Math.max(pages,1));
    items.forEach(function(li){li.hidden=true;});
    list.slice((page-1)*PER,page*PER).forEach(function(li){li.hidden=false;});
    var pg=$('pager'); pg.innerHTML=''; pg.hidden=pages<2;
    for(var i=1;i<=pages;i++)(function(n){var b=document.createElement('button');b.type='button';b.textContent=n;
      if(n===page)b.setAttribute('aria-current','page');
      b.addEventListener('click',function(){page=n;show(list,title);$('main').scrollIntoView({block:'start'});});pg.appendChild(b);})(i);
  }
  function loadHay(){
    if(hay) return Promise.resolve(hay);
    return fetch('search.json').then(function(r){if(!r.ok)throw r.status;return r.json();}).then(function(j){return hay=j;})
      .catch(function(){var h={};items.forEach(function(li){h[li.dataset.id]=li.textContent.toLowerCase();});return h;});
  }
  function route(){
    page=1;
    var q=(new URLSearchParams(location.search).get('q')||'').trim(), c=location.hash.slice(5);
    if(location.hash.indexOf('#cat-')===0 && CAT[c]){mark('cat-'+c);show(items.filter(function(li){return li.dataset.cat===c;}),CAT[c]);return;}
    if(q){
      var t='‘'+q+'’ 검색 결과';mark(null);$('q').value=q;
      $('listtitle').textContent=t;$('listcount').textContent='찾는 중…';
      loadHay().then(function(h){var s=q.toLowerCase();show(items.filter(function(li){return (h[li.dataset.id]||'').indexOf(s)>=0;}),t);});
      return;
    }
    mark('home');show(items,'전체글');
  }
  window.addEventListener('hashchange',function(){route();window.scrollTo(0,0);});
  route();
})();
