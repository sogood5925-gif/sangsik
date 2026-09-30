(function(){
  /* 방문 통계 페이지(stats/). 카운터 주소와 키 이름은 src/site.js 와 같아야 해요 */
  var SITE={counter:'https://abacus.jasoncameron.dev/', counterNs:'sogood5925-gif.github.io'};
  var ON_SITE=location.protocol==='http:'||location.protocol==='https:';
  var CAT={life:'생활정보',dis:'질병',nut:'영양소',hea:'건강상식'};
  var SRC=[['google','구글'],['naver','네이버'],['daum','다음'],['bing','빙'],['search','그 밖의 검색엔진'],
    ['ai','AI 서비스(챗GPT 등)'],['kakao','카카오톡'],['sns','SNS·커뮤니티'],['root','내 첫 페이지(github.io)'],
    ['other','그 밖의 사이트'],['direct','직접 방문·즐겨찾기']];
  var START='2026.09.30';   // 유입 경로와 글 조회수를 세기 시작한 날
  function $(id){return document.getElementById(id);}
  function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
  function put(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function fmt(v){return Number(v).toLocaleString('ko-KR');}
  function cnt(k){return fetch(SITE.counter+'get/'+SITE.counterNs+'/sangsik-'+k)
    .then(function(r){if(r.status===404)return 0; if(!r.ok)throw r.status; return r.json().then(function(j){return j.value;});});}
  function kst(d){return new Date(Date.now()+9*36e5-d*864e5).toISOString().slice(0,10).replace(/-/g,'');}
  function el(tag,cls,text){var e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;}
  function seg(id,on){[].forEach.call($(id).children,function(b){b.setAttribute('aria-pressed',b.dataset.k===on?'true':'false');});}

  /* 내 방문 빼기: 이 브라우저에서는 방문·유입·조회수를 세지 않아요 */
  function me(){var on=get('sangsik-me')==='1';
    $('me-note').textContent=on?'이 브라우저의 방문은 지금 통계에서 빠지고 있어요.':'블로그 주인이 자기 방문을 세지 않게 하려면 쓰는 브라우저마다 한 번씩 눌러 주세요.';
    $('me-btn').textContent=on?'다시 세기':'이 브라우저 방문 빼기';
    $('me-btn').setAttribute('aria-pressed',on?'true':'false');}
  $('me-btn').addEventListener('click',function(){put('sangsik-me',get('sangsik-me')==='1'?'0':'1');me();});
  me();

  var posts=JSON.parse($('plist').textContent);
  if(!ON_SITE){$('st-off').hidden=false;return;}

  /* 방문자 */
  [['s-today','d-'+kst(0)],['s-yday','d-'+kst(1)],['s-total','total']].forEach(function(x){
    cnt(x[1]).then(function(v){$(x[0]).textContent=fmt(v);}).catch(function(){$(x[0]).textContent='?';});});

  /* 유입 경로: 기간마다 경로별 값을 불러와 막대로 보여 줘요 */
  var now=kst(0), ym=now.slice(0,6), lm=new Date(Date.UTC(+ym.slice(0,4),+ym.slice(4)-2,1)).toISOString().slice(0,7).replace('-','');
  var PK={today:function(s){return 'sd-'+now+'-'+s},yday:function(s){return 'sd-'+kst(1)+'-'+s},
    month:function(s){return 'sm-'+ym+'-'+s},lmonth:function(s){return 'sm-'+lm+'-'+s},total:function(s){return 'src-'+s}};
  var srcReq=0;
  function sources(p){
    seg('src-p',p); var req=++srcReq, box=$('src-bars');
    $('src-sum').textContent='불러오는 중…';
    Promise.all(SRC.map(function(s){return cnt(PK[p](s[0])).catch(function(){return null;});})).then(function(v){
      if(req!==srcReq) return;
      var rows=SRC.map(function(s,i){return {label:s[1],v:v[i]};});
      var failed=rows.some(function(r){return r.v===null;});
      rows.forEach(function(r){if(r.v===null)r.v=0;});
      rows.sort(function(a,b){return b.v-a.v;});
      var sum=rows.reduce(function(a,r){return a+r.v;},0), max=Math.max.apply(null,rows.map(function(r){return r.v;}))||1;
      $('src-sum').textContent=(sum?'모두 '+fmt(sum)+'명':'아직 기록이 없어요')+' · '+START+'부터 집계'+(failed?' · 일부를 불러오지 못했어요':'');
      box.innerHTML='';
      rows.forEach(function(r){
        var pct=sum?Math.round(r.v/sum*1000)/10:0, li=el('li',r.v?null:'zero');
        li.title=r.label+': '+fmt(r.v)+'명 ('+pct+'%)';
        li.appendChild(el('span','b-label',r.label));
        var tr=el('span','b-track'), bar=el('span','b-bar');bar.style.width=(r.v/max*100)+'%';tr.appendChild(bar);li.appendChild(tr);
        li.appendChild(el('span','b-val',fmt(r.v)+'명 · '+pct+'%'));
        box.appendChild(li);});
    });
  }
  [].forEach.call($('src-p').children,function(b){b.addEventListener('click',function(){sources(b.dataset.k);});});
  sources('today');

  /* 글별 조회수: 300편을 6개씩 나눠 불러와요 */
  var VW={}, cat='all', shown=30, done=0;
  function table(){
    seg('pv-cat',cat);
    var list=posts.filter(function(p){return cat==='all'||p.c===cat;})
      .sort(function(a,b){return (VW[b.id]||0)-(VW[a.id]||0);});
    var total=list.reduce(function(a,p){return a+(VW[p.id]||0);},0), body=$('pv-body');
    $('pv-state').textContent=(done<posts.length?'불러오는 중 '+done+'/'+posts.length+' · ':'')+
      (cat==='all'?'전체':CAT[cat])+' '+list.length+'편 · 조회 합계 '+fmt(total)+' · '+START+'부터 집계';
    body.innerHTML='';
    list.slice(0,shown).forEach(function(p,i){
      var tr=el('tr'), a=el('a',null,p.t), td=el('td');
      a.href='../'+p.id+'/'; td.appendChild(el('span','item-cat k-'+p.c,CAT[p.c])); td.appendChild(a);
      tr.appendChild(el('td','num',String(i+1))); tr.appendChild(td);
      tr.appendChild(el('td','num',p.id in VW?fmt(VW[p.id]):(done<posts.length?'…':'?')));
      body.appendChild(tr);});
    $('pv-more').hidden=list.length<=shown;
  }
  [].forEach.call($('pv-cat').children,function(b){b.addEventListener('click',function(){cat=b.dataset.k;shown=30;table();});});
  $('pv-more').addEventListener('click',function(){shown+=30;table();});
  var queue=posts.slice(), timer=null;
  function redraw(){if(!timer) timer=setTimeout(function(){timer=null;table();},300);}
  function next(){var p=queue.shift(); if(!p) return;
    cnt('p-'+p.id).then(function(v){VW[p.id]=v;}).catch(function(){}).then(function(){done++;redraw();next();});}
  for(var i=0;i<6;i++) next();
  table();
})();
