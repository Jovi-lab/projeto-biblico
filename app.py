import base64
import html
import json
import mimetypes
import os
import random
import unicodedata

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
        "forca_tentativas": [],
        "forca_erros": 0,
        "vf_idx": 0,
        "vf_acertos": 0,
        "vf_respondidas": {},
        "ordenacao_itens": [],
        "ordenacao_concluida": False,
        "desafio_concluido": False,
        "final_epico": None,
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


def normalizar_texto(texto):
    normalizado = unicodedata.normalize("NFD", str(texto or ""))
    sem_acentos = "".join(c for c in normalizado if unicodedata.category(c) != "Mn")
    return sem_acentos.upper()


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
    st.session_state.historia_idx = indice
    st.session_state.cena_idx = 0
    st.session_state.fase = "texto"
    st.session_state.minijogo_dados = None
    st.session_state.forca_tentativas = []
    st.session_state.forca_erros = 0
    st.session_state.vf_idx = 0
    st.session_state.vf_acertos = 0
    st.session_state.vf_respondidas = {}
    st.session_state.ordenacao_itens = []
    st.session_state.ordenacao_concluida = False
    st.session_state.desafio_concluido = False
    st.session_state.final_epico = None
    st.session_state.tela = "cena"


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


def minijogo_forca(dados, tema=None):
    palavra = str(dados.get("palavra_oculta", "")).upper()
    palavra_normalizada = normalizar_texto(palavra)
    if not palavra:
        st.error("Erro ao carregar o mini-jogo.")
        if st.button("Recarregar"):
            st.session_state.minijogo_dados = None
            st.session_state.fase = "minijogo"
            st.rerun()
        return

    tentativas = st.session_state.forca_tentativas
    erros = st.session_state.forca_erros
    max_erros = 6

    st.markdown(
        f"""
    <div class="story-box">
        <span class="story-label">Versiculo</span><br>
        <span class="story-question">_{escape(dados.get("versiculo_com_lacuna", ""))}_</span>
    </div>
    <div class="story-ref">Ref: {escape(dados.get("referencia", ""))}</div>
    <div class="story-ref">Dica: {escape(dados.get("dica", ""))}</div>
    """,
        unsafe_allow_html=True,
    )
    st.divider()

    display = ""
    acertou_tudo = True
    for letra in palavra:
        letra_normalizada = normalizar_texto(letra)
        if not letra_normalizada.isalpha():
            display += f"{escape(letra)} "
        elif letra_normalizada in tentativas:
            display += f"{escape(letra)} "
        else:
            display += "_ "
            acertou_tudo = False

    st.markdown(
        f"""
    <div class="story-text" style="font-size:28px;text-align:center;letter-spacing:10px;">
        {display}
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="story-ref">Erros: {erros}/{max_erros}</div>', unsafe_allow_html=True)

    letras_erradas = [l for l in tentativas if l not in palavra_normalizada]
    if letras_erradas:
        st.markdown(
            f'<div class="story-ref">Letras erradas: {" ".join(letras_erradas)}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    if acertou_tudo:
        st.success("Versiculo completado!")
        if st.button("Continuar ->", use_container_width=True):
            st.session_state.fase = "proxima"
            st.rerun()
        return

    if erros >= max_erros:
        st.error(f"Fim de jogo! A palavra era: {palavra}")
        st.info(f"Versiculo: {dados.get('versiculo_completo', '')}")
        if st.button("Tentar novamente", use_container_width=True):
            st.session_state.forca_tentativas = []
            st.session_state.forca_erros = 0
            st.rerun()
        return

    cols = st.columns(9)
    for i, letra in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        letra_normalizada = normalizar_texto(letra)
        if letra_normalizada not in tentativas:
            if cols[i % 9].button(letra, key=f"forca_{letra}"):
                st.session_state.forca_tentativas.append(letra_normalizada)
                if letra_normalizada not in palavra_normalizada:
                    st.session_state.forca_erros += 1
                st.rerun()


def minijogo_verdadeiro_falso(dados, tema=None):
    perguntas = dados.get("perguntas", [])
    if not perguntas:
        st.error("Erro ao carregar perguntas.")
        if st.button("Recarregar"):
            st.session_state.minijogo_dados = None
            st.rerun()
        return

    idx = st.session_state.vf_idx
    respondidas = st.session_state.vf_respondidas

    if idx >= len(perguntas):
        acertos = st.session_state.vf_acertos
        st.success(f"{acertos} de {len(perguntas)} corretas!")
        if st.button("Continuar ->", use_container_width=True):
            st.session_state.fase = "proxima"
            st.rerun()
        return

    pergunta = perguntas[idx]
    st.markdown(
        f'<div class="story-label">Pergunta {idx + 1} de {len(perguntas)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="story-box"><span class="story-question">{escape(pergunta["pergunta"])}</span></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    if idx in respondidas:
        if respondidas[idx] == pergunta["resposta"]:
            st.success("Correto!")
        else:
            st.error("Errado!")
        st.markdown(f'<div class="story-ref">{escape(pergunta["explicacao"])}</div>', unsafe_allow_html=True)
        if st.button("Proxima ->", use_container_width=True):
            st.session_state.vf_idx += 1
            st.rerun()
    else:
        col1, col2 = st.columns(2)
        if col1.button("Verdadeiro", use_container_width=True):
            st.session_state.vf_respondidas[idx] = True
            if pergunta["resposta"] is True:
                st.session_state.vf_acertos += 1
            st.rerun()
        if col2.button("Falso", use_container_width=True):
            st.session_state.vf_respondidas[idx] = False
            if pergunta["resposta"] is False:
                st.session_state.vf_acertos += 1
            st.rerun()


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

    if tipo == "forca":
        st.session_state.forca_tentativas = []
        st.session_state.forca_erros = 0
        if all(minijogo.get(campo) for campo in ["versiculo_completo", "referencia", "palavra_oculta", "versiculo_com_lacuna"]):
            return minijogo
        return ia.gerar_jogo_forca(cena.get("titulo", ""), cena.get("referencia", ""), cena.get("texto", ""), minijogo)

    if tipo == "verdadeiro_falso":
        st.session_state.vf_idx = 0
        st.session_state.vf_acertos = 0
        st.session_state.vf_respondidas = {}
        if minijogo.get("perguntas"):
            return minijogo
        return ia.gerar_verdadeiro_falso(cena.get("titulo", ""), cena.get("referencia", ""), cena.get("texto", ""), minijogo)

    if tipo == "mira":
        return minijogo

    return minijogo


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
        if tipo == "forca":
            minijogo_forca(dados, tema_atual)
        elif tipo == "verdadeiro_falso":
            minijogo_verdadeiro_falso(dados, tema_atual)
        elif tipo == "mira":
            minijogo_mira(tema_atual)

    elif fase == "proxima":
        st.markdown(f'<div class="story-title">{escape(cena["titulo"])}</div>', unsafe_allow_html=True)
        st.divider()
        mostrar_imagem(cena.get("imagem", ""))
        st.divider()
        if st.button("Proxima cena ->", use_container_width=True):
            st.session_state.cena_idx += 1
            st.session_state.fase = "texto"
            st.session_state.minijogo_dados = None
            st.session_state.forca_tentativas = []
            st.session_state.forca_erros = 0
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
