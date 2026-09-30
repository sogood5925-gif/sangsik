(function(){
  /* GitHub Pages와 Vercel 모두에서 댓글과 방문자 수를 사용해요. 통계 데이터 이름은 기존 값과 맞춰 양쪽 방문을 합쳐요. */
  var SITE={url:'https://sangsik-beta.vercel.app/', repo:'sogood5925-gif/sangsik', counter:'https://abacus.jasoncameron.dev/', counterNs:'sogood5925-gif.github.io'};
  var ON_SITE=location.protocol==='http:'||location.protocol==='https:';
  var CAT={life:'생활정보',dis:'질병',nut:'영양소',hea:'건강상식'}, PER=10;
  function $(id){return document.getElementById(id);}
  function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
  function put(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function mark(h){[].forEach.call(document.querySelectorAll('[data-h]'),function(a){a.setAttribute('aria-current',a.dataset.h===h?'true':'false');});}

  /* 예전 주소(#post-아이디)로 들어오면 글 주소로 옮겨요 */
  var old=location.hash.match(/^#post-([a-z0-9-]+)$/);
  if(old && $('postlist') && $('postlist').querySelector('[data-id="'+old[1]+'"]')){location.replace(old[1]+'/');return;}

  /* 방문자 수: 한 브라우저는 하루에 한 번만 세요(한국 시간 기준). 불러오지 못하면 칸을 숨겨요.
     통계 페이지(stats/)에서 '내 방문 빼기'를 켠 브라우저는 세지 않고 읽기만 해요 */
  var day=new Date(Date.now()+9*36e5).toISOString().slice(0,10).replace(/-/g,'');
  var ME=get('sangsik-me')==='1';
  function cnt(verb,k){return fetch(SITE.counter+verb+'/'+SITE.counterNs+'/sangsik-'+k)
    .then(function(r){if(r.status===404)return 0; if(!r.ok)throw r.status; return r.json().then(function(j){return j.value;});});}
  function fmt(v){return Number(v).toLocaleString('ko-KR');}
  /* 들어온 경로: 이전 페이지 주소(referrer)와 앱 안 브라우저 표시(user agent)로 나눠요. stats/ 의 목록과 이름이 같아야 해요 */
  function source(){
    var ua=navigator.userAgent||'', h='', path='';
    try{var u=new URL(document.referrer);h=u.hostname.toLowerCase();path=u.pathname;}catch(e){}
    var is=function(re){return re.test(h);};
    if(h===location.hostname) return path.indexOf('/sangsik/')===0?'direct':'root';
    if(/KAKAOTALK/i.test(ua)||is(/(^|\.)kakao\.com$/)) return 'kakao';
    if(is(/(^|\.)(chatgpt\.com|openai\.com|perplexity\.ai|claude\.ai|copilot\.microsoft\.com|gemini\.google\.com|wrtn\.ai)$/)) return 'ai';
    if(is(/(^|\.)google\.[a-z.]+$/)) return 'google';
    if(is(/(^|\.)naver\.(com|net)$/)||/NAVER\(inapp/i.test(ua)) return 'naver';
    if(is(/(^|\.)daum\.net$/)) return 'daum';
    if(is(/(^|\.)bing\.com$/)) return 'bing';
    if(is(/(^|\.)(zum\.com|duckduckgo\.com|yahoo\.[a-z.]+|ecosia\.org|baidu\.com|yandex\.[a-z.]+)$/)) return 'search';
    if(/FBAN|FBAV|Instagram|Line\/|BAND\//.test(ua)||is(/(^|\.)(facebook\.com|instagram\.com|t\.co|twitter\.com|x\.com|threads\.net|band\.us|youtube\.com|reddit\.com|tiktok\.com|dcinside\.com|clien\.net|theqoo\.net|fmkorea\.com)$/)) return 'sns';
    return h?'other':'direct';
  }
  if(ON_SITE){
    var fresh=!ME && get('sangsik-visit')!==day;
    var verb=fresh?'hit':'get';
    Promise.all([cnt(verb,'d-'+day),cnt(verb,'total')]).then(function(v){
      $('v-today').textContent=fmt(v[0]);
      $('v-total').textContent=fmt(v[1]);
      $('visits').hidden=false;
      if(fresh) put('sangsik-visit',day);
    }).catch(function(){});
    if(fresh){var src=source();
      ['src-'+src,'sm-'+day.slice(0,6)+'-'+src,'sd-'+day+'-'+src].forEach(function(k){cnt('hit',k).catch(function(){});});}
  }

  /* 글 조회수: 한 브라우저에서 같은 글은 하루에 한 번만 세요 */
  var vw=$('views');
  if(vw && ON_SITE){
    var seen={}; try{seen=JSON.parse(get('sangsik-pv')||'{}');}catch(e){}
    if(seen.d!==day||!Array.isArray(seen.ids)) seen={d:day,ids:[]};
    var vid=vw.dataset.id, vhit=!ME && seen.ids.indexOf(vid)<0;
    cnt(vhit?'hit':'get','p-'+vid).then(function(v){
      $('vcount').textContent=fmt(v);vw.hidden=false;
      if(vhit){seen.ids.push(vid);put('sangsik-pv',JSON.stringify(seen));}
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
    pager($('pager'),pages,page,function(n){page=n;show(list,title);$('main').scrollIntoView({block:'start'});});
    views(list.slice((page-1)*PER,page*PER));
  }
  /* 쪽 번호는 10개씩 묶어 보여 주고, 화살표로 앞뒤 묶음(처음·마지막)으로 옮겨 가요 */
  function pager(pg,pages,page,go){
    pg.innerHTML=''; pg.hidden=pages<2; if(pages<2) return;
    var G=10, s=Math.floor((page-1)/G)*G+1, e=Math.min(s+G-1,pages);
    function b(text,n,label,cur){var x=document.createElement('button');x.type='button';x.textContent=text;
      if(label){x.setAttribute('aria-label',label);x.className=/쪽$/.test(label)&&!/10쪽$/.test(label)?'arw end':'arw';}
      if(n===null) x.disabled=true; else x.addEventListener('click',function(){go(n);});
      if(cur) x.setAttribute('aria-current','page');
      pg.appendChild(x);}
    if(pages>G){b('«',s>1?1:null,'첫 쪽');b('‹',s>1?s-1:null,'이전 10쪽');}
    for(var i=s;i<=e;i++) b(String(i),i,null,i===page);
    if(pages>G){b('›',e<pages?e+1:null,'다음 10쪽');b('»',e<pages?pages:null,'마지막 쪽');}
  }
  /* 목록에 보이는 글의 조회수를 불러와요(한 번 불러온 값은 다시 쓰고, 세지는 않아요) */
  var VW={};
  function views(lis){
    if(!ON_SITE) return;
    lis.forEach(function(li){
      var id=li.dataset.id, sp=li.querySelector('.item-views');
      var fill=function(v){sp.textContent=' · 조회 '+fmt(v);sp.hidden=false;};
      if(!sp) return;
      if(id in VW){if(VW[id]!==null) fill(VW[id]); return;}
      VW[id]=null;
      cnt('get','p-'+id).then(function(v){VW[id]=v;fill(v);}).catch(function(){delete VW[id];});
    });
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
      var t='���'+q+'’ 검색 결과';mark(null);$('q').value=q;
      $('listtitle').textContent=t;$('listcount').textContent='찾는 중…';
      loadHay().then(function(h){var s=q.toLowerCase();show(items.filter(function(li){return (h[li.dataset.id]||'').indexOf(s)>=0;}),t);});
      return;
    }
    mark('home');show(items,'전체글');
  }
  window.addEventListener('hashchange',function(){route();window.scrollTo(0,0);});
  route();
})();
