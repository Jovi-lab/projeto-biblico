import base64
import html
import json
import mimetypes
import os
import random

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from src.carregador import Carregador
from src.ia_helper import IAHelper


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ia = IAHelper(GROQ_API_KEY)

st.set_page_config(
    page_title="Projeto Biblico",
    page_icon="PB",
    layout="wide",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
* { box-sizing: border-box; }
.stApp { background: #050607 !important; color: #f7f5ef; }
.block-container { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 4rem; }
header[data-testid="stHeader"] { background: transparent; }
div[data-testid="stToolbar"] { right: 1rem; }

/* Streaming home */
.streaming-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}
.brand-lockup {
    display: flex;
    align-items: center;
    gap: .7rem;
    color: #f7f5ef;
    font-family: Inter, sans-serif;
    font-weight: 800;
    letter-spacing: 0;
    font-size: 1.05rem;
}
.brand-mark {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    background: #d9a441;
    color: #120f08;
    font-weight: 900;
}
.topbar-meta {
    color: #a9aaa7;
    font: 600 .8rem Inter, sans-serif;
}
.hero-banner {
    position: relative;
    min-height: 430px;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    padding: clamp(1.4rem, 5vw, 3.4rem);
    margin-bottom: 1.6rem;
    background-size: cover;
    background-position: center;
    isolation: isolate;
    box-shadow: 0 24px 70px rgba(0,0,0,.42);
}
.hero-banner::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(5,6,7,.94) 0%, rgba(5,6,7,.72) 42%, rgba(5,6,7,.18) 100%),
        linear-gradient(0deg, rgba(5,6,7,.92) 0%, rgba(5,6,7,.05) 58%);
    z-index: -1;
}
.hero-content { max-width: 610px; }
.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    color: #f3c565;
    font: 800 .76rem Inter, sans-serif;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: .8rem;
}
.hero-title {
    font: 800 clamp(2.4rem, 6vw, 4.8rem)/.92 Inter, sans-serif;
    color: #fffaf0;
    letter-spacing: 0;
    margin: 0 0 .85rem 0;
}
.hero-copy {
    font: 500 1rem/1.65 Inter, sans-serif;
    color: #dedbd2;
    max-width: 54ch;
    margin: 0 0 1.1rem 0;
}
.hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    margin-top: .7rem;
}
.hero-tag {
    border: 1px solid rgba(255,255,255,.18);
    background: rgba(255,255,255,.08);
    color: #f7f5ef;
    border-radius: 999px;
    padding: .34rem .7rem;
    font: 700 .76rem Inter, sans-serif;
}
.shelf-title {
    color: #fffaf0;
    font: 800 1.18rem Inter, sans-serif;
    margin: .6rem 0 .9rem 0;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #121417 !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 8px !important;
    overflow: hidden;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px) scale(1.015);
    border-color: rgba(243,197,101,.66) !important;
    box-shadow: 0 18px 44px rgba(0,0,0,.36), 0 0 0 1px rgba(243,197,101,.14);
}
.story-card-title {
    color: #fffaf0;
    font: 800 1rem/1.25 Inter, sans-serif;
    margin: .55rem 0 .12rem;
}
.story-card-meta {
    color: #f3c565;
    font: 800 .72rem Inter, sans-serif;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: .45rem;
}
.story-card-copy {
    color: #b8b9b4;
    font: 500 .86rem/1.45 Inter, sans-serif;
    min-height: 3.7rem;
}
.locked-poster {
    aspect-ratio: 4 / 5;
    border-radius: 6px;
    display: grid;
    place-items: center;
    background:
        linear-gradient(145deg, rgba(217,164,65,.22), rgba(27,30,34,.92)),
        repeating-linear-gradient(45deg, rgba(255,255,255,.05) 0 8px, transparent 8px 16px);
    color: #f7f5ef;
    font: 800 2rem Inter, sans-serif;
}
.stButton > button {
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,.16);
    background: #f3c565;
    color: #120f08;
    font-family: Inter, sans-serif;
    font-weight: 800;
    min-height: 2.8rem;
}
.stButton > button:hover {
    border-color: #fff0bd;
    background: #ffd477;
    color: #120f08;
}
.stButton > button:disabled {
    background: #2a2d31;
    color: #8e918d;
    border-color: rgba(255,255,255,.08);
}

