(function(){
  const canvas = document.getElementById('rpgCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  ctx.imageSmoothingEnabled = false;
  canvas.focus();
  canvas.addEventListener('click', () => canvas.focus());

  const theme = window.RPG_THEME || {
    primary: '#C9A84C',
    text: '#F5E6C8',
    border: '#8B6914',
    bg: '#1a0e00',
    font: 'Cinzel'
  };

  const keys = {};
  const assets = { bg:{}, portraits:{}, cutscenes:{}, goliath:null, davidSheet:null, davidSheetAlpha:null };
  const urls = {
    bg: {
      pasture: 'app/static/rpg/davi/curral.png',
      houseExt: 'app/static/rpg/davi/exterior_casa.png',
      houseInt: 'app/static/rpg/davi/interior_casa.png',
      camp: 'app/static/rpg/davi/acampamento_israel.png',
      valley: 'app/static/rpg/davi/vale_ela.png'
    },
    portraits: {
      Samuel: 'app/static/rpg/davi/portraits/samuel.png',
      Davi: 'app/static/rpg/davi/portraits/davi_pastor.png',
      Jessé: 'app/static/rpg/davi/portraits/davi_pastor.png',
      Golias: 'app/static/rpg/davi/portraits/golias.png'
    },
    cutscenes: {
      fear: 'app/static/rpg/davi/cutscenes/soldados_fugindo.png',
      duel: 'app/static/rpg/davi/cutscenes/davi_golias.png'
    },
    goliath: 'app/static/rpg/davi/sprite_golias.png',
    davidSheet: 'app/static/rpg/davi/characters/davi_shepherd_sheet.png'
  };

  const state = {
    scene: 'pasture',
    mode: 'title',
    last: performance.now(),
    hint: '',
    toast: '',
    toastTime: 0,
    fade: 0,
    fadeDir: 0,
    fadeDone: null,
    dialog: null,
    cutscene: null,
    shake: 0,
    glow: 0,
    progress: {
      intro: false,
      messenger: false,
      herd: false,
      samuel: false,
      brothersGone: false,
      basket: false,
      eliabe: false,
      soldier: false,
      saul: false,
      stones: false,
      finalWords: false,
      completed: false
    },
    herd: [
      {x:214,y:116,done:false},
      {x:156,y:169,done:false},
      {x:324,y:184,done:false},
      {x:408,y:112,done:false}
    ],
    stones: [
      {x:210,y:178,r:18,smooth:true,picked:false},{x:310,y:150,r:18,smooth:false,picked:false},
      {x:432,y:196,r:16,smooth:true,picked:false},{x:548,y:162,r:17,smooth:true,picked:false},
      {x:684,y:222,r:18,smooth:false,picked:false},{x:282,y:318,r:15,smooth:true,picked:false},
      {x:420,y:350,r:18,smooth:false,picked:false},{x:600,y:336,r:16,smooth:true,picked:false},
      {x:748,y:342,r:17,smooth:false,picked:false}
    ],
    aim: {x:742,y:204,dx:2.25,dy:1.35,r:28,tries:3,fall:0}
  };

  const player = {x:128,y:318,w:32,h:42,speed:2.25,dir:'down',basket:false,moving:false,walkTime:0};

  const scenes = {
    pasture: {
      title: 'Pasto de Belém',
      objective: () => state.progress.herd ? 'Siga pela estrada para a casa de Jessé.' : (state.progress.messenger ? 'Cuide das ovelhas do campo.' : 'Fale com o mensageiro de Jessé.'),
      bg: 'pasture',
      start: {x:128,y:318},
      exits: [{x:850,y:250,w:90,h:150,to:'houseExt',at:{x:452,y:424},need:()=>state.progress.herd}]
    },
    houseExt: {
      title: 'Frente da Casa de Jessé',
      objective: () => 'Entre pela porta para encontrar Samuel.',
      bg: 'houseExt',
      start: {x:452,y:424},
      exits: [{x:458,y:326,w:78,h:86,to:'houseInt',at:{x:470,y:410}}]
    },
    houseInt: {
      title: 'Casa de Jessé',
      objective: () => state.progress.samuel ? (state.progress.basket ? 'Saia para o acampamento de Israel.' : 'Fale com Jessé a sós.') : 'Ouça Samuel diante da família.',
      bg: 'houseInt',
      start: {x:470,y:410},
      exits: [{x:420,y:420,w:120,h:60,to:'camp',at:{x:88,y:318},need:()=>state.progress.basket}]
    },
    camp: {
      title: 'Acampamento de Israel',
      objective: () => state.progress.saul ? (state.progress.stones ? 'Siga para o Vale de Elá.' : 'Escolha cinco pedras lisas no riacho.') : (state.progress.soldier ? 'Fale com Saul.' : (state.progress.eliabe ? 'Fale com um soldado.' : 'Procure Eliabe entre as tendas.')),
      bg: 'camp',
      start: {x:88,y:318},
      exits: [{x:850,y:240,w:92,h:210,to:'valley',at:{x:118,y:312},need:()=>state.progress.stones}]
    },
    valley: {
      title: 'Vale de Elá',
      objective: () => state.progress.finalWords ? 'Acerte Golias com a funda.' : 'Aproxime-se e responda a Golias.',
      bg: 'valley',
      start: {x:118,y:312},
      exits: []
    }
  };

  function loadImage(src){
    return new Promise(resolve => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => resolve(null);
      img.src = src;
    });
  }

  async function loadAssets(){
    for (const [k,src] of Object.entries(urls.bg)) assets.bg[k] = await loadImage(src);
    for (const [k,src] of Object.entries(urls.portraits)) assets.portraits[k] = await loadImage(src);
    for (const [k,src] of Object.entries(urls.cutscenes)) assets.cutscenes[k] = await loadImage(src);
    assets.goliath = await loadImage(urls.goliath);
    assets.davidSheet = await loadImage(urls.davidSheet);
    if (assets.davidSheet) assets.davidSheetAlpha = chromaKeyGreen(assets.davidSheet);
  }
  loadAssets();

  function chromaKeyGreen(img){
    const off = document.createElement('canvas');
    off.width = img.width;
    off.height = img.height;
    const octx = off.getContext('2d');
    octx.imageSmoothingEnabled = false;
    octx.drawImage(img,0,0);
    const imageData = octx.getImageData(0,0,off.width,off.height);
    const d = imageData.data;
    for (let i=0;i<d.length;i+=4) {
      if (d[i] < 70 && d[i+1] > 185 && d[i+2] < 80) d[i+3] = 0;
    }
    octx.putImageData(imageData,0,0);
    return off;
  }

  function post(event, detail){ window.parent.postMessage({source:'projeto-biblico-rpg', event, detail}, '*'); }
  function toast(text){ state.toast = text; state.toastTime = 160; }
  function center(){ return {x:player.x + player.w/2, y:player.y + player.h}; }
  function near(x,y,r=58){ const p=center(); return Math.hypot(p.x-x,p.y-y) <= r; }
  function inRect(p,r){ return p.x>=r.x && p.x<=r.x+r.w && p.y>=r.y && p.y<=r.y+r.h; }

  function startDialog(speaker, color, lines, done){
    state.mode = 'dialog';
    state.dialog = {speaker, color: color || theme.primary, lines, i:0, shown:0, done};
  }

  function startCutscene(key, title, lines, done){
    state.mode = 'cutscene';
    state.cutscene = {key,title,lines,i:0,shown:0,done};
  }

  function transition(to, at){
    state.fadeDir = 1;
    state.fadeDone = () => {
      state.scene = to;
      player.x = at.x;
      player.y = at.y;
      state.mode = 'explore';
      toast(scenes[to].title);
      if (to === 'camp' && !state.progress.campSeen) {
        state.progress.campSeen = true;
        startCutscene('fear', 'O Desafio no Acampamento', [
          'Davi chega com alimento para seus irmãos e ouve o terror no acampamento.',
          'Golias sai das fileiras dos filisteus e desafia Israel, manhã e tarde.',
          'Os homens de Israel fogem com medo. Davi escuta e pergunta por que o exército do Deus vivo é afrontado.'
        ]);
      }
      if (to === 'valley' && !state.progress.valleySeen) {
        state.progress.valleySeen = true;
        startCutscene('duel', 'O Vale de Elá', [
          'Davi desce ao vale sem armadura, com cajado, funda e cinco pedras lisas.',
          'Golias confia em espada, lança e dardo.',
          'Davi confia no nome do Senhor dos Exércitos.'
        ]);
      }
    };
  }

  function currentTextBox(){ return state.dialog || state.cutscene; }
  function advanceTextBox(){
    const box = currentTextBox();
    if (!box) return;
    const text = box.lines[box.i] || '';
    if (box.shown < text.length) { box.shown = text.length; return; }
    box.i += 1;
    box.shown = 0;
    if (box.i >= box.lines.length) {
      const done = box.done;
      state.dialog = null;
      state.cutscene = null;
      state.mode = 'explore';
      if (done) done();
    }
  }

  function interact(){
    if (state.mode === 'title') {
      state.mode = 'explore';
      startDialog('Narrador', theme.primary, [
        'Belém acorda tranquila. Davi, o filho mais novo de Jessé, cuida do rebanho no campo.',
        'Naquele dia, um mensageiro chega: Samuel, o profeta, está na casa de Jessé.',
        'A jornada começa no ordinário: ouvir, obedecer e cuidar bem do que está diante dele.'
      ], () => { state.progress.intro = true; });
      return;
    }
    if (state.mode === 'dialog' || state.mode === 'cutscene') { advanceTextBox(); return; }
    if (state.mode === 'stones' || state.mode === 'aim') return;

    if (state.scene === 'pasture') {
      if (!state.progress.messenger && near(270,270,62)) {
        startDialog('Mensageiro', '#E6C36A', [
          'Davi, seu pai Jessé te chama em casa.',
          'Samuel, o profeta, está lá.',
          'Antes de partir, cuide das ovelhas espalhadas pelo pasto.'
        ], () => { state.progress.messenger = true; state.mode = 'herd'; });
        return;
      }
      if (state.mode === 'herd') { gatherSheep(true); return; }
    }

    if (state.scene === 'houseInt') {
      if (!state.progress.samuel && near(510,215,70)) {
        startDialog('Samuel', theme.primary, [
          'O Senhor não vê como o homem vê.',
          'O homem olha para a aparência, mas o Senhor olha para o coração. (1 Samuel 16:7)',
          'Samuel unge Davi no meio de seus irmãos, e o Espírito do Senhor se apodera de Davi daquele dia em diante.'
        ], () => {
          state.progress.samuel = true;
          state.glow = 150;
          startDialog('Narrador', theme.primary, [
            'Algum tempo depois, os três irmãos mais velhos de Davi seguem Saul para a guerra.',
            'Jessé chama Davi novamente, agora sem os irmãos na casa.'
          ], () => { state.progress.brothersGone = true; });
        });
        return;
      }
      if (state.progress.brothersGone && !state.progress.basket && near(325,300,66)) {
        startDialog('Jessé', '#E8D3A4', [
          'Davi, leve alimento para seus irmãos no acampamento.',
          'Veja como eles estão e traga-me notícias deles. (1 Samuel 17:17-18)'
        ], () => { state.progress.basket = true; player.basket = true; });
        return;
      }
    }

    if (state.scene === 'camp') {
      if (!state.progress.eliabe && near(285,260,64)) {
        startDialog('Eliabe', '#D9B076', [
          'Por que desceste aqui?',
          'E a quem deixaste aquelas poucas ovelhas no deserto? (1 Samuel 17:28)'
        ], () => { state.progress.eliabe = true; state.shake = 30; });
        return;
      }
      if (state.progress.eliabe && !state.progress.soldier && near(430,345,66)) {
        startDialog('Soldado', '#D7DDE8', [
          'Por quarenta dias, manhã e tarde, esse filisteu se apresenta e desafia Israel.',
          'Quando o vemos, fugimos com muito medo.'
        ], () => { state.progress.soldier = true; });
        return;
      }
      if (state.progress.soldier && !state.progress.saul && near(665,255,76)) {
        startDialog('Saul', '#D8C083', [
          'Você não pode lutar contra esse filisteu. Você é muito jovem.',
          'Davi: O Senhor que me livrou da pata do leão e da pata do urso me livrará também desse filisteu.',
          'Saul veste Davi com armadura, mas Davi a tira, pois não estava acostumado.'
        ], () => { state.progress.saul = true; toast('Davi recusa a armadura.'); });
        return;
      }
      if (state.progress.saul && !state.progress.stones && near(765,430,86)) {
        state.mode = 'stones';
        state.stones.forEach(s => s.picked = false);
        post('minigame_started', {name:'cinco_pedras'});
        return;
      }
    }

    if (state.scene === 'valley' && !state.progress.finalWords && near(735,250,125)) {
      startDialog('Golias', '#B86E52', [
        'Sou eu algum cão para vires a mim com paus?',
        'Davi: Tu vens contra mim com espada, lança e dardo.',
        'Davi: Eu, porém, venho contra ti em nome do Senhor dos Exércitos. (1 Samuel 17:45)'
      ], () => { state.progress.finalWords = true; state.mode = 'aim'; });
    }
  }

  function gatherSheep(manual=false){
    let changed = false;
    for (const s of state.herd) {
      if (!s.done && near(s.x,s.y,64)) {
        s.done = true;
        changed = true;
      }
    }
    if (changed) toast('Ovelha cuidada.');
    if (state.herd.every(s => s.done)) {
      state.progress.herd = true;
      state.mode = 'explore';
      startDialog('Davi', theme.primary, [
        'O rebanho está seguro.',
        'Agora posso ir à casa de meu pai.'
      ]);
    } else if (manual) toast('Aproxime-se de uma ovelha destacada.');
  }

  function blocksFor(scene){
    if (scene === 'pasture') return [
      {x:690,y:360,w:260,h:170},
      {x:76,y:142,w:36,h:46},{x:505,y:116,w:35,h:56},
      {x:734,y:82,w:144,h:24},{x:874,y:88,w:26,h:170},{x:610,y:112,w:28,h:138},
      {x:636,y:232,w:140,h:28},{x:812,y:232,w:92,h:28}
    ];
    if (scene === 'houseExt') return [
      {x:72,y:180,w:120,h:170},{x:726,y:164,w:120,h:220},
      {x:421,y:244,w:148,h:92},{x:535,y:290,w:145,h:112}
    ];
    if (scene === 'houseInt') return [
      {x:0,y:0,w:160,h:H},{x:790,y:0,w:170,h:H},{x:276,y:108,w:130,h:132},
      {x:178,y:250,w:100,h:76},{x:560,y:95,w:150,h:104},{x:560,y:330,w:96,h:88}
    ];
    if (scene === 'camp') return [
      {x:100,y:120,w:72,h:72},{x:195,y:168,w:72,h:72},{x:292,y:120,w:72,h:72},
      {x:386,y:168,w:72,h:72},{x:482,y:120,w:72,h:72},{x:602,y:122,w:185,h:142},
      {x:660,y:388,w:290,h:70}
    ];
    if (scene === 'valley') return [{x:0,y:55,w:42,h:505},{x:918,y:55,w:42,h:505},{x:625,y:80,w:280,h:85}];
    return [];
  }

  function canWalk(nx,ny){
    const foot = {x:nx + player.w/2, y:ny + player.h};
    if (foot.x < 22 || foot.x > W-22 || foot.y < 72 || foot.y > H-20) return false;
    return !blocksFor(state.scene).some(r => inRect(foot,r));
  }

  function update(dt){
    state.hint = '';
    if (state.fadeDir) {
      state.fade += state.fadeDir * 0.06;
      if (state.fade >= 1) {
        state.fade = 1; state.fadeDir = -1;
        if (state.fadeDone) { const fn = state.fadeDone; state.fadeDone = null; fn(); }
      }
      if (state.fade <= 0) { state.fade = 0; state.fadeDir = 0; }
    }

    const box = currentTextBox();
    if (box) box.shown = Math.min((box.lines[box.i] || '').length, box.shown + dt * 0.045);
    if (state.mode === 'title' || state.mode === 'dialog' || state.mode === 'cutscene' || state.mode === 'final') {
      tickEffects();
      return;
    }

    if (state.mode === 'explore' || state.mode === 'herd') {
      let dx=0, dy=0;
      if (keys.ArrowLeft || keys.a) dx -= 1;
      if (keys.ArrowRight || keys.d) dx += 1;
      if (keys.ArrowUp || keys.w) dy -= 1;
      if (keys.ArrowDown || keys.s) dy += 1;
      player.moving = false;
      if (dx || dy) {
        const len = Math.hypot(dx,dy);
        const nx = player.x + dx/len * player.speed;
        const ny = player.y + dy/len * player.speed;
        const beforeX = player.x;
        const beforeY = player.y;
        if (canWalk(nx, player.y)) player.x = nx;
        if (canWalk(player.x, ny)) player.y = ny;
        player.dir = Math.abs(dx)>Math.abs(dy) ? (dx>0?'right':'left') : (dy>0?'down':'up');
        player.moving = beforeX !== player.x || beforeY !== player.y;
        if (player.moving) player.walkTime += dt;
      }
      for (const ex of scenes[state.scene].exits || []) {
        if ((!ex.need || ex.need()) && inRect(center(), ex)) transition(ex.to, ex.at);
      }
      if (state.mode === 'herd') gatherSheep();
    }

    if (state.mode === 'aim') {
      state.aim.x += state.aim.dx;
      state.aim.y += state.aim.dy;
      if (state.aim.x < 670 || state.aim.x > 838) state.aim.dx *= -1;
      if (state.aim.y < 145 || state.aim.y > 252) state.aim.dy *= -1;
    }
    tickEffects();
  }

  function tickEffects(){
    if (state.toastTime > 0) state.toastTime -= 1;
    if (state.shake > 0) state.shake -= 1;
    if (state.glow > 0) state.glow -= 1;
    if (state.aim.fall > 0) state.aim.fall -= 1;
  }

  function drawText(text,x,y,size=17,color=theme.text,align='left',weight=700){
    ctx.font = `${weight} ${size}px ${theme.font}, Georgia, serif`;
    ctx.fillStyle = color;
    ctx.textAlign = align;
    ctx.fillText(text,x,y);
  }
  function rect(x,y,w,h,c){ ctx.fillStyle=c; ctx.fillRect(x,y,w,h); }
  function ellipse(x,y,rx,ry,c,stroke){
    ctx.beginPath(); ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2); ctx.fillStyle=c; ctx.fill();
    if (stroke){ ctx.strokeStyle=stroke; ctx.lineWidth=2; ctx.stroke(); }
  }
  function roundRect(x,y,w,h,r,c,stroke){
    ctx.beginPath(); ctx.roundRect(x,y,w,h,r); ctx.fillStyle=c; ctx.fill();
    if (stroke){ ctx.strokeStyle=stroke; ctx.lineWidth=2; ctx.stroke(); }
  }
  function wrap(text,x,y,max,lineH,size,color){
    ctx.font = `600 ${size}px ${theme.font}, Georgia, serif`;
    ctx.fillStyle = color; ctx.textAlign='left';
    let line = '';
    for (const word of text.split(' ')) {
      const next = line + word + ' ';
      if (ctx.measureText(next).width > max && line) { ctx.fillText(line,x,y); line = word + ' '; y += lineH; }
      else line = next;
    }
    ctx.fillText(line,x,y);
  }

  function cover(img){
    if (!img) return false;
    const scale = Math.max(W/img.width,(H-55)/img.height);
    const dw = img.width*scale, dh = img.height*scale;
    ctx.drawImage(img,(W-dw)/2,55+((H-55)-dh)/2,dw,dh);
    return true;
  }

  function drawBase(){
    if (state.shake) ctx.translate((Math.random()-.5)*5,(Math.random()-.5)*4);
    const scene = scenes[state.scene];
    rect(0,0,W,H,'#4d391d');
    if (!cover(assets.bg[scene.bg])) {
      rect(0,55,W,H-55,'#746333');
      ctx.beginPath(); ctx.moveTo(0,360); ctx.bezierCurveTo(220,320,360,360,520,306); ctx.bezierCurveTo(700,245,805,308,960,255);
      ctx.lineWidth=54; ctx.strokeStyle='#c5a061'; ctx.stroke();
    }
    rect(0,0,W,55,'rgba(24,13,3,.92)');
    drawText(scene.title,24,35,24,theme.primary);
    drawText(scene.objective(),W-24,35,14,theme.text,'right',700);
    rect(0,H-8,W,8,'rgba(40,22,8,.95)');
  }

  function px(x,y,w,h,c){ ctx.fillStyle = c; ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); }

  function drawSprite(x,y,opts={}){
    const scale = opts.scale || (opts.w ? opts.w / 26 : 1);
    const s = Math.max(.72, scale);
    const skin = opts.skin || '#c98d5a';
    const hair = opts.hair || '#3a220f';
    const tunic = opts.body || '#a66c32';
    const mantle = opts.mantle || '#74451f';
    const outline = 'rgba(33,18,8,.88)';
    const ox = Math.round(x);
    const oy = Math.round(y);

    ellipse(ox + 13*s, oy + 39*s, 12*s, 4*s, 'rgba(0,0,0,.24)');

    if (opts.staff) {
      px(ox + 2*s, oy + 7*s, 2*s, 31*s, '#4d321c');
      px(ox + 4*s, oy + 5*s, 6*s, 2*s, '#6f4a26');
      px(ox + 8*s, oy + 7*s, 2*s, 4*s, '#6f4a26');
    }

    px(ox + 8*s, oy + 35*s, 5*s, 8*s, outline);
    px(ox + 16*s, oy + 35*s, 5*s, 8*s, outline);
    px(ox + 9*s, oy + 34*s, 4*s, 7*s, '#3b2615');
    px(ox + 17*s, oy + 34*s, 4*s, 7*s, '#3b2615');

    px(ox + 6*s, oy + 13*s, 20*s, 24*s, outline);
    px(ox + 8*s, oy + 15*s, 16*s, 20*s, tunic);
    px(ox + 8*s, oy + 15*s, 16*s, 5*s, '#d0a15c');
    px(ox + 9*s, oy + 21*s, 14*s, 13*s, mantle);
    px(ox + 9*s, oy + 27*s, 14*s, 3*s, 'rgba(42,24,10,.45)');

    px(ox + 4*s, oy + 20*s, 5*s, 12*s, outline);
    px(ox + 23*s, oy + 20*s, 5*s, 12*s, outline);
    px(ox + 5*s, oy + 21*s, 3*s, 9*s, skin);
    px(ox + 24*s, oy + 21*s, 3*s, 9*s, skin);

    px(ox + 8*s, oy + 4*s, 17*s, 16*s, outline);
    px(ox + 10*s, oy + 6*s, 13*s, 13*s, skin);
    px(ox + 8*s, oy + 3*s, 17*s, 6*s, hair);
    px(ox + 9*s, oy + 8*s, 4*s, 3*s, hair);
    px(ox + 14*s, oy + 10*s, 2*s, 2*s, '#221308');
    px(ox + 20*s, oy + 10*s, 2*s, 2*s, '#221308');
    px(ox + 16*s, oy + 15*s, 5*s, 1*s, '#6d3c22');

    if (opts.basket) {
      px(ox + 25*s, oy + 23*s, 14*s, 11*s, '#6b411d');
      px(ox + 26*s, oy + 24*s, 12*s, 9*s, '#c59043');
      px(ox + 28*s, oy + 22*s, 8*s, 2*s, '#8b5a28');
    }
  }

  function drawPlayer(){
    const sheet = assets.davidSheetAlpha || assets.davidSheet;
    if (sheet) {
      const rowByDir = {down:0, up:1, left:2, right:3};
      const row = rowByDir[player.dir] ?? 0;
      const cw = sheet.width / 5;
      const ch = sheet.height / 4;
      const frame = player.moving ? (1 + Math.floor(player.walkTime / 120) % 4) : 0;
      const sx = frame * cw + cw * .24;
      const sy = row * ch + ch * .06;
      const sw = cw * .52;
      const sh = ch * .86;
      const dw = 52;
      const dh = 66;
      ellipse(player.x + 16, player.y + 40, 16, 5, 'rgba(0,0,0,.24)');
      ctx.drawImage(sheet, sx, sy, sw, sh, player.x - 10, player.y - 24, dw, dh);
      if (player.basket) {
        px(player.x + 25, player.y + 24, 14, 11, '#6b411d');
        px(player.x + 26, player.y + 25, 12, 9, '#c59043');
      }
      return;
    }
    drawSprite(player.x, player.y, {staff: state.scene !== 'camp' && state.scene !== 'valley', basket: player.basket});
  }
  function drawNpc(x,y,name,opts={}){
    drawSprite(x-13,y-31,{body:opts.body,mantle:opts.mantle,hair:opts.hair,w:26,h:36});
    drawText(name,x,y+24,12,theme.text,'center',700);
  }

  function drawSceneActors(){
    if (state.scene === 'pasture') {
      if (!state.progress.messenger) drawNpc(270,270,'Mensageiro',{body:'#c79758',mantle:'#7e4c2a'});
      if (state.mode === 'herd') drawHerd();
    }
    if (state.scene === 'houseInt') {
      drawNpc(325,300,'Jessé',{body:'#d0a16d',mantle:'#6d4528'});
      drawNpc(510,215,'Samuel',{body:'#d7c36f',mantle:'#f0d88a',hair:'#f6e7b7'});
      if (!state.progress.brothersGone) {
        drawNpc(420,315,'Eliabe',{body:'#a96a3a',mantle:'#5f321c'});
        drawNpc(590,318,'Abinadabe',{body:'#a97842',mantle:'#684024'});
        drawNpc(665,315,'Samá',{body:'#a97842',mantle:'#684024'});
      }
    }
    if (state.scene === 'camp') {
      drawCampFallback();
      drawNpc(285,260,'Eliabe',{body:'#b77a42',mantle:'#6d351c'});
      drawNpc(430,345,'Soldado',{body:'#cbd3dc',mantle:'#7a8691'});
      drawNpc(665,255,'Saul',{body:'#c5a153',mantle:'#875f1d'});
    }
    if (state.scene === 'valley') drawValley();
  }

  function drawCampFallback(){
    if (scenes[state.scene].bg) return;
    for (let i=0;i<70;i++) {
      const x = (i * 73) % W;
      const y = 70 + ((i * 41) % 420);
      px(x,y,2,2,i%3 ? 'rgba(255,226,150,.16)' : 'rgba(54,34,15,.16)');
    }
    for (let i=0;i<5;i++) {
      const x=110+i*96, y=128+(i%2)*48;
      ellipse(x+34,y+55,42,8,'rgba(0,0,0,.18)');
      ctx.beginPath(); ctx.moveTo(x,y+52); ctx.lineTo(x+34,y); ctx.lineTo(x+68,y+52); ctx.closePath();
      ctx.fillStyle='#c09759'; ctx.fill(); ctx.strokeStyle='#5a371b'; ctx.lineWidth=3; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x+34,y+5); ctx.lineTo(x+34,y+52); ctx.strokeStyle='rgba(84,50,24,.45)'; ctx.lineWidth=2; ctx.stroke();
      px(x+28,y+33,13,19,'#3b2111');
      px(x+9,y+50,6,10,'#6b421f'); px(x+53,y+50,6,10,'#6b421f');
    }
    roundRect(610,130,165,125,8,'#8f602f','#3b2413');
    px(626,148,134,15,'rgba(255,221,150,.18)');
    px(677,195,30,60,'#3b2111');
    drawText('Tenda de Saul',692,116,14,theme.text,'center');
    px(562,292,34,24,'#8a5d2f'); px(566,296,26,16,'#b07a3d');
    px(588,286,28,18,'#6d4927'); px(592,290,20,10,'#9b6a33');
    ellipse(520,338,28,14,'rgba(0,0,0,.22)');
    px(508,330,24,12,'#5a3518'); px(512,326,16,8,'#cf7d2d'); px(517,321,6,8,'#ffd060');
    ctx.beginPath(); ctx.moveTo(680,420); ctx.bezierCurveTo(735,395,835,445,925,413); ctx.lineWidth=36; ctx.strokeStyle='#4a8c9d'; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(680,416); ctx.bezierCurveTo(735,392,835,441,925,409); ctx.lineWidth=5; ctx.strokeStyle='rgba(231,255,255,.35)'; ctx.stroke();
    drawText('Riacho',805,402,14,theme.text,'center');
  }

  function drawValley(){
    if (assets.bg.valley) {
      drawGoliath(710,state.aim.fall ? 310 : 188);
      return;
    }
    rect(65,130,250,300,'rgba(197,161,83,.22)');
    rect(650,105,250,350,'rgba(92,34,24,.26)');
    drawText('Israel',190,112,18,theme.text,'center');
    drawText('Filisteus',775,88,18,theme.text,'center');
    for (let i=0;i<7;i++) drawSprite(100+i*28,180+(i%3)*55,{w:18,h:24,body:'#d8c083',mantle:'#8b7235'});
    for (let i=0;i<7;i++) drawSprite(700+i*28,330-(i%3)*52,{w:18,h:24,body:'#9e4c38',mantle:'#5b1e18'});
    drawGoliath(710,state.aim.fall ? 310 : 188);
  }

  function drawGoliath(x,y){
    if (assets.goliath) {
      ellipse(x+50,y+137,56,12,'rgba(0,0,0,.25)');
      ctx.drawImage(assets.goliath,x-12,y-8,122,154);
    } else {
      drawSprite(x,y,{w:58,h:76,body:'#8e4c38',mantle:'#4a1d17'});
    }
    drawText('Golias',x+52,y+148,15,theme.text,'center');
  }

  function drawHerd(){
    const pulse = 1 + Math.sin(performance.now()/260)*.08;
    for (const s of state.herd) {
      ctx.save();
      ctx.lineWidth = s.done ? 3 : 2;
      ctx.strokeStyle = s.done ? 'rgba(145,220,120,.85)' : 'rgba(245,211,100,.76)';
      ctx.fillStyle = s.done ? 'rgba(70,130,55,.16)' : 'rgba(245,211,100,.10)';
      ctx.beginPath(); ctx.ellipse(s.x,s.y,34*pulse,24*pulse,0,0,Math.PI*2); ctx.fill(); ctx.stroke();
      if (s.done) {
        ctx.strokeStyle='#e9ffd7'; ctx.lineWidth=4; ctx.beginPath(); ctx.moveTo(s.x-10,s.y+1); ctx.lineTo(s.x-2,s.y+9); ctx.lineTo(s.x+14,s.y-10); ctx.stroke();
      }
      ctx.restore();
    }
  }

  function drawQuest(){
    const text = scenes[state.scene].objective();
    roundRect(22,H-74,690,46,10,'rgba(24,13,3,.76)','rgba(201,168,76,.38)');
    drawText(text,42,H-44,13,'rgba(245,230,200,.94)', 'left', 700);
  }

  function drawTitle(){
    drawBase();
    roundRect(110,100,740,280,16,'rgba(24,13,3,.94)',theme.border);
    drawText('Davi',W/2,150,42,theme.primary,'center');
    wrap('Um RPG bíblico sobre obediência, coragem e confiança em Deus. Comece no pasto de Belém e viva os acontecimentos de 1 Samuel 16-17 com tarefas, diálogos e escolhas fiéis ao texto bíblico.',165,203,630,30,20,theme.text);
    drawText('Pressione E ou Espaço para começar',W/2,326,19,theme.primary,'center');
  }

  function drawDialog(){
    const d = state.dialog;
    const text = (d.lines[d.i] || '').slice(0, Math.floor(d.shown));
    roundRect(44,372,872,156,12,'rgba(24,13,3,.95)',theme.border);
    roundRect(68,402,92,92,8,'rgba(0,0,0,.35)',theme.border);
    const img = assets.portraits[d.speaker];
    if (img) ctx.drawImage(img,74,408,80,80);
    else ellipse(114,448,34,34,'rgba(201,168,76,.28)',theme.border);
    drawText(d.speaker.toUpperCase(),184,412,18,d.color || theme.primary);
    wrap('"' + text + '"',184,448,650,25,19,theme.text);
    drawText('[E] Continuar',812,503,15,theme.primary,'center');
  }

  function drawCutscene(){
    const c = state.cutscene;
    rect(0,0,W,H,'#130802');
    rect(0,0,W,55,'rgba(26,14,0,.94)');
    drawText(c.title,24,35,24,theme.primary);
    const img = assets.cutscenes[c.key];
    if (img) {
      const box={x:90,y:82,w:780,h:305};
      roundRect(box.x-8,box.y-8,box.w+16,box.h+16,10,'rgba(0,0,0,.35)',theme.border);
      const s=Math.min(box.w/img.width,box.h/img.height), dw=img.width*s, dh=img.height*s;
      ctx.drawImage(img,box.x+(box.w-dw)/2,box.y+(box.h-dh)/2,dw,dh);
    }
    roundRect(70,410,820,105,12,'rgba(24,13,3,.94)',theme.border);
    wrap('"' + (c.lines[c.i] || '').slice(0,Math.floor(c.shown)) + '"',100,445,710,25,20,theme.text);
    drawText('[E] Continuar',795,492,15,theme.primary,'center');
  }

  function drawStones(){
    drawBase();
    rect(75,105,810,320,'#4e9dad');
    rect(75,150,810,38,'rgba(255,255,255,.09)');
    for (const s of state.stones) {
      ctx.beginPath(); ctx.ellipse(s.x,s.y,s.r+6,s.r,s.smooth?0:.6,0,Math.PI*2);
      ctx.fillStyle = s.picked ? theme.primary : (s.smooth ? '#d7d2c2' : '#6e6258');
      ctx.fill(); ctx.strokeStyle=s.smooth?'#ece6d4':'#332c28'; ctx.stroke();
    }
    const picked = state.stones.filter(s=>s.smooth && s.picked).length;
    roundRect(44,445,872,80,10,'rgba(24,13,3,.9)',theme.border);
    drawText('Cinco Pedras Lisas',70,475,20,theme.primary);
    drawText('Clique nas 5 pedras lisas do riacho. Selecionadas: ' + picked + '/5',70,504,16,theme.text);
  }

  function drawAim(){
    drawBase(); drawSceneActors(); drawPlayer();
    const a = state.aim;
    ctx.beginPath(); ctx.arc(a.x,a.y,a.r,0,Math.PI*2); ctx.fillStyle='rgba(201,168,76,.26)'; ctx.fill();
    ctx.strokeStyle=theme.primary; ctx.lineWidth=3; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(a.x-46,a.y); ctx.lineTo(a.x+46,a.y); ctx.moveTo(a.x,a.y-46); ctx.lineTo(a.x,a.y+46); ctx.stroke();
    roundRect(45,450,870,66,10,'rgba(24,13,3,.9)',theme.border);
    drawText('A Funda de Davi',70,478,20,theme.primary);
    drawText('Clique no alvo quando passar pela testa de Golias. Tentativas: ' + a.tries,70,506,16,theme.text);
  }

  function drawFinal(){
    drawBase();
    roundRect(100,95,760,350,14,'rgba(24,13,3,.94)',theme.border);
    drawText('Davi',W/2,150,42,theme.primary,'center');
    wrap('Davi prevaleceu contra o filisteu com uma funda e uma pedra. A vitória não veio por espada nem por lança, mas pelo Senhor, diante de Israel e dos filisteus. (1 Samuel 17:49-51)',150,205,660,32,21,theme.text);
    drawText('RPG concluído',W/2,382,24,theme.primary,'center');
  }

  function drawHud(){
    if (state.mode === 'herd') {
      roundRect(24,68,460,84,8,'rgba(24,13,3,.84)',theme.border);
      drawText('Guardar o Rebanho',44,96,19,theme.primary);
      drawText('Aproxime-se das ovelhas destacadas no pasto.',44,124,15,theme.text);
      drawText('Cuidadas: ' + state.herd.filter(s=>s.done).length + '/' + state.herd.length,44,144,13,'rgba(245,230,200,.84)');
    }
  }

  function draw(){
    ctx.clearRect(0,0,W,H);
    ctx.save();
    if (state.mode === 'title') drawTitle();
    else if (state.mode === 'cutscene') drawCutscene();
    else if (state.mode === 'stones') drawStones();
    else if (state.mode === 'aim') drawAim();
    else if (state.mode === 'final') drawFinal();
    else {
      drawBase(); drawSceneActors(); drawPlayer(); drawQuest(); drawHud();
      if (state.dialog) drawDialog();
    }
    if (state.toastTime > 0 && state.toast) {
      roundRect(250,500,460,38,8,'rgba(24,13,3,.9)',theme.border);
      drawText(state.toast,480,525,15,theme.primary,'center');
    }
    if (state.glow > 0) {
      const p=center(); ctx.beginPath(); ctx.arc(p.x,p.y-40,28+Math.sin(state.glow/6)*5,0,Math.PI*2); ctx.strokeStyle=theme.primary; ctx.lineWidth=3; ctx.stroke();
    }
    if (state.fade > 0) { ctx.fillStyle=`rgba(0,0,0,${state.fade})`; ctx.fillRect(0,0,W,H); }
    ctx.restore();
  }

  function click(e){
    const rectCanvas = canvas.getBoundingClientRect();
    const x = (e.clientX - rectCanvas.left) * (W / rectCanvas.width);
    const y = (e.clientY - rectCanvas.top) * (H / rectCanvas.height);
    if (state.mode === 'stones') {
      for (const s of state.stones) {
        if (!s.picked && Math.hypot(x-s.x,y-s.y) <= s.r+10) {
          if (s.smooth) s.picked = true;
          else toast('Essa pedra é irregular.');
        }
      }
      if (state.stones.filter(s=>s.smooth && s.picked).length >= 5) {
        state.progress.stones = true; state.mode = 'explore'; post('minigame_completed',{name:'cinco_pedras'});
        startDialog('Davi',theme.primary,['Davi escolhe cinco pedras lisas do riacho e as põe em sua bolsa de pastor. (1 Samuel 17:40)']);
      }
    }
    if (state.mode === 'aim') {
      const hit = Math.hypot(x-state.aim.x,y-state.aim.y) <= state.aim.r && state.aim.x > 720 && state.aim.x < 790 && state.aim.y > 160 && state.aim.y < 225;
      if (hit) {
        state.aim.fall = 150; state.mode = 'final'; state.progress.completed = true; post('rpg_completed',{story:'Davi'});
      } else {
        state.aim.tries -= 1;
        if (state.aim.tries <= 0) { state.aim.tries = 3; toast('Respire, observe o alvo e tente novamente.'); }
      }
    }
  }

  function loop(now){
    const dt = Math.min(40, now - state.last);
    state.last = now;
    update(dt); draw();
    requestAnimationFrame(loop);
  }

  window.addEventListener('keydown', e => {
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','Spacebar','w','a','s','d','e'].includes(k) || e.key === ' ') e.preventDefault();
    keys[k] = true;
    if (k === 'e' || e.key === ' ' || k === 'Spacebar') interact();
  });
  window.addEventListener('keyup', e => { keys[e.key.length === 1 ? e.key.toLowerCase() : e.key] = false; });
  canvas.addEventListener('click', click);
  requestAnimationFrame(loop);
})();
