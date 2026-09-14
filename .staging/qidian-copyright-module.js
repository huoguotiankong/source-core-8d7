/* alpha79：本模块私有依赖内聚。未进入该功能时，不在全局运行时建立这些 helper。 */
function qfCopyrightImageData2929(ctx,url,referer,maxBytes){
    url=String(url||'').trim();if(!url)return '';if(/^\/\//.test(url))url='https:'+url;
    try{
        var j=qfJava(ctx);if(!j||typeof j.get!=='function')return '';
        var ref=String(referer||'https://www.qidian.com/');
        var uas=[QF_UA,'Mozilla/mobile QDReaderAndroid/7.9.394/1526/1000009/V2505A','Dalvik/2.1.0 (Linux; U; Android 10; V2505A Build/UKQ1.230924.001)'];
        for(var ui=0;ui<uas.length;ui++){
            try{
                var r=j.get(url,{'User-Agent':uas[ui],'Referer':ref,'Accept':'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'},18000);
                try{if(r&&typeof r.statusCode==='function'){var sc=Number(r.statusCode());if(sc&&sc!==200)continue;}}catch(_sc){}
                var bytes=null;try{if(r&&typeof r.bodyAsBytes==='function')bytes=r.bodyAsBytes();}catch(_bb){}
                if(!bytes||!bytes.length||bytes.length<64)continue;var lim=Number(maxBytes||0);if(lim>0&&bytes.length>lim)continue;
                function b(i){try{return Number(bytes[i])&255;}catch(_e){return -1;}}
                var mime='image/jpeg';if(b(0)===0x89&&b(1)===0x50&&b(2)===0x4e&&b(3)===0x47)mime='image/png';else if(b(0)===0x47&&b(1)===0x49&&b(2)===0x46)mime='image/gif';else if(b(0)===0x52&&b(1)===0x49&&b(2)===0x46&&b(3)===0x46&&b(8)===0x57&&b(9)===0x45&&b(10)===0x42&&b(11)===0x50)mime='image/webp';else if(b(0)===0xff&&b(1)===0xd8&&b(2)===0xff)mime='image/jpeg';
                var b64=String(Packages.android.util.Base64.encodeToString(bytes,2)||'').replace(/[\r\n]/g,'');if(b64)return 'data:'+mime+';base64,'+b64;
            }catch(_one){}
        }
    }catch(e){}return '';
}


/* alpha39：版权页为低频功能，仅打开“版权信息”目录项时加载。 */

function qfBidV09(baseUrl) {
    var xs = [];
    try { xs.push(String(baseUrl || "")); } catch(e0) {}
    try {
        var b = qfBook(this);
        if (b) {
            if (b.bookUrl) xs.push(String(b.bookUrl));
            if (b.tocUrl) xs.push(String(b.tocUrl));
            if (b.coverUrl) xs.push(String(b.coverUrl));
            if (b.getVariable) xs.push("book_id=" + String(b.getVariable("qf_bid") || ""));
        }
    } catch(e1) {}
    for (var i = 0; i < xs.length; i++) {
        var m = xs[i].match(/(?:book_id=|bookId=|\/book\/|qdbimg\/349573\/)(\d+)/i);
        if (m && m[1]) return String(m[1]);
    }
    return "";
}
/* 旧 Archive/彩蛋网络链已移除。 */

/* alpha68：版权页改为起点 APP 风格。
 * 只保留：封面、书名、类型、上架时间、字数/状态、正版支持文案、作者。
 * 不再显示作者头像、作家等级、作者简介、标签，避免与 APP 样式混杂。
 */
/* v4.0.0-alpha6：版权页 Data Provider / Domain / Renderer 正式拆层。
 * qfCopyrightDataV420 只负责官方数据获取与归一化；
 * qfCopyrightRenderV420 只消费稳定模型并生成阅读视图；
 * qdCopyrightV2929 保留旧 ABI，内部仅做兼容编排。 */
function qfCopyrightData(baseUrl){
    var name=String(qfQueryV09(baseUrl,'qfBook')||qfBookVarV09.call(this,'qf_name','本书')||'本书');
    var author=String(qfQueryV09(baseUrl,'qfAuthor')||qfBookVarV09.call(this,'qf_author','')||'');
    var bid=String(qfBidV09.call(this,baseUrl)||qfBookVarV09.call(this,'qf_bid','')||'');
    var _bind=String(qfBookVarV09.call(this,'qf_detailBind','')||'');
    var _bound=!!bid&&_bind.indexOf(String(bid)+'|')===0;
    var rawKind=_bound?String(qfBookVarV09.call(this,'qf_kind','')||''):'';
    var rawStatus=_bound?String(qfBookVarV09.call(this,'qf_status','')||''):'';
    var words=_bound?String(qfBookVarV09.call(this,'qf_wordCount','')||qfBookVarV09.call(this,'qf_words','')||''):'';
    var pub=_bound?String(qfBookVarV09.call(this,'qf_publishDate','')||''):'';
    var pubSource=pub?'detail-variable':'',pubLabel='上架';
    var cover=_bound?String(qfBookVarV09.call(this,'qf_cover','')||''):'';

    function t(v){return qfText(String(v==null?'':v)).replace(/\s+/g,' ').trim();}
    function cat(v){var z=t(v),ls=['玄幻','奇幻','武侠','仙侠','都市','现实','军事','历史','游戏','体育','科幻','悬疑','诸天无限','轻小说','短篇'];for(var i=0;i<ls.length;i++)if(z.indexOf(ls[i])>=0)return ls[i];return z||'作品';}
    function st(v){v=t(v);return /完本|完结/.test(v)?'完本':'连载';}
    function wc(v){v=t(v);var m=v.match(/(\d+(?:\.\d+)?)\s*万/);if(m)return String(Math.round(Number(m[1])));var n=Number(v.replace(/[^0-9.]/g,''));return isFinite(n)&&n>0?String(n>=10000?Math.round(n/10000):Math.round(n)):'—';}
    function ts(v){
        if(v===undefined||v===null||v==='')return 0;
        var n=Number(v);if(isFinite(n)&&n>946684800){if(n<1e12)n*=1000;return n;}
        var z=String(v).trim(),m=z.match(/(20\d{2})[^0-9]?(\d{1,2})[^0-9]?(\d{1,2})/);
        if(m){var d=new Date(Number(m[1]),Number(m[2])-1,Number(m[3]));return d.getTime();}
        var p=Date.parse(z.replace(/-/g,'/'));return isNaN(p)?0:p;
    }
    function dt(v){var n=ts(v);if(!n)return '';var d=new Date(n);function z(x){return x<10?'0'+x:String(x);}return d.getFullYear()+'.'+z(d.getMonth()+1)+'.'+z(d.getDate());}
    function deep(o,names,d){
        if(o==null||d>12)return '';
        if(Array.isArray(o)){for(var i=0;i<o.length;i++){var r=deep(o[i],names,d+1);if(r!=='')return r;}return '';}
        if(typeof o!=='object')return '';
        for(var a=0;a<names.length;a++)for(var k in o)if(Object.prototype.hasOwnProperty.call(o,k)&&String(k).toLowerCase()===String(names[a]).toLowerCase()){
            var v=o[k];if(v!==undefined&&v!==null&&String(v)!=='')return v;
        }
        for(var p in o)if(Object.prototype.hasOwnProperty.call(o,p)&&o[p]&&typeof o[p]==='object'){var x=deep(o[p],names,d+1);if(x!=='')return x;}
        return '';
    }
    function earliestChapterTime(n,d,best){
        if(n==null||d>14)return best||0;
        if(Array.isArray(n)){for(var i=0;i<n.length;i++)best=earliestChapterTime(n[i],d+1,best);return best||0;}
        if(typeof n!=='object')return best||0;
        var cid=deep(n,['ChapterId','chapterId','chapterID','cid'],0);
        if(cid){var tv=deep(n,['PublishTime','publishTime','FirstPublishTime','firstPublishTime','CreateTime','createTime','uT','UT','UpdateTime','updateTime','time','Time'],0),nn=ts(tv);if(nn&&(!best||nn<best))best=nn;}
        for(var k in n)if(Object.prototype.hasOwnProperty.call(n,k)&&n[k]&&typeof n[k]==='object')best=earliestChapterTime(n[k],d+1,best);
        return best||0;
    }

    /* APP 详情 / 目录全部经 Official Adapter 获取，版权模块不再知道 qidian_app 模块名。 */
    if(bid){
        try{
            var dr=qfOfficialCallV400.call(this,'bookDetail',[bid]),dj=dr&&dr.json||{},rr=String(dr&&dr.raw||'');
            if(rr&&rr.length>200){
                var root=(dj.Data!==undefined&&dj.Data!==null)?dj.Data:((dj.data!==undefined&&dj.data!==null)?dj.data:dj);
                if(!author)author=t(deep(root,['AuthorName','authorName','Author','author'],0)||'');
                if(!words)words=String(deep(root,['WordsCount','wordsCount','WordCount','wordCount','WordsCnt','wordsCnt'],0)||'');
                if(!cover)cover=String(deep(root,['BookCoverUrl','bookCoverUrl','CoverUrl','coverUrl','BookCover','bookCover','Cover','cover'],0)||'');
                if(!dt(pub)){
                    var dp=deep(root,[
                        'ShelfTime','shelfTime','OnShelfTime','onShelfTime','UpShelfTime','upShelfTime',
                        'BookShelfTime','bookShelfTime','VipTime','vipTime','VipStartTime','vipStartTime',
                        'PublishTime','publishTime','BookPublishTime','bookPublishTime','PublishDate','publishDate',
                        'FirstPublishTime','firstPublishTime','OnlineTime','onlineTime','OnLineTime','onLineTime',
                        'StartTime','startTime','CreateTime','createTime','CreateDate','createDate'
                    ],0);
                    if(dt(dp)){pub=dp;pubSource='book-detail';pubLabel='上架';}
                }
            }
        }catch(_app){}
    }
    if(!dt(pub)&&bid){
        try{
            var cr=qfOfficialCallV400.call(this,'catalog',[bid]),
                er=earliestChapterTime(cr&&cr.json||{},0,0);
            if(er){pub=er;pubSource='catalog-earliest';pubLabel='首发';}
        }catch(_cat){}
    }

    /* alpha7.1：v3 目录在部分书上会 -1004，而 v2/getsimple 已被目录主链证明
       能稳定返回 ChapterData.time。只在前两级仍无日期时补一次官方 getsimple。
       得到的是最早官方章节发布时间，因此 UI 标记为“首发”。 */
    if(!dt(pub)&&bid){
        try{
            var sr=qfOfficialCallV400.call(this,'appRequest',[
                '/argus/api/v2/chapterlist/getsimple',
                {bookId:bid,showrelate:0},
                {bookId:bid,timeout:6500}
            ]);
            var sj=sr&&sr.json?sr.json:{},se=earliestChapterTime(sj,0,0);
            if(se){pub=se;pubSource='getsimple-earliest';pubLabel='首发';}
        }catch(_simpleDate){}
    }
    if(!cover){try{var bk=qfBook(this);if(bk&&bk.coverUrl)cover=String(bk.coverUrl||'');}catch(_bk){}}
    if(/^\/\//.test(cover))cover='https:'+cover;
    if(/^http:\/\//i.test(cover))cover='https://'+cover.slice(7);

    return {
        ok:true,bookId:bid,title:t(name)||'本书',author:t(author),category:cat(rawKind),status:st(rawStatus+' '+rawKind),
        wordCountWan:wc(words),wordCountRaw:t(words),publishDate:dt(pub)||'—',publishTime:ts(pub)||0,
        publishLabel:String(dt(pub)?pubLabel:'上架'),publishSource:String(pubSource||'none'),coverUrl:String(cover||''),
        source:'qidian-official',schema:'qf.copyright/1',contractVersion:1
    };
}
function qfCopyrightRender(model){
    model=model&&typeof model==='object'?model:{};
    var bid=String(model.bookId||''),name=String(model.title||'本书'),author=String(model.author||''),kind=String(model.category||'作品'),status=String(model.status||'连载'),date=String(model.publishDate||'—'),dateLabel=String(model.publishLabel||'上架'),num=String(model.wordCountWan||'—'),cover=String(model.coverUrl||'');
    function e(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}
    function t(v){return qfText(String(v==null?'':v)).replace(/\s+/g,' ').trim();}
    var coverData='';
    if(cover){try{coverData=qfCopyrightImageData2929(this,cover,bid?'https://www.qidian.com/book/'+encodeURIComponent(bid)+'/':'https://www.qidian.com/',4*1024*1024)||'';}catch(_cv){}}
    function tx(X,Y,S,F,O,W,A){return '<text x="'+X+'" y="'+Y+'" font-size="'+F+'"'+(O!=null?' opacity="'+O+'"':'')+(W?' font-weight="'+W+'"':'')+(A?' text-anchor="'+A+'"':'')+'>'+e(S)+'</text>';}
    function line(y){return '<line x1="92" y1="'+y+'" x2="628" y2="'+y+'" stroke="currentColor" opacity=".14" stroke-dasharray="2 7"/>';}
    function titleText(z){z=t(z)||'本书';var fs=z.length<=8?40:(z.length<=12?35:30),max=520;return '<text x="360" y="446" text-anchor="middle" font-size="'+fs+'" font-weight="650"'+(z.length>15?' textLength="'+max+'" lengthAdjust="spacingAndGlyphs"':'')+'>'+e(z)+'</text>';}
    var H=1050,svg='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="720" height="'+H+'" viewBox="0 0 720 '+H+'">'+
      '<rect width="720" height="'+H+'" fill="transparent"/>'+
      '<defs><clipPath id="qfcv68"><rect x="252" y="66" width="216" height="288" rx="3"/></clipPath></defs>'+
      '<rect x="246" y="60" width="228" height="300" fill="currentColor" opacity=".055"/>'+
      (coverData?'<image href="'+e(coverData)+'" xlink:href="'+e(coverData)+'" x="252" y="66" width="216" height="288" preserveAspectRatio="xMidYMid slice" clip-path="url(#qfcv68)"/>':'<rect x="252" y="66" width="216" height="288" fill="currentColor" opacity=".06"/>'+tx(360,222,'封面',28,.34,'500','middle'))+
      titleText(name)+
      tx(148,544,kind,34,1,'600','middle')+tx(148,584,'类型',18,.42,'400','middle')+
      tx(360,544,date,34,1,'600','middle')+tx(360,584,dateLabel,18,.42,'400','middle')+
      tx(572,544,num,34,1,'600','middle')+tx(572,584,'万字/'+status,18,.42,'400','middle')+
      line(638)+tx(96,724,'支持原创文字，支持正版阅读！',29,.92,'500','start')+
      tx(620,788,'— '+(author||'作者'),27,.9,'500','end')+line(846)+
      tx(360,934,'— 本作品由起点中文网进行电子制作与发行 —',18,.46,'400','middle')+
      tx(360,974,'版权所有 · 侵权必究',18,.46,'400','middle')+'</svg>';
    try{var j=qfJava(this);if(j&&j.base64Encode)return '<img src="data:image/svg+xml;base64,'+j.base64Encode(svg)+'" style="display:block;width:100%;height:auto;margin:0;padding:0;">';}catch(_b){}
    return '<div>'+svg+'</div>';
}
function qdCopyrightV2929(baseUrl){return qfCopyrightRenderV420.call(this,qfCopyrightDataV420.call(this,baseUrl));}
function qdCopyrightV2928(baseUrl){return qdCopyrightV2929.call(this,baseUrl);}
function qdCopyrightV17(baseUrl){return qdCopyrightV2929.call(this,baseUrl);}

function qfCopyrightDataV420(){return qfCopyrightData.apply(this,arguments);}

function qfCopyrightRenderV420(){return qfCopyrightRender.apply(this,arguments);}