/* Story experience */
.story-shell {
    max-width: 900px;
    margin: 0 auto;
    color: var(--story-text, #f5e6c8);
}
.story-text {
    font-family: var(--story-font, Georgia, serif);
    color: var(--story-text, #f5e6c8);
    font-size: 17px;
    line-height: 1.9;
    background: var(--story-panel, rgba(65, 37, 13, .72));
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--story-border, #8b6914);
    box-shadow: inset 0 0 40px rgba(255, 231, 168, .05);
    white-space: pre-wrap;
    word-break: break-word;
}
.story-title {
    font-family: var(--story-font, Georgia, serif);
    color: var(--story-primary, #c9a84c);
    font-size: 26px;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 0 2px 16px rgba(0, 0, 0, .35);
}
.story-ref {
    font-family: var(--story-font, Georgia, serif);
    color: var(--story-muted, #d8c384);
    font-size: 14px;
    margin-top: 0.5rem;
}
.story-box {
    background: var(--story-panel, rgba(65, 37, 13, .72));
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--story-border, #8b6914);
    margin-bottom: 1rem;
    box-shadow: 0 18px 50px rgba(0, 0, 0, .16);
}
.story-question {
    font-family: var(--story-font, Georgia, serif);
    color: var(--story-text, #f5e6c8);
    font-size: 18px;
    line-height: 1.7;
}
.story-label {
    font-family: var(--story-font, Georgia, serif);
    color: var(--story-primary, #c9a84c);
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 0.5rem;
}
.story-nav {
    font-family: var(--story-font, Georgia, serif);
    color: var(--story-muted, #d8c384);
    font-size: 14px;
    background: var(--story-panel, rgba(65, 37, 13, .72));
    border: 1px solid var(--story-border, #8b6914);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}
@media (max-width: 720px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .hero-banner { min-height: 500px; align-items: flex-end; }
    .topbar-meta { display: none; }
}
</style>
""",
    unsafe_allow_html=True,
)

carregador = Carregador("data/historias.json")
historias_data = carregador.carregar()


def init_state():
    defaults = {
        "tela": "inicio",
        "historia_idx": None,
        "cena_idx": 0,
        "fase": "texto",
        "minijogo_dados": None,
        "ordenacao_itens": [],
        "ordenacao_concluida": False,
        "desafio_concluido": False,
        "final_epico": None,
        "rpg_finalizado": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def local_image_src(path):
    if not path or not os.path.exists(path):
        return ""
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def escape(value):
    return html.escape(str(value or ""), quote=True)


DEFAULT_TEMA = {
    "fundo": "#1a0e00",
    "cor_primaria": "#C9A84C",
    "cor_texto": "#F5E6C8",
    "cor_borda": "#8B6914",
    "fonte": "Cinzel",
    "fonte_url": "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap",
    "atmosfera": "pergaminho",
}


def tema_da_historia(historia):
    tema = DEFAULT_TEMA.copy()
    tema.update(historia.get("tema") or {})
    return tema


def hex_to_rgba(hex_color, alpha):
    color = str(hex_color or "#000000").strip().lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    except (ValueError, IndexError):
        r, g, b = 0, 0, 0
    return f"rgba({r}, {g}, {b}, {alpha})"


def textura_atmosfera(tema):
    atmosfera = tema.get("atmosfera", "pergaminho")
    fundo = tema["fundo"]
    primaria = tema["cor_primaria"]
    if atmosfera == "oceano":
        return (
            f"radial-gradient(circle at 18% 18%, {hex_to_rgba(primaria, .22)}, transparent 24%),"
            f"radial-gradient(circle at 82% 34%, rgba(91, 230, 222, .16), transparent 20%),"
            f"linear-gradient(180deg, {hex_to_rgba(fundo, .96)}, #02070c 100%)"
        )
    if atmosfera == "exodo":
        return (
            f"radial-gradient(circle at 72% 18%, {hex_to_rgba(primaria, .30)}, transparent 28%),"
            f"linear-gradient(135deg, {hex_to_rgba(fundo, .98)}, #3d1209 58%, #130706 100%)"
        )
    return (
        f"radial-gradient(circle at 22% 12%, {hex_to_rgba(primaria, .18)}, transparent 26%),"
        f"linear-gradient(135deg, {hex_to_rgba(fundo, .96)}, #3a210d 54%, #100905 100%)"
    )


def aplicar_tema(historia):
    tema = tema_da_historia(historia)
    fonte_url = tema.get("fonte_url", "")
    fonte = tema.get("fonte", "Georgia")
    primaria = tema["cor_primaria"]
    texto = tema["cor_texto"]
    borda = tema["cor_borda"]
    fundo = tema["fundo"]
    panel = hex_to_rgba(fundo, .72)
    muted = hex_to_rgba(texto, .72)
    texture = textura_atmosfera(tema)
    import_font = f"@import url('{fonte_url}');" if fonte_url else ""

    st.markdown(
        f"""
        <style>
        {import_font}
        .stApp {{
            background: {texture} !important;
        }}
        .stApp, .story-shell {{
            --story-font: '{fonte}', Georgia, serif;
            --story-primary: {primaria};
            --story-text: {texto};
            --story-border: {borda};
            --story-panel: {panel};
            --story-muted: {muted};
        }}
        .stButton > button {{
            background: {primaria};
            color: #1a1207;
            border-color: {borda};
            font-family: '{fonte}', Georgia, serif;
        }}
        .stButton > button:hover {{
            background: {hex_to_rgba(primaria, .88)};
            color: #1a1207;
            border-color: {texto};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return tema


def historia_bloqueada(historia):
    return bool(historia.get("bloqueada")) or not historia.get("cenas")


def resetar_jogo_para_historia(indice):
    historia = historias_data[indice]
    st.session_state.historia_idx = indice
    st.session_state.cena_idx = 0
    st.session_state.fase = "texto"
    st.session_state.minijogo_dados = None
    st.session_state.ordenacao_itens = []
    st.session_state.ordenacao_concluida = False
    st.session_state.desafio_concluido = False
    st.session_state.final_epico = None
    st.session_state.rpg_finalizado = False
    st.session_state.tela = "rpg" if historia.get("modo") == "rpg" else "cena"


def mostrar_imagem(caminho):
    if caminho and os.path.exists(caminho):
        st.image(Image.open(caminho), use_container_width=True)
        return True
    return False


def tela_digitada(titulo, texto, referencia="", tema=None):
    tema = tema or DEFAULT_TEMA
    titulo_js = json.dumps(titulo or "", ensure_ascii=True)
    texto_js = json.dumps(texto or "", ensure_ascii=True)
    ref_js = json.dumps(referencia or "", ensure_ascii=True)
    altura = min(220 + len(texto or "") // 2, 900)
    fonte_url = tema.get("fonte_url", "")
    fonte = tema.get("fonte", "Georgia")
    primaria = tema["cor_primaria"]
    texto_cor = tema["cor_texto"]
    borda = tema["cor_borda"]
    fundo = tema["fundo"]
    panel = hex_to_rgba(fundo, .74)
    muted = hex_to_rgba(texto_cor, .72)
    texture = textura_atmosfera(tema)
    import_font = f"@import url('{fonte_url}');" if fonte_url else ""
    html_component = f"""
    <style>
    {import_font}
    body {{ margin:0; padding:0; background:transparent; overflow-x:hidden; }}
    #wrap {{
        background:{texture};
        padding:1.5rem 1rem;
        border-radius:8px;
    }}
    #titulo {{
        font-family:'{fonte}', Georgia, serif;
        color:{primaria};
        font-size:26px;
        text-align:center;
        margin-bottom:1.5rem;
        text-shadow:0 2px 16px rgba(0,0,0,.36);
        min-height:40px;
        font-weight:700;
    }}
    #caixa {{
        font-family:'{fonte}', Georgia, serif;
        color:{texto_cor};
        font-size:17px;
        line-height:1.9;
        background:{panel};
        padding:1.5rem;
        border-radius:8px;
        border:1px solid {borda};
        box-shadow:inset 0 0 46px rgba(255, 231, 168, .06);
        white-space:pre-wrap;
        word-break:break-word;
    }}
    #ref {{
        font-family:'{fonte}', Georgia, serif;
        color:{muted};
        font-size:14px;
        margin-top:0.75rem;
    }}
    </style>
    <div id="wrap">
        <div id="titulo"></div>
        <div id="caixa"></div>
        <div id="ref"></div>
    </div>
    <script>
    (function(){{
        const titulo = {titulo_js};
        const texto = {texto_js};
        const ref = {ref_js};
        const elTitulo = document.getElementById('titulo');
        const elCaixa = document.getElementById('caixa');
        const elRef = document.getElementById('ref');
        async function digitar(el, str, delay){{
            for (const c of str) {{
                el.textContent += c;
                await new Promise(r => setTimeout(r, delay));
            }}
        }}
        async function run(){{
            await digitar(elTitulo, titulo, 55);
            await new Promise(r => setTimeout(r, 300));
            await digitar(elCaixa, texto, 16);
            await new Promise(r => setTimeout(r, 200));
            if (ref) await digitar(elRef, 'Referencia: ' + ref, 25);
        }}
        run();
    }})();
    </script>
    """
    st.components.v1.html(html_component, height=altura, scrolling=False)


def tela_digitada_simples(texto, tema=None):
    tema = tema or DEFAULT_TEMA
    texto_js = json.dumps(texto or "", ensure_ascii=True)
    altura = min(170 + len(texto or "") // 2, 800)
    fonte_url = tema.get("fonte_url", "")
    fonte = tema.get("fonte", "Georgia")
    texto_cor = tema["cor_texto"]
    borda = tema["cor_borda"]
    fundo = tema["fundo"]
    panel = hex_to_rgba(fundo, .74)
    import_font = f"@import url('{fonte_url}');" if fonte_url else ""
    html_component = f"""
    <style>
    {import_font}
    body {{ margin:0; padding:0; background:transparent; }}
    #caixa {{
        font-family:'{fonte}', Georgia, serif;
        color:{texto_cor};
        font-size:17px;
        line-height:1.9;
        background:{panel};
        padding:1.5rem;
        border-radius:8px;
        border:1px solid {borda};
        white-space:pre-wrap;
        word-break:break-word;
    }}
    </style>
    <div id="caixa"></div>
    <script>
    (function(){{
        const texto = {texto_js};
        const el = document.getElementById('caixa');
        async function digitar(){{
            for (const c of texto) {{
                el.textContent += c;
                await new Promise(r => setTimeout(r, 16));
            }}
        }}
        digitar();
    }})();
    </script>
    """
    st.components.v1.html(html_component, height=altura, scrolling=False)


def minijogo_mira(tema=None):
    tema = tema or DEFAULT_TEMA
    fonte_url = tema.get("fonte_url", "")
    fonte = tema.get("fonte", "Georgia")
    primaria = tema["cor_primaria"]
    texto_cor = tema["cor_texto"]
    borda = tema["cor_borda"]
    fundo = tema["fundo"]
    primary_soft = hex_to_rgba(primaria, .48)
    primary_faint = hex_to_rgba(primaria, .18)
    panel = hex_to_rgba(fundo, .82)
    import_font = f"@import url('{fonte_url}');" if fonte_url else ""
    mira_html = """
    <style>
    __IMPORT_FONT__
    body { margin:0; padding:0; background:transparent; }
    #miraWrap {
        width: min(100%, 720px);
        margin: 0 auto;
        border: 2px solid __BORDA__;
        border-radius: 8px;
        overflow: hidden;
        background: __PANEL__;
        box-shadow: 0 22px 60px rgba(0,0,0,.25);
    }
    #miraStage {
        position: relative;
        width: 100%;
        min-height: 320px;
        background: __FUNDO__;
    }
    #bgImg {
        width: 100%;
        height: auto;
        display: block;
        filter: brightness(0.62) sepia(0.2);
        user-select: none;
        -webkit-user-drag: none;
    }
    #miraCanvas {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        cursor: crosshair;
        touch-action: manipulation;
    }
    #miraInfo {
        background: __PANEL__;
        border-top: 1px solid __BORDA__;
        padding: 12px 16px;
        font-family: '__FONTE__', Georgia, serif;
    }
    #miraResult { color: __TEXTO__; font-size: 15px; margin-bottom: 5px; min-height: 22px; }
    #miraTent { color: __PRIMARIA__; font-size: 13px; }
    </style>

    <div id="miraWrap">
        <div id="miraStage">
            <img id="bgImg" src="app/static/capa_mira.png" alt="">
            <canvas id="miraCanvas"></canvas>
        </div>
        <div id="miraInfo">
            <div id="miraResult">Mire no alvo e clique no momento certo.</div>
            <div id="miraTent">Tentativas restantes: 3</div>
        </div>
    </div>

    <script>
    (function(){
        const stage = document.getElementById('miraStage');
        const canvas = document.getElementById('miraCanvas');
        const ctx = canvas.getContext('2d');
        const res = document.getElementById('miraResult');
        const tent = document.getElementById('miraTent');
        const bg = document.getElementById('bgImg');

        let width = 640, height = 380, dpr = 1;
        let x = 0, y = 0, dx = 2.4, dy = 1.3;
        let raio = 30, tentativas = 3, jogando = true, started = false;

        function syncCanvas(){
            const rect = stage.getBoundingClientRect();
            width = Math.max(320, Math.round(rect.width));
            height = Math.max(300, Math.round(rect.height));
            dpr = Math.max(1, window.devicePixelRatio || 1);
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';
            canvas.width = Math.round(width * dpr);
            canvas.height = Math.round(height * dpr);
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            raio = Math.max(22, Math.min(34, width * 0.05));
            x = clamp(x || width * 0.52, raio, width - raio);
            y = clamp(y || height * 0.24, raio, height - raio);
        }

        function clamp(value, min, max){ return Math.max(min, Math.min(max, value)); }

        function init(){
            syncCanvas();
            x = width * 0.52;
            y = height * 0.23;
            if (!started) {
                started = true;
                requestAnimationFrame(animar);
            }
        }

        function desenhar(){
            ctx.clearRect(0, 0, width, height);
            const pulse = 1 + Math.sin(Date.now() / 130) * 0.06;
            const r = raio * pulse;
            const g = ctx.createRadialGradient(x, y, 2, x, y, r);
            g.addColorStop(0, '__PRIMARIA__');
            g.addColorStop(0.38, '__PRIMARY_SOFT__');
            g.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fillStyle = g;
            ctx.fill();
            ctx.strokeStyle = '__PRIMARIA__';
            ctx.lineWidth = 2;
            ctx.stroke();
            [0.48, 0.76].forEach(scale => {
                ctx.beginPath();
                ctx.arc(x, y, r * scale, 0, Math.PI * 2);
                ctx.strokeStyle = '__PRIMARY_SOFT__';
                ctx.lineWidth = 1;
                ctx.stroke();
            });
            ctx.strokeStyle = '__PRIMARY_FAINT__';
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(x - r - 18, y); ctx.lineTo(x + r + 18, y); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(x, y - r - 18); ctx.lineTo(x, y + r + 18); ctx.stroke();
            tent.textContent = 'Tentativas restantes: ' + tentativas;
        }

        function animar(){
            if (!jogando) { desenhar(); return; }
            const headBandTop = height * 0.12;
            const headBandBottom = height * 0.48;
            x += dx;
            y += dy;
            if (x + raio > width || x - raio < 0) dx *= -1;
            if (y + raio > headBandBottom || y - raio < headBandTop) dy *= -1;
            x = clamp(x, raio, width - raio);
            y = clamp(y, headBandTop + raio, headBandBottom - raio);
            dx = clamp(dx + (Math.random() - 0.5) * 0.07, -3.2, 3.2);
            dy = clamp(dy + (Math.random() - 0.5) * 0.05, -2.2, 2.2);
            desenhar();
            requestAnimationFrame(animar);
        }

        function handleClick(e){
            if (!jogando) return;
            const rect = canvas.getBoundingClientRect();
            const cx = (e.clientX - rect.left) * (width / rect.width);
            const cy = (e.clientY - rect.top) * (height / rect.height);
            const dist = Math.hypot(cx - x, cy - y);
            if (dist <= raio) {
                jogando = false;
                res.style.color = '__PRIMARIA__';
                res.textContent = 'Acertou! A pedra atingiu o alvo.';
            } else {
                tentativas -= 1;
                if (tentativas <= 0) {
                    jogando = false;
                    res.style.color = '#FF5555';
                    res.textContent = 'Tentativas encerradas. Reinicie para tentar de novo.';
                } else {
                    res.style.color = '__TEXTO__';
                    res.textContent = 'Errou. Ajuste a mira e tente novamente.';
                }
            }
            desenhar();
        }

        canvas.addEventListener('click', handleClick);
        new ResizeObserver(syncCanvas).observe(stage);
        bg.addEventListener('load', init, { once: true });
        bg.addEventListener('error', init, { once: true });
        if (bg.complete) init();
        setTimeout(init, 350);
    })();
    </script>
    """
    mira_html = (
        mira_html.replace("__IMPORT_FONT__", import_font)
        .replace("__BORDA__", borda)
        .replace("__PANEL__", panel)
        .replace("__FUNDO__", fundo)
        .replace("__FONTE__", fonte)
        .replace("__TEXTO__", texto_cor)
        .replace("__PRIMARIA__", primaria)
        .replace("__PRIMARY_SOFT__", primary_soft)
        .replace("__PRIMARY_FAINT__", primary_faint)
    )
    st.components.v1.html(mira_html, height=590)
    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("Concluir desafio", use_container_width=True):
        st.session_state.fase = "proxima"
        st.rerun()
    if col2.button("Tentar novamente", use_container_width=True):
        st.rerun()


def minijogo_ordenacao(dados, tema=None):
    if "eventos" not in dados:
        st.error("Erro ao carregar o desafio.")
        if st.button("Recarregar"):
            st.session_state.minijogo_dados = None
            st.rerun()
        return

    eventos_corretos = dados["eventos"]
    if not st.session_state.ordenacao_itens:
        embaralhado = eventos_corretos.copy()
        random.shuffle(embaralhado)
        st.session_state.ordenacao_itens = embaralhado

    st.markdown('<div class="story-label">Coloque os eventos na ordem correta</div>', unsafe_allow_html=True)
    st.markdown('<div class="story-ref">Use os botoes para reordenar</div>', unsafe_allow_html=True)
    st.divider()

    itens = st.session_state.ordenacao_itens
    for i, evento in enumerate(itens):
        col1, col2, col3 = st.columns([7, 1, 1])
        col1.markdown(
            f'<div class="story-ref" style="font-size:15px;">{i + 1}. {escape(evento)}</div>',
            unsafe_allow_html=True,
        )
        if i > 0:
            if col2.button("Subir", key=f"up_{i}"):
                itens[i], itens[i - 1] = itens[i - 1], itens[i]
                st.rerun()
        if i < len(itens) - 1:
            if col3.button("Descer", key=f"down_{i}"):
                itens[i], itens[i + 1] = itens[i + 1], itens[i]
                st.rerun()

    st.divider()
    if st.button("Verificar ordem", use_container_width=True):
        if itens == eventos_corretos:
            st.session_state.ordenacao_concluida = True
            st.rerun()
        else:
            st.error("A ordem ainda nao esta correta. Tente novamente.")

    if st.session_state.ordenacao_concluida:
        st.success("Ordem correta!")
        if st.button("Ver o final ->", use_container_width=True):
            st.session_state.desafio_concluido = True
            st.rerun()


def preparar_minijogo(cena):
    minijogo = cena.get("minijogo", {})
    tipo = minijogo.get("tipo")

    if tipo == "mira":
        return minijogo

    return minijogo


def tela_rpg_davi(historia, tema):
    primaria = tema["cor_primaria"]
    texto = tema["cor_texto"]
    borda = tema["cor_borda"]
    fundo = tema["fundo"]
    fonte = tema.get("fonte", "Georgia")
    html_code = """
    <style>
      body { margin: 0; background: transparent; }
      #rpgWrap {
        width: min(100%, 980px);
        margin: 0 auto;
        border: 2px solid __BORDA__;
        border-radius: 8px;
        overflow: hidden;
        background: #150a02;
        box-shadow: 0 28px 90px rgba(0,0,0,.45);
      }
      #rpgCanvas {
        width: 100%;
        display: block;
        outline: none;
        background: __FUNDO__;
      }
      #rpgHelp {
        padding: 10px 14px;
        color: __TEXTO__;
        background: rgba(20, 11, 3, .92);
        border-top: 1px solid __BORDA__;
        font: 14px __FONTE__, Georgia, serif;
      }
    </style>
    <div id="rpgWrap">
      <canvas id="rpgCanvas" width="960" height="560" tabindex="0"></canvas>
      <div id="rpgHelp">Setas ou WASD para mover. E ou Espaço para interagir e avançar diálogos.</div>
    </div>
    <script>
    (function(){
      const canvas = document.getElementById('rpgCanvas');
      const ctx = canvas.getContext('2d');
      canvas.focus();
      canvas.addEventListener('click', () => canvas.focus());

      const theme = {
        primary: '__PRIMARIA__',
        text: '__TEXTO__',
        border: '__BORDA__',
        bg: '__FUNDO__',
        font: '__FONTE__'
      };

      const W = canvas.width, H = canvas.height;
      const keys = {};
      const player = { x: 125, y: 322, w: 28, h: 38, speed: 2.45, basket: false, dir: 'down' };
      let area = 0;
      let mode = 'intro';
      let last = performance.now();
      let hint = '';
      let toast = '';
      let toastTimer = 0;
      let flash = 0;
      let anoint = 0;
      let armor = 0;
      let goliathFall = 0;
      let cameraShake = 0;
      let typed = { npc: '', lines: [], index: 0, shown: 0, done: null, color: theme.primary };
      let flags = {
        intro: false,
        messenger: false,
        herdDone: false,
        samuel: false,
        anointed: false,
        basket: false,
        eliabe: false,
        soldier: false,
        saul: false,
        armorRefused: false,
        stones: false,
        finalDialog: false,
        goliathDown: false,
        completed: false
      };

      const areas = [
        { name: 'Pasto de Belém', objective: 'Fale com o mensageiro de Jessé.', ground: '#796a31', path: '#bd9656', edge: '#4f3d1e' },
        { name: 'Casa de Jessé', objective: 'Ouça Samuel e receba a missão de Jessé.', ground: '#75502c', path: '#cda363', edge: '#3b2413' },
        { name: 'Acampamento de Israel', objective: 'Procure Eliabe, o soldado e Saul. Depois escolha as pedras.', ground: '#93713e', path: '#d1aa66', edge: '#4d3720' },
        { name: 'Vale de Elá', objective: 'Enfrente Golias confiando no Senhor.', ground: '#9b7b43', path: '#d8b068', edge: '#56341f' }
      ];

      const sheep = [
        {x:210,y:150,vx:.55,vy:.2,in:false},{x:325,y:205,vx:-.35,vy:.45,in:false},
        {x:470,y:138,vx:.35,vy:-.32,in:false},{x:555,y:275,vx:-.42,vy:.2,in:false},
        {x:260,y:410,vx:.25,vy:-.35,in:false}
      ];
      const stones = [
        {x:190,y:160,r:16,smooth:true,hit:false},{x:310,y:130,r:18,smooth:false,hit:false},
        {x:425,y:185,r:15,smooth:true,hit:false},{x:555,y:150,r:17,smooth:true,hit:false},
        {x:690,y:210,r:18,smooth:false,hit:false},{x:255,y:315,r:15,smooth:true,hit:false},
        {x:405,y:350,r:17,smooth:false,hit:false},{x:595,y:335,r:16,smooth:true,hit:false},
        {x:745,y:345,r:18,smooth:false,hit:false}
      ];
      let herdStart = 0;
      let stonesStart = 0;
      let aim = { x: 730, y: 190, dx: 2.4, dy: 1.3, r: 30, tries: 3 };

      function post(event, detail){
        window.parent.postMessage({ source: 'projeto-biblico-rpg', event, detail }, '*');
      }

      function notify(text){
        toast = text;
        toastTimer = 180;
      }

      function startDialog(npc, color, lines, done){
        mode = 'dialog';
        typed = { npc, color: color || theme.primary, lines, index: 0, shown: 0, done };
      }

      function currentLine(){ return typed.lines[typed.index] || ''; }
      function advanceDialog(){
        const line = currentLine();
        if (typed.shown < line.length) { typed.shown = line.length; return; }
        typed.index += 1;
        typed.shown = 0;
        if (typed.index >= typed.lines.length) {
          const done = typed.done;
          mode = 'explore';
          post('dialog_finished', { npc: typed.npc, area: areas[area].name });
          if (done) done();
        }
      }

      function startIntro(){
        startDialog('Narrador', theme.primary, [
          'Belém ainda desperta sob o sol do campo.',
          'Davi cuida das ovelhas de Jessé, sem imaginar que aquele dia mudará sua história.',
          'Aproxime-se do mensageiro e pressione E.'
        ], () => { flags.intro = true; mode = 'explore'; });
      }

      function moveArea(next){
        area = next;
        player.x = 90;
        player.y = 318;
        mode = 'explore';
        notify(areas[area].name);
      }

      function dist(a,b){ return Math.hypot((a.x+a.w/2)-b.x, (a.y+a.h/2)-b.y); }
      function near(x,y,range=58){ return Math.hypot(player.x + player.w/2 - x, player.y + player.h/2 - y) < range; }

      function interact(){
        if (mode === 'intro') { startIntro(); return; }
        if (mode === 'dialog') { advanceDialog(); return; }
        if (mode === 'final') { return; }
        if (mode === 'herd' || mode === 'stones' || mode === 'aim') return;

        if (area === 0) {
          if (!flags.messenger && near(270,270)) {
            startDialog('Mensageiro', '#E6C36A', [
              'Davi, seu pai Jessé te chama em casa.',
              'Samuel, o profeta, está lá.',
              'Antes de partir, reúna o rebanho no curral.'
            ], () => { flags.messenger = true; startHerd(); });
            return;
          }
          if (flags.herdDone && player.x > 860) moveArea(1);
        }

        if (area === 1) {
          if (!flags.samuel && near(510,215)) {
            startDialog('Samuel', theme.primary, [
              'O Senhor não vê como o homem vê.',
              'Pois o homem olha para a aparência.',
              'Mas o Senhor olha para o coração. (1 Samuel 16:7)'
            ], () => { flags.samuel = true; flags.anointed = true; anoint = 120; });
            return;
          }
          if (flags.anointed && !flags.basket && near(325,300)) {
            startDialog('Jessé', '#E8D3A4', [
              'Davi, leve este cesto com comida para seus irmãos no acampamento de Israel.'
            ], () => { flags.basket = true; player.basket = true; });
            return;
          }
          if (flags.basket && player.x > 860) moveArea(2);
        }

        if (area === 2) {
          if (!flags.eliabe && near(285,260)) {
            startDialog('Eliabe', '#D9B076', [
              'Por que desceste aqui?',
              'E a quem deixaste aquelas poucas ovelhas?'
            ], () => { flags.eliabe = true; flash = 80; cameraShake = 30; });
            return;
          }
          if (flags.eliabe && !flags.soldier && near(430,345)) {
            startDialog('Soldado', '#D7DDE8', [
              'Por quarenta dias, manhã e tarde, esse filisteu tem nos desafiado!'
            ], () => { flags.soldier = true; });
            return;
          }
          if (flags.soldier && !flags.saul && near(665,255)) {
            startDialog('Saul', '#D8C083', [
              'Você não pode lutar contra esse filisteu. Você é muito jovem.',
              'Davi: O Senhor que me livrou da pata do leão e do urso me livrará também desse filisteu.'
            ], () => { flags.saul = true; armor = 120; });
            return;
          }
          if (flags.saul && !flags.stones && near(765,430,76)) { startStones(); return; }
          if (flags.stones && player.x > 860) moveArea(3);
        }

        if (area === 3) {
          if (!flags.finalDialog && near(730,245,110)) {
            startDialog('Golias', '#B86E52', [
              'Sou eu um cão para você vir a mim com um cajado?',
              'Davi: Você vem contra mim com espada, lança e dardo.',
              'Davi: Mas eu venho em nome do Senhor dos Exércitos!'
            ], () => { flags.finalDialog = true; startAim(); });
          }
        }
      }

      function startHerd(){
        mode = 'herd';
        herdStart = performance.now();
        player.x = 150; player.y = 280;
        post('minigame_started', { name: 'guardar_rebanho' });
      }

      function updateHerd(dt){
        const pen = {x:720,y:86,w:170,h:140};
        for (const s of sheep) {
          const px = player.x + player.w/2, py = player.y + player.h/2;
          const d = Math.hypot(px - s.x, py - s.y);
          if (d < 44) {
            s.vx += (s.x - px) / Math.max(1,d) * .22;
            s.vy += (s.y - py) / Math.max(1,d) * .22;
          }
          s.x += s.vx; s.y += s.vy;
          s.vx *= .96; s.vy *= .96;
          if (s.x < 50 || s.x > 910) s.vx *= -1;
          if (s.y < 70 || s.y > 500) s.vy *= -1;
          s.x = Math.max(40, Math.min(920, s.x));
          s.y = Math.max(60, Math.min(510, s.y));
          s.in = s.x > pen.x && s.x < pen.x + pen.w && s.y > pen.y && s.y < pen.y + pen.h;
        }
        const elapsed = (performance.now() - herdStart) / 1000;
        if (sheep.every(s => s.in)) {
          flags.herdDone = true;
          mode = 'explore';
          post('minigame_completed', { name: 'guardar_rebanho' });
          startDialog('Davi', theme.primary, ['O rebanho está reunido. Agora posso ir à casa de meu pai.'], null);
        } else if (elapsed > 30) {
          notify('Tente de novo: reúna as ovelhas com calma.');
          sheep.forEach((s,i) => { s.x = 210 + i*70; s.y = 150 + (i%2)*120; s.vx = .4; s.vy = .3; s.in = false; });
          herdStart = performance.now();
        }
      }

      function startStones(){
        mode = 'stones';
        stonesStart = performance.now();
        stones.forEach(s => s.hit = false);
        post('minigame_started', { name: 'escolher_pedras' });
      }

      function startAim(){
        mode = 'aim';
        aim = { x: 730, y: 190, dx: 2.4, dy: 1.3, r: 30, tries: 3 };
        post('minigame_started', { name: 'mira' });
      }

      function finishRpg(){
        flags.completed = true;
        mode = 'final';
        post('rpg_completed', { story: 'Davi' });
      }

      function canvasClick(e){
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (W / rect.width);
        const y = (e.clientY - rect.top) * (H / rect.height);
        if (mode === 'stones') {
          for (const s of stones) {
            if (!s.hit && Math.hypot(x-s.x, y-s.y) <= s.r+4) {
              if (s.smooth) s.hit = true;
              else { flash = 18; }
            }
          }
          if (stones.filter(s => s.smooth && s.hit).length >= 5) {
            flags.stones = true;
            mode = 'explore';
            post('minigame_completed', { name: 'escolher_pedras' });
            startDialog('Davi', theme.primary, ['Cinco pedras lisas foram escolhidas do riacho.'], null);
          }
        }
        if (mode === 'aim') {
          const hit = Math.hypot(x-aim.x, y-aim.y) <= aim.r;
          if (hit) {
            flags.goliathDown = true;
            goliathFall = 150;
            mode = 'cinematic';
            post('minigame_completed', { name: 'mira' });
            setTimeout(finishRpg, 1100);
          } else {
            aim.tries -= 1;
            if (aim.tries <= 0) { aim.tries = 3; notify('Respire e tente novamente.'); }
          }
        }
      }

      function update(dt){
        hint = '';
        if (mode === 'intro') return;
        if (mode === 'dialog') {
          typed.shown = Math.min(currentLine().length, typed.shown + dt * .045);
          return;
        }
        if (mode === 'final') return;
        let movingAllowed = mode === 'explore' || mode === 'herd';
        if (movingAllowed) {
          let dx = 0, dy = 0;
          if (keys.ArrowLeft || keys.a) dx -= 1;
          if (keys.ArrowRight || keys.d) dx += 1;
          if (keys.ArrowUp || keys.w) dy -= 1;
          if (keys.ArrowDown || keys.s) dy += 1;
          if (dx || dy) {
            const len = Math.hypot(dx,dy);
            player.x += dx / len * player.speed;
            player.y += dy / len * player.speed;
            player.dir = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
          }
          player.x = Math.max(24, Math.min(W-44, player.x));
          player.y = Math.max(62, Math.min(H-54, player.y));
        }
        if (mode === 'herd') updateHerd(dt);
        if (mode === 'aim') {
          aim.x += aim.dx; aim.y += aim.dy;
          if (aim.x < 570 || aim.x > 860) aim.dx *= -1;
          if (aim.y < 120 || aim.y > 275) aim.dy *= -1;
        }
        if (flash > 0) flash -= 1;
        if (anoint > 0) anoint -= 1;
        if (armor > 0) armor -= 1;
        if (goliathFall > 0) goliathFall -= 1;
        if (cameraShake > 0) cameraShake -= 1;
        if (toastTimer > 0) toastTimer -= 1;
      }

      function drawText(text, x, y, size=18, color=theme.text, align='left'){
        ctx.fillStyle = color;
        ctx.font = `700 ${size}px ${theme.font}, Georgia, serif`;
        ctx.textAlign = align;
        ctx.fillText(text, x, y);
      }
      function rect(x,y,w,h,c){ ctx.fillStyle=c; ctx.fillRect(x,y,w,h); }
      function ellipse(x,y,rx,ry,c,stroke){
        ctx.beginPath(); ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);
        ctx.fillStyle=c; ctx.fill();
        if (stroke) { ctx.strokeStyle=stroke; ctx.lineWidth=2; ctx.stroke(); }
      }
      function roundRect(x,y,w,h,r,c,stroke){
        ctx.beginPath();
        ctx.roundRect(x,y,w,h,r);
        ctx.fillStyle=c; ctx.fill();
        if (stroke) { ctx.strokeStyle=stroke; ctx.lineWidth=2; ctx.stroke(); }
      }
      function sprite(x,y,w,h,c,label,scale=1, opts={}){
        const sw=w*scale, sh=h*scale;
        ellipse(x+sw/2, y+sh+5, sw*.45, 6*scale, 'rgba(0,0,0,.22)');
        roundRect(x+sw*.16,y+sh*.32,sw*.68,sh*.56,7*scale,c,'rgba(0,0,0,.32)');
        if (opts.mantle) {
          ctx.beginPath();
          ctx.moveTo(x+sw*.18,y+sh*.38); ctx.lineTo(x+sw*.82,y+sh*.38); ctx.lineTo(x+sw*.66,y+sh*.95); ctx.lineTo(x+sw*.32,y+sh*.95); ctx.closePath();
          ctx.fillStyle=opts.mantle; ctx.fill();
        }
        ellipse(x+sw/2,y+sh*.23,sw*.25,sh*.21,'#C98D5A','rgba(53,29,10,.45)');
        rect(x+sw*.28,y+sh*.12,sw*.44,sh*.08,'#37200c');
        drawText(label, x+sw/2, y+sh*.70, 13*scale, opts.text || '#231404', 'center');
      }
      function npc(x,y,c,label,name,opts={}){
        sprite(x-15,y-24,30,42,c,label,1,opts);
        drawText(name, x, y+32, 13, theme.text, 'center');
      }
      function drawTree(x,y){
        rect(x-5,y+18,10,26,'#5b371c');
        ellipse(x,y+12,25,22,'#455f2a','#263915');
        ellipse(x-14,y+22,18,16,'#516c32');
        ellipse(x+14,y+23,18,16,'#516c32');
      }
      function drawRock(x,y,s=1){
        ctx.beginPath(); ctx.ellipse(x,y,16*s,10*s,-.25,0,Math.PI*2);
        ctx.fillStyle='#8b8067'; ctx.fill(); ctx.strokeStyle='#554b3b'; ctx.stroke();
      }
      function drawTent(x,y,color='#b98b54'){
        ctx.beginPath(); ctx.moveTo(x,y+52); ctx.lineTo(x+34,y); ctx.lineTo(x+68,y+52); ctx.closePath();
        ctx.fillStyle=color; ctx.fill(); ctx.strokeStyle='#5a371b'; ctx.lineWidth=2; ctx.stroke();
        rect(x+29,y+30,12,22,'#3b2111');
      }

      function drawAreaBase(){
        const a = areas[area];
        if (cameraShake > 0) ctx.translate((Math.random()-.5)*6, (Math.random()-.5)*4);
        rect(0,0,W,H,a.ground);
        const grad = ctx.createRadialGradient(W*.35,H*.2,30,W*.5,H*.5,620);
        grad.addColorStop(0,'rgba(255,226,150,.13)');
        grad.addColorStop(1,'rgba(20,10,2,.18)');
        ctx.fillStyle=grad; ctx.fillRect(0,55,W,H-55);
        for (let x=0;x<W;x+=48) for (let y=55;y<H;y+=48) {
          ctx.fillStyle = (x+y)%96===0 ? 'rgba(255,255,255,.035)' : 'rgba(0,0,0,.025)';
          ctx.fillRect(x,y,48,48);
        }
        ctx.beginPath();
        ctx.moveTo(0,368); ctx.bezierCurveTo(180,318,330,355,515,302); ctx.bezierCurveTo(690,254,795,300,960,248);
        ctx.lineWidth=54; ctx.strokeStyle=a.path; ctx.stroke();
        ctx.lineWidth=5; ctx.strokeStyle='rgba(82,48,20,.24)'; ctx.stroke();
        rect(0,0,W,55,'rgba(26,14,0,.88)');
        drawText(a.name, 24, 35, 24, theme.primary);
        drawText(a.objective, W-28, 35, 15, theme.text, 'right');
        rect(0,H-8,W,8,a.edge);
        rect(0,55,8,H-55,a.edge);
        rect(W-8,55,8,H-55,a.edge);
      }

      function drawWorld(){
        drawAreaBase();
        if (area === 0) {
          drawTree(83,128); drawTree(135,182); drawTree(595,118); drawTree(638,173);
          drawRock(392,430); drawRock(520,364,.8); drawRock(694,316,.9);
          rect(715,93,185,155,'rgba(94,62,29,.45)');
          ctx.strokeStyle = '#4a2e17'; ctx.lineWidth = 7; ctx.strokeRect(715,93,185,155);
          rect(785,242,48,12,'#bd9656');
          drawText('Curral', 807, 84, 16, theme.text, 'center');
          npc(270,270,'#CDA15A','M','Mensageiro',{mantle:'#7e4c2a'});
          for (const s of sheep) {
            ellipse(s.x,s.y,17,12,s.in ? '#fff8dc' : '#f2f0e6','#7b6d55');
            ellipse(s.x+10,s.y-7,7,6,'#f7f2e6','#7b6d55');
            rect(s.x-8,s.y+9,3,7,'#3c3327'); rect(s.x+7,s.y+9,3,7,'#3c3327');
          }
          if (flags.herdDone) drawText('Saída para a Casa de Jessé', 820, 520, 15, theme.primary, 'center');
          if (!flags.messenger && near(270,270)) hint = 'E: falar com o mensageiro';
          if (flags.herdDone && player.x > 820) hint = 'E: seguir para a casa';
        }
        if (area === 1) {
          roundRect(160,104,640,340,10,'rgba(93,54,24,.80)',theme.border);
          rect(182,128,596,42,'rgba(255,225,160,.10)');
          rect(450,414,70,30,'#2f1a0c');
          drawText('Casa de Jessé', 480, 154, 20, theme.primary, 'center');
          npc(325,300,'#D9B27C','J','Jessé',{mantle:'#6d4528'});
          npc(510,215,'#D4BF74','S','Samuel',{mantle:'#f0d88a'});
          npc(420,315,'#A96A3A','E','Eliabe',{mantle:'#5f321c'});
          npc(590,318,'#A97842','A','Abinadabe',{mantle:'#684024'});
          npc(665,315,'#A97842','S','Samá',{mantle:'#684024'});
          if (!flags.samuel && near(510,215)) hint = 'E: ouvir Samuel';
          if (flags.anointed && !flags.basket && near(325,300)) hint = 'E: falar com Jessé';
          if (flags.basket && player.x > 830) hint = 'E: seguir ao acampamento';
        }
        if (area === 2) {
          for (let i=0;i<5;i++) {
            drawTent(110+i*96,128+(i%2)*48,'#c09759');
          }
          roundRect(610,130,165,125,8,'#8f602f','#3b2413');
          drawText('Tenda de Saul', 692, 116, 16, theme.text, 'center');
          ctx.beginPath(); ctx.moveTo(680,420); ctx.bezierCurveTo(735,395,835,445,925,413); ctx.lineWidth=36; ctx.strokeStyle='#4a8c9d'; ctx.stroke();
          ctx.lineWidth=5; ctx.strokeStyle='rgba(231,255,255,.18)'; ctx.stroke();
          drawText('Riacho', 805, 402, 15, theme.text, 'center');
          npc(285,260,'#B77A42','E','Eliabe',{mantle:'#6d351c'});
          npc(430,345,'#CBD3DC','S','Soldado',{mantle:'#7a8691'});
          npc(665,255,'#C5A153','R','Saul',{mantle:'#875f1d'});
          if (flags.eliabe && flash > 0) drawText('GOLIAS!', 820, 108, 32, '#5b1712', 'center');
          if (!flags.eliabe && near(285,260)) hint = 'E: falar com Eliabe';
          if (flags.eliabe && !flags.soldier && near(430,345)) hint = 'E: falar com o soldado';
          if (flags.soldier && !flags.saul && near(665,255)) hint = 'E: falar com Saul';
          if (flags.saul && !flags.stones && near(765,430,76)) hint = 'E: escolher cinco pedras lisas';
          if (flags.stones && player.x > 830) hint = 'E: seguir ao Vale de Elá';
        }
        if (area === 3) {
          rect(65,130,250,300,'rgba(197,161,83,.22)');
          rect(650,105,250,350,'rgba(92,34,24,.26)');
          drawText('Israel', 190, 112, 18, theme.text, 'center');
          drawText('Filisteus', 775, 88, 18, theme.text, 'center');
          for (let i=0;i<7;i++) sprite(100+i*28,180+(i%3)*55,18,24,'#D8C083','I',.8);
          for (let i=0;i<7;i++) sprite(700+i*28,330-(i%3)*52,18,24,'#9E4C38','F',.8);
          const gy = flags.goliathDown ? 300 + Math.min(90, (150-goliathFall)) : 190;
          sprite(715, gy, 58, 76, '#8E4C38', 'G', 1.6, {mantle:'#4a1d17', text:'#f4d6b5'});
          drawText('Golias', 760, gy+138, 16, theme.text, 'center');
          if (!flags.finalDialog && near(730,245,110)) hint = 'E: enfrentar Golias';
        }
        sprite(player.x, player.y, player.w, player.h, theme.primary, player.basket ? 'D+' : 'D', 1, {mantle:'#8a5b24'});
        if (player.basket) roundRect(player.x+22, player.y+18, 16, 13, 4, '#c59043', '#6b411d');
        if (anoint > 0) {
          ctx.beginPath(); ctx.arc(player.x+14, player.y-8, 28 + Math.sin(anoint/6)*5, 0, Math.PI*2);
          ctx.strokeStyle = theme.primary; ctx.lineWidth = 3; ctx.stroke();
        }
        if (armor > 0) {
          drawText('Saul tenta vestir Davi com armadura, mas Davi a recusa.', W/2, 505, 18, theme.primary, 'center');
        }
      }

      function drawDialog(){
        roundRect(45,382,870,145,12,'rgba(24,13,3,.94)',theme.border);
        drawText('[' + typed.npc.toUpperCase() + ']', 72, 414, 18, typed.color);
        const text = currentLine().slice(0, Math.floor(typed.shown));
        wrapText('"' + text + '"', 72, 450, 790, 24, 19, theme.text);
        drawText('[E] Continuar', 800, 505, 15, theme.primary, 'center');
      }

      function drawIntro(){
        drawAreaBase();
        drawTree(115,150); drawTree(620,140); drawTree(710,205);
        npc(270,270,'#CDA15A','M','Mensageiro',{mantle:'#7e4c2a'});
        for (const s of sheep) ellipse(s.x,s.y,17,12,'#f2f0e6','#7b6d55');
        sprite(player.x, player.y, player.w, player.h, theme.primary, 'D', 1, {mantle:'#8a5b24'});
        roundRect(108,95,744,290,16,'rgba(24,13,3,.88)',theme.border);
        drawText('Davi', W/2, 152, 44, theme.primary, 'center');
        wrapText('Um RPG bíblico top-down: viva a jornada de Davi desde os campos de Belém até o Vale de Elá. Fale com personagens, cumpra tarefas e avance pela história de 1 Samuel 16-17.', 170, 205, 620, 31, 21, theme.text);
        drawText('Pressione E ou Espaço para começar', W/2, 335, 20, theme.primary, 'center');
      }

      function wrapText(text, x, y, maxWidth, lineHeight, size, color){
        ctx.font = `600 ${size}px ${theme.font}, Georgia, serif`;
        ctx.fillStyle = color;
        const words = text.split(' ');
        let line = '';
        for (const word of words) {
          const test = line + word + ' ';
          if (ctx.measureText(test).width > maxWidth && line) {
            ctx.fillText(line, x, y);
            line = word + ' ';
            y += lineHeight;
          } else line = test;
        }
        ctx.fillText(line, x, y);
      }

      function drawHerdHud(){
        const left = Math.max(0, 30 - Math.floor((performance.now()-herdStart)/1000));
        roundRect(24,68,430,84,8,'rgba(24,13,3,.82)',theme.border);
        drawText('Guardar o Rebanho', 44, 96, 19, theme.primary);
        drawText('Empurre as ovelhas para o curral. Tempo: ' + left + 's', 44, 124, 15, theme.text);
        drawText('Dica: toque nelas pelo lado oposto ao curral.', 44, 144, 13, 'rgba(245,230,200,.82)');
      }

      function drawStones(){
        drawAreaBase();
        rect(75,105,810,320,'#4e9dad');
        rect(75,150,810,38,'rgba(255,255,255,.09)');
        for (const s of stones) {
          ctx.beginPath(); ctx.ellipse(s.x,s.y,s.r+6,s.r,s.smooth ? 0 : .6,0,Math.PI*2);
          ctx.fillStyle = s.hit ? theme.primary : (s.smooth ? '#d7d2c2' : '#6e6258');
          ctx.fill();
          ctx.strokeStyle = s.smooth ? '#ece6d4' : '#332c28'; ctx.stroke();
        }
        const picked = stones.filter(s => s.smooth && s.hit).length;
        const left = Math.max(0, 30 - Math.floor((performance.now()-stonesStart)/1000));
        roundRect(44,445,872,80,10,'rgba(24,13,3,.9)',theme.border);
        drawText('Escolher as Pedras', 70, 475, 20, theme.primary);
        drawText('Clique nas 5 pedras lisas do riacho. Selecionadas: ' + picked + '/5 | Tempo: ' + left + 's', 70, 504, 16, theme.text);
        if (left <= 0) startStones();
      }

      function drawAim(){
        drawWorld();
        ctx.beginPath(); ctx.arc(aim.x, aim.y, aim.r, 0, Math.PI*2);
        ctx.fillStyle = 'rgba(201,168,76,.26)'; ctx.fill();
        ctx.strokeStyle = theme.primary; ctx.lineWidth = 3; ctx.stroke();
        ctx.beginPath(); ctx.moveTo(aim.x-48,aim.y); ctx.lineTo(aim.x+48,aim.y); ctx.moveTo(aim.x,aim.y-48); ctx.lineTo(aim.x,aim.y+48); ctx.stroke();
        roundRect(45,450,870,66,10,'rgba(24,13,3,.9)',theme.border);
        drawText('A Mira', 70, 478, 20, theme.primary);
        drawText('Clique no alvo sobre Golias. Tentativas: ' + aim.tries, 70, 506, 16, theme.text);
      }

      function drawFinal(){
        drawAreaBase();
        roundRect(95,96,770,350,14,'rgba(24,13,3,.92)',theme.border);
        drawText('Davi', W/2, 150, 42, theme.primary, 'center');
        wrapText('Davi correu ao combate, lançou a pedra com a funda e atingiu Golias na testa. O filisteu caiu com o rosto em terra, e Israel viu que o Senhor livra não por espada nem por lança. Quadrinhos desbloqueados no painel abaixo.', 150, 205, 660, 32, 21, theme.text);
        drawText('RPG concluído', W/2, 382, 24, theme.primary, 'center');
      }

      function draw(){
        ctx.clearRect(0,0,W,H);
        ctx.save();
        if (mode === 'intro') drawIntro();
        else if (mode === 'stones') drawStones();
        else if (mode === 'aim') drawAim();
        else if (mode === 'cinematic') drawWorld();
        else if (mode === 'final') drawFinal();
        else {
          drawWorld();
          if (mode === 'herd') drawHerdHud();
          if (mode === 'dialog') drawDialog();
          if (hint) {
            roundRect(300,72,360,38,8,'rgba(24,13,3,.86)',theme.border);
            drawText(hint, 480, 97, 15, theme.primary, 'center');
          }
        }
        if (toastTimer > 0 && toast) {
          roundRect(245,500,470,38,8,'rgba(24,13,3,.9)',theme.border);
          drawText(toast, 480, 525, 15, theme.primary, 'center');
        }
        if (flash > 0) {
          ctx.fillStyle = 'rgba(255,255,255,.16)';
          ctx.fillRect(0,0,W,H);
        }
        ctx.restore();
      }

      function loop(now){
        const dt = Math.min(40, now - last);
        last = now;
        update(dt);
        draw();
        requestAnimationFrame(loop);
      }

      window.addEventListener('keydown', e => {
        const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
        if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','Spacebar','w','a','s','d','e'].includes(k) || e.key === ' ') e.preventDefault();
        keys[k] = true;
        if (k === 'e' || e.key === ' ' || k === 'Spacebar') interact();
      });
      window.addEventListener('keyup', e => { const k = e.key.length === 1 ? e.key.toLowerCase() : e.key; keys[k] = false; });
      canvas.addEventListener('click', canvasClick);
      requestAnimationFrame(loop);
    })();
    </script>
    """
    html_code = (
        html_code.replace("__PRIMARIA__", primaria)
        .replace("__TEXTO__", texto)
        .replace("__BORDA__", borda)
        .replace("__FUNDO__", fundo)
        .replace("__FONTE__", fonte)
    )
    st.components.v1.html(html_code, height=630, scrolling=False)
    st.caption("Conclua o RPG no Canvas primeiro. Ao ver a tela 'RPG concluido', libere o desfecho abaixo.")
    if st.button("Liberar desfecho apos concluir o RPG", use_container_width=True):
        st.session_state.rpg_finalizado = True
        st.session_state.desafio_concluido = True
        st.session_state.tela = "desafio_final"
        st.rerun()


def tela_inicial():
    historias_render = historias_data
    historia_destaque = next((h for h in historias_render if not historia_bloqueada(h)), historias_render[0] if historias_render else {})
    hero_src = local_image_src(historia_destaque.get("imagem_capa")) or local_image_src("assets/static/capa.jpg") or local_image_src("static/capa.jpg")
    hero_style = f"background-image:url('{hero_src}');" if hero_src else "background:linear-gradient(135deg,#15181c,#382915);"
    categoria = historia_destaque.get("categoria", "Narrativa")

    st.markdown(
        f"""
        <div class="streaming-topbar">
            <div class="brand-lockup"><span class="brand-mark">PB</span><span>Projeto Biblico</span></div>
            <div class="topbar-meta">Historias interativas da Biblia</div>
        </div>
        <section class="hero-banner" style="{hero_style}">
            <div class="hero-content">
                <div class="hero-kicker">Historia em destaque</div>
                <h1 class="hero-title">{escape(historia_destaque.get("titulo", "Projeto Biblico"))}</h1>
                <p class="hero-copy">{escape(historia_destaque.get("narrativa", "Escolha uma historia e entre em uma experiencia narrativa com desafios."))}</p>
                <div class="hero-tags">
                    <span class="hero-tag">{escape(categoria)}</span>
                    <span class="hero-tag">{len(historia_destaque.get("cenas", []))} cenas</span>
                    <span class="hero-tag">Mini-jogos</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if historia_destaque and not historia_bloqueada(historia_destaque):
        destaque_idx = historias_data.index(historia_destaque)
        if st.button("Jogar agora", key="hero_play", use_container_width=False):
            resetar_jogo_para_historia(destaque_idx)
            st.rerun()

    st.markdown('<div class="shelf-title">Catalogo de historias</div>', unsafe_allow_html=True)

    if not historias_render:
        st.info("Nenhuma historia cadastrada ainda.")
        return

    for row_start in range(0, len(historias_render), 4):
        cols = st.columns(4)
        for col, historia in zip(cols, historias_render[row_start : row_start + 4]):
            indice = historias_data.index(historia)
            bloqueada = historia_bloqueada(historia)
            with col:
                with st.container(border=True):
                    imagem_capa = historia.get("imagem_capa", "")
                    if imagem_capa and os.path.exists(imagem_capa):
                        st.image(Image.open(imagem_capa), use_container_width=True)
                    else:
                        st.markdown('<div class="locked-poster">LOCK</div>', unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div class="story-card-title">{escape(historia.get("titulo", "Em breve"))}</div>
                        <div class="story-card-meta">{escape(historia.get("categoria", "Bloqueada"))}</div>
                        <div class="story-card-copy">{escape(historia.get("narrativa", "Historia ainda em desenvolvimento."))}</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if bloqueada:
                        st.button("Bloqueada", key=f"locked_{indice}", disabled=True, use_container_width=True)
                    elif st.button("Jogar", key=f"historia_{indice}", use_container_width=True):
                        resetar_jogo_para_historia(indice)
                        st.rerun()


if st.session_state.tela == "inicio":
    tela_inicial()

elif st.session_state.tela == "rpg":
    historia = historias_data[st.session_state.historia_idx]
    tema_atual = aplicar_tema(historia)
    st.markdown('<div class="story-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="story-title">RPG de {escape(historia["titulo"])}</div>', unsafe_allow_html=True)
    tela_rpg_davi(historia, tema_atual)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.tela == "cena":
    historia = historias_data[st.session_state.historia_idx]
    tema_atual = aplicar_tema(historia)
    st.markdown('<div class="story-shell">', unsafe_allow_html=True)
    cenas = historia["cenas"]
    idx = st.session_state.cena_idx

    if idx >= len(cenas):
        st.session_state.tela = "desafio_final"
        st.session_state.minijogo_dados = None
        st.session_state.ordenacao_itens = []
        st.rerun()

    cena = cenas[idx]
    fase = st.session_state.fase

    st.markdown(
        f'<div class="story-nav">{escape(historia["titulo"])} | Cena {idx + 1} de {len(cenas)}</div>',
        unsafe_allow_html=True,
    )

    if fase == "texto":
        tela_digitada(cena["titulo"], cena["texto"], cena["referencia"], tema_atual)
        st.divider()
        if st.button("Iniciar mini-jogo", use_container_width=True):
            with st.spinner("Carregando mini-jogo..."):
                st.session_state.minijogo_dados = preparar_minijogo(cena)
            st.session_state.fase = "minijogo"
            st.rerun()

    elif fase == "minijogo":
        tipo = cena["minijogo"]["tipo"]
        st.markdown(f'<div class="story-title">Mini-jogo | {escape(cena["titulo"])}</div>', unsafe_allow_html=True)
        st.divider()
        dados = st.session_state.minijogo_dados
        if tipo == "mira":
            minijogo_mira(tema_atual)
        else:
            st.info("Este evento agora deve ser implementado no RPG Canvas da historia.")

    elif fase == "proxima":
        st.markdown(f'<div class="story-title">{escape(cena["titulo"])}</div>', unsafe_allow_html=True)
        st.divider()
        mostrar_imagem(cena.get("imagem", ""))
        st.divider()
        if st.button("Proxima cena ->", use_container_width=True):
            st.session_state.cena_idx += 1
            st.session_state.fase = "texto"
            st.session_state.minijogo_dados = None
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.tela == "desafio_final":
    historia = historias_data[st.session_state.historia_idx]
    tema_atual = aplicar_tema(historia)
    st.markdown('<div class="story-shell">', unsafe_allow_html=True)
    desafio = historia["desafio_final"]

    st.markdown(f'<div class="story-title">{escape(desafio["titulo"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-ref">{escape(desafio["descricao"])}</div>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state.desafio_concluido:
        if st.session_state.minijogo_dados is None:
            if desafio.get("eventos"):
                st.session_state.minijogo_dados = {"eventos": desafio["eventos"]}
                st.session_state.ordenacao_itens = []
            else:
                with st.spinner("A IA esta preparando o desafio final..."):
                    dados = ia.gerar_desafio_ordenacao(historia["titulo"])
                    st.session_state.minijogo_dados = dados
                    st.session_state.ordenacao_itens = []
            st.rerun()
        else:
            minijogo_ordenacao(st.session_state.minijogo_dados, tema_atual)
    else:
        if st.session_state.final_epico is None:
            with st.spinner("Gerando narrativa final..."):
                st.session_state.final_epico = ia.gerar_final_epico(
                    historia["titulo"],
                    historia.get("desafio_final", {}),
                    historia.get("cenas", []),
                )

        st.markdown('<div class="story-title">Narrativa Final</div>', unsafe_allow_html=True)
        tela_digitada_simples(st.session_state.final_epico, tema_atual)
        st.divider()

        st.markdown('<div class="story-label">Video cinematico</div>', unsafe_allow_html=True)
        video_path = desafio.get("video", "")
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.info("Video cinematico em breve.")

        st.divider()
        st.markdown('<div class="story-label">Historia em quadrinhos</div>', unsafe_allow_html=True)

        quadrinhos = [p for p in desafio.get("quadrinhos", []) if p and os.path.exists(p)]
        if not quadrinhos:
            quadrinhos = [c.get("imagem", "") for c in historia.get("cenas", []) if c.get("imagem", "")]

        if quadrinhos:
            cols = st.columns(2)
            for i, img_path in enumerate(quadrinhos):
                with cols[i % 2]:
                    if os.path.exists(img_path):
                        st.image(Image.open(img_path), use_container_width=True)
        else:
            st.info("Imagens em breve.")

        st.divider()
        if st.button("<- Voltar ao inicio", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
