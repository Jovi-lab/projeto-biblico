import streamlit as st
import os
import json
import random
import time
from PIL import Image
from dotenv import load_dotenv
from src.carregador import Carregador
from src.ia_helper import IAHelper

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ia = IAHelper(GROQ_API_KEY)

st.set_page_config(
    page_title="Projeto Bíblico",
    page_icon="✝",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
* { box-sizing: border-box; }
.stApp { background: #000 !important; }
.hacker-text {
    font-family: 'Share Tech Mono', monospace;
    color: #00FF41;
    font-size: 17px;
    line-height: 1.9;
    background: #000;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #00FF41;
    white-space: pre-wrap;
    word-break: break-word;
}
.hacker-title {
    font-family: 'Share Tech Mono', monospace;
    color: #00FF41;
    font-size: 26px;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 0 0 10px #00FF41;
}
.hacker-ref {
    font-family: 'Share Tech Mono', monospace;
    color: #00AA20;
    font-size: 13px;
    margin-top: 0.5rem;
}
.hacker-box {
    background: #000;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #00FF41;
    margin-bottom: 1rem;
}
.hacker-pergunta {
    font-family: 'Share Tech Mono', monospace;
    color: #00FF41;
    font-size: 18px;
    line-height: 1.7;
}
.hacker-label {
    font-family: 'Share Tech Mono', monospace;
    color: #00AA20;
    font-size: 14px;
    margin-bottom: 0.5rem;
}
.hacker-nav {
    font-family: 'Share Tech Mono', monospace;
    color: #00AA20;
    font-size: 13px;
    background: #000;
    border: 1px solid #00AA20;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

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

def mostrar_imagem(caminho):
    if caminho and os.path.exists(caminho):
        st.image(Image.open(caminho), use_container_width=True)
        return True
    return False

def tela_digitada(titulo, texto, referencia=""):
    html = f"""
    <div style="background:#000;min-height:100vh;padding:2rem 1rem;">
        <div id="titulo" style="font-family:'Share Tech Mono',monospace;color:#00FF41;font-size:26px;
            text-align:center;margin-bottom:2rem;text-shadow:0 0 10px #00FF41;min-height:40px;"></div>
        <div id="texto" style="font-family:'Share Tech Mono',monospace;color:#00FF41;font-size:17px;
            line-height:1.9;background:#000;padding:1.5rem;border-radius:8px;
            border:1px solid #00FF41;min-height:100px;white-space:pre-wrap;word-break:break-word;"></div>
        <div id="ref" style="font-family:'Share Tech Mono',monospace;color:#00AA20;
            font-size:13px;margin-top:0.75rem;min-height:20px;"></div>
        <div id="cursor" style="display:inline-block;width:10px;height:18px;
            background:#00FF41;margin-left:4px;animation:blink 0.7s infinite;">█</div>
    </div>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0}} }}
    </style>
    <script>
    (function(){{
        const titulo = {json.dumps(titulo)};
        const texto = {json.dumps(texto)};
        const ref = {json.dumps(referencia)};
        const elTitulo = document.getElementById('titulo');
        const elTexto = document.getElementById('texto');
        const elRef = document.getElementById('ref');

        async function digitar(el, str, delay){{
            for(let c of str){{
                el.textContent += c;
                await new Promise(r => setTimeout(r, delay));
            }}
        }}

        async function run(){{
            await digitar(elTitulo, '> ' + titulo, 60);
            await new Promise(r => setTimeout(r, 400));
            await digitar(elTexto, texto, 18);
            await new Promise(r => setTimeout(r, 300));
            if(ref) await digitar(elRef, '> Referência: ' + ref, 30);
            document.getElementById('cursor').style.display = 'none';
        }}
        run();
    }})();
    </script>
    """
    altura = 200 + len(texto) // 2
    st.components.v1.html(html, height=min(altura, 900), scrolling=True)

def minijogo_forca(dados):
    palavra = dados.get("palavra_oculta", "").upper()
    if not palavra:
        st.error("Erro ao carregar o mini-jogo. Tente novamente.")
        if st.button("Recarregar"):
            st.session_state.minijogo_dados = None
            st.session_state.fase = "minijogo"
            st.rerun()
        return

    tentativas = st.session_state.forca_tentativas
    erros = st.session_state.forca_erros
    max_erros = 6

    versiculo = dados.get("versiculo_com_lacuna", "")
    referencia = dados.get("referencia", "")
    dica = dados.get("dica", "")
    versiculo_completo = dados.get("versiculo_completo", "")

    st.markdown(f"""
    <div class="hacker-box">
        <span class="hacker-label">> VERSÍCULO:</span><br>
        <span class="hacker-pergunta">_{versiculo}_</span>
    </div>
    <div class="hacker-ref">> Ref: {referencia}</div>
    <div class="hacker-ref">> Dica: {dica}</div>
    """, unsafe_allow_html=True)
    st.divider()

    display = ""
    acertou_tudo = True
    for letra in palavra:
        if letra in tentativas:
            display += f"{letra} "
        else:
            display += "_ "
            acertou_tudo = False

    st.markdown(f"""
    <div class="hacker-text" style="font-size:28px;text-align:center;letter-spacing:10px;">
        {display}
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="hacker-ref">> Erros: {erros}/{max_erros}</div>', unsafe_allow_html=True)

    letras_erradas = [l for l in tentativas if l not in palavra]
    if letras_erradas:
        st.markdown(f'<div class="hacker-ref">> Letras erradas: {" ".join(letras_erradas)}</div>', unsafe_allow_html=True)

    st.divider()

    if acertou_tudo:
        st.success("✅ Versículo completado!")
        if st.button("Continuar →", use_container_width=True):
            st.session_state.fase = "proxima"
            st.rerun()
        return

    if erros >= max_erros:
        st.error(f"Fim de jogo! A palavra era: {palavra}")
        st.info(f"Versículo: {versiculo_completo}")
        if st.button("Tentar novamente", use_container_width=True):
            st.session_state.forca_tentativas = []
            st.session_state.forca_erros = 0
            st.rerun()
        return

    cols = st.columns(9)
    for i, letra in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        if letra not in tentativas:
            if cols[i % 9].button(letra, key=f"forca_{letra}"):
                st.session_state.forca_tentativas.append(letra)
                if letra not in palavra:
                    st.session_state.forca_erros += 1
                st.rerun()

def minijogo_verdadeiro_falso(dados):
    perguntas = dados.get("perguntas", [])
    if not perguntas:
        st.error("Erro ao carregar perguntas.")
        if st.button("Recarregar"):
            st.session_state.minijogo_dados = None
            st.session_state.fase = "minijogo"
            st.rerun()
        return

    idx = st.session_state.vf_idx
    respondidas = st.session_state.vf_respondidas

    if idx >= len(perguntas):
        acertos = st.session_state.vf_acertos
        st.success(f"✅ {acertos} de {len(perguntas)} corretas!")
        if st.button("Continuar →", use_container_width=True):
            st.session_state.fase = "proxima"
            st.rerun()
        return

    pergunta = perguntas[idx]
    st.markdown(f'<div class="hacker-label">> PERGUNTA {idx+1} DE {len(perguntas)}:</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hacker-box"><span class="hacker-pergunta">{pergunta["pergunta"]}</span></div>', unsafe_allow_html=True)
    st.divider()

    if idx in respondidas:
        correta = pergunta["resposta"]
        if respondidas[idx] == correta:
            st.success("✅ Correto!")
        else:
            st.error("❌ Errado!")
        st.markdown(f'<div class="hacker-ref">> {pergunta["explicacao"]}</div>', unsafe_allow_html=True)
        if st.button("Próxima →", use_container_width=True):
            st.session_state.vf_idx += 1
            st.rerun()
    else:
        col1, col2 = st.columns(2)
        if col1.button("✅ Verdadeiro", use_container_width=True):
            st.session_state.vf_respondidas[idx] = True
            if pergunta["resposta"] == True:
                st.session_state.vf_acertos += 1
            st.rerun()
        if col2.button("❌ Falso", use_container_width=True):
            st.session_state.vf_respondidas[idx] = False
            if pergunta["resposta"] == False:
                st.session_state.vf_acertos += 1
            st.rerun()

def minijogo_mira():
    mira_html = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    body { background: #000; margin: 0; padding: 0; }
    #miraContainer {
        position: relative;
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid #00FF41;
        background: #0a0a0a;
    }
    #bgImg {
        width: 100%;
        display: block;
        min-height: 320px;
        object-fit: cover;
        filter: brightness(0.6) sepia(0.3);
    }
    #miraCanvas {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        cursor: crosshair;
    }
    #miraInfo {
        background: #000;
        border-top: 1px solid #00FF41;
        padding: 10px 16px;
        font-family: 'Share Tech Mono', monospace;
        color: #00FF41;
        font-size: 14px;
        min-height: 80px;
    }
    #miraResult { font-size: 16px; margin-bottom: 6px; min-height: 24px; }
    #miraTent { color: #00AA20; font-size: 13px; }
    #miraAcertou {
        display: none;
        background: #000;
        border: 1px solid #00FF41;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-family: 'Share Tech Mono', monospace;
        color: #00FF41;
        font-size: 16px;
        margin-top: 10px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>

    <div id="miraContainer">
        <img id="bgImg" src="app/static/capa_mira.png"
             onerror="this.src='';this.style.minHeight='320px';this.style.background='#1a0800';">
        <canvas id="miraCanvas"></canvas>
    </div>
    <div id="miraInfo">
        <div id="miraResult">> Mire na cabeça do gigante e clique!</div>
        <div id="miraTent">> Tentativas restantes: 3</div>
    </div>
    <div id="miraAcertou">✅ ACERTOU! A pedra atingiu Golias!<br>
        <small style="color:#00AA20;">Role a página para continuar</small>
    </div>

    <script>
    (function(){
        const canvas = document.getElementById('miraCanvas');
        const ctx = canvas.getContext('2d');
        const res = document.getElementById('miraResult');
        const tent = document.getElementById('miraTent');
        const acertouDiv = document.getElementById('miraAcertou');
        const bg = document.getElementById('bgImg');

        function syncCanvas(){
            canvas.width = bg.offsetWidth || 400;
            canvas.height = bg.offsetHeight || 320;
        }

        bg.onload = syncCanvas;
        setTimeout(syncCanvas, 500);

        let x, y, dx = 2.5, dy = 1.8;
        let raio = 30, tentativas = 3, jogando = true;

        function resetPos(){
            x = (canvas.width || 400) * 0.5;
            y = (canvas.height || 320) * 0.2;
        }
        resetPos();

        function desenhar(){
            if(!canvas.width) return;
            ctx.clearRect(0,0,canvas.width,canvas.height);
            const grad = ctx.createRadialGradient(x,y,2,x,y,raio);
            grad.addColorStop(0,'rgba(0,255,65,0.95)');
            grad.addColorStop(0.35,'rgba(0,200,50,0.6)');
            grad.addColorStop(1,'rgba(0,255,65,0)');
            ctx.beginPath();
            ctx.arc(x,y,raio,0,Math.PI*2);
            ctx.fillStyle=grad;
            ctx.fill();
            ctx.strokeStyle='#00FF41';
            ctx.lineWidth=2;
            ctx.stroke();
            [raio*0.5, raio*0.75].forEach(r=>{
                ctx.beginPath();
                ctx.arc(x,y,r,0,Math.PI*2);
                ctx.strokeStyle='rgba(0,255,65,0.5)';
                ctx.lineWidth=1;
                ctx.stroke();
            });
            ctx.strokeStyle='rgba(0,255,65,0.7)';
            ctx.lineWidth=1;
            ctx.beginPath();ctx.moveTo(x-raio-18,y);ctx.lineTo(x+raio+18,y);ctx.stroke();
            ctx.beginPath();ctx.moveTo(x,y-raio-18);ctx.lineTo(x,y+raio+18);ctx.stroke();
            tent.textContent = '> Tentativas restantes: ' + tentativas;
        }

        function animar(){
            if(!jogando) return;
            if(!canvas.width){ setTimeout(animar,100); return; }
            x+=dx; y+=dy;
            if(x+raio>canvas.width||x-raio<0) dx=-dx;
            if(y+raio>canvas.height||y-raio<0) dy=-dy;
            dx+=(Math.random()-0.5)*0.15;
            dy+=(Math.random()-0.5)*0.15;
            dx=Math.max(-4.5,Math.min(4.5,dx));
            dy=Math.max(-3.5,Math.min(3.5,dy));
            desenhar();
            requestAnimationFrame(animar);
        }

        canvas.addEventListener('click',function(e){
            if(!jogando) return;
            const rect=canvas.getBoundingClientRect();
            const scaleX=canvas.width/rect.width;
            const scaleY=canvas.height/rect.height;
            const cx=(e.clientX-rect.left)*scaleX;
            const cy=(e.clientY-rect.top)*scaleY;
            const dist=Math.sqrt((cx-x)**2+(cy-y)**2);
            if(dist<=raio){
                jogando=false;
                res.style.color='#00FF41';
                res.textContent='> ⚡ ACERTOU! A pedra atingiu Golias!';
                acertouDiv.style.display='block';
            } else {
                tentativas--;
                if(tentativas<=0){
                    jogando=false;
                    res.style.color='#FF4444';
                    res.textContent='> Suas tentativas acabaram!';
                } else {
                    res.style.color='#FAC775';
                    res.textContent='> Errou! Continue mirando...';
                }
            }
        });
        setTimeout(()=>{ syncCanvas(); resetPos(); animar(); }, 300);
    })();
    </script>
    """
    st.components.v1.html(mira_html, height=480)
    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("✅ Acertei!", use_container_width=True):
        st.session_state.fase = "proxima"
        st.rerun()
    if col2.button("🔄 Tentar novamente", use_container_width=True):
        st.rerun()

def minijogo_ordenacao(dados):
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

    st.markdown('<div class="hacker-label">> COLOQUE OS EVENTOS NA ORDEM CORRETA:</div>', unsafe_allow_html=True)
    st.markdown('<div class="hacker-ref">> Use ↑ ↓ para reordenar</div>', unsafe_allow_html=True)
    st.divider()

    itens = st.session_state.ordenacao_itens
    for i, evento in enumerate(itens):
        col1, col2, col3 = st.columns([7, 1, 1])
        col1.markdown(f'<div class="hacker-ref" style="font-size:15px;">{i+1}. {evento}</div>', unsafe_allow_html=True)
        if i > 0:
            if col2.button("↑", key=f"up_{i}"):
                itens[i], itens[i-1] = itens[i-1], itens[i]
                st.rerun()
        if i < len(itens)-1:
            if col3.button("↓", key=f"down_{i}"):
                itens[i], itens[i+1] = itens[i+1], itens[i]
                st.rerun()

    st.divider()
    if st.button("✅ Verificar ordem", use_container_width=True):
        if itens == eventos_corretos:
            st.session_state.ordenacao_concluida = True
            st.rerun()
        else:
            st.error("A ordem não está correta. Tente novamente!")

    if st.session_state.ordenacao_concluida:
        st.success("✅ Ordem correta!")
        if st.button("Ver o final →", use_container_width=True):
            st.session_state.desafio_concluido = True
            st.rerun()

# ── TELA INICIAL ──────────────────────────────────────────────────────────────
if st.session_state.tela == "inicio":
    capa_path = "assets/static/capa.jpg"
    if os.path.exists(capa_path):
        st.markdown(f"""
        <div style="position:relative;width:100%;border-radius:12px;
            overflow:hidden;margin-bottom:1.5rem;">
            <img src="app/static/capa.jpg"
                style="width:100%;display:block;filter:brightness(0.45);">
            <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                align-items:center;justify-content:center;padding:2rem;">
                <p style="font-family:'Share Tech Mono',monospace;color:#00FF41;
                    font-size:36px;text-align:center;
                    text-shadow:0 0 20px #00FF41;margin:0;">✝ Projeto Bíblico</p>
                <p style="font-family:'Share Tech Mono',monospace;
                    color:rgba(0,255,65,0.7);font-size:14px;
                    text-align:center;margin-top:8px;">
                    Explore histórias sagradas de um jeito diferente</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        img = Image.open("assets/static/capa.jpg") if os.path.exists("assets/static/capa.jpg") else None
        if img:
            st.image(img, use_container_width=True)
        st.title("✝ Projeto Bíblico")

    st.markdown('<div class="hacker-label">> ESCOLHA UMA HISTÓRIA:</div>', unsafe_allow_html=True)
    st.divider()

    for i, h in enumerate(historias_data):
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                imagem_capa = h.get("imagem_capa", "")
                if not (imagem_capa and os.path.exists(imagem_capa) and st.image(Image.open(imagem_capa), use_container_width=True) is None):
                    st.markdown('<p style="font-size:40px;text-align:center;color:#00FF41;">✝</p>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<p style="font-family:Share Tech Mono,monospace;color:#00FF41;font-size:20px;margin:0;">{h["titulo"]}</p>', unsafe_allow_html=True)
                st.caption(h["categoria"])
                st.write(h["narrativa"])
                if st.button("▶ Jogar", key=f"historia_{i}"):
                    st.session_state.historia_idx = i
                    st.session_state.cena_idx = 0
                    st.session_state.fase = "texto"
                    st.session_state.minijogo_dados = None
                    st.session_state.tela = "cena"
                    st.rerun()

# ── TELA DE CENA ──────────────────────────────────────────────────────────────
elif st.session_state.tela == "cena":
    historia = historias_data[st.session_state.historia_idx]
    cenas = historia["cenas"]
    idx = st.session_state.cena_idx

    if idx >= len(cenas):
        st.session_state.tela = "desafio_final"
        st.session_state.minijogo_dados = None
        st.session_state.ordenacao_itens = []
        st.rerun()

    cena = cenas[idx]
    fase = st.session_state.fase

    # Navegação
    st.markdown(f'<div class="hacker-nav">> {historia["titulo"]} — Cena {idx+1} de {len(cenas)}</div>', unsafe_allow_html=True)

    # FASE: texto
    if fase == "texto":
        tela_digitada(cena["titulo"], cena["texto"], cena["referencia"])
        st.divider()
        if st.button("▶ Iniciar mini-jogo", use_container_width=True):
            with st.spinner("Carregando mini-jogo..."):
                tipo = cena["minijogo"]["tipo"]
                if tipo == "forca":
                    dados = ia.gerar_jogo_forca(cena["titulo"])
                    st.session_state.forca_tentativas = []
                    st.session_state.forca_erros = 0
                elif tipo == "verdadeiro_falso":
                    dados = ia.gerar_verdadeiro_falso(cena["titulo"], cena["referencia"])
                    st.session_state.vf_idx = 0
                    st.session_state.vf_acertos = 0
                    st.session_state.vf_respondidas = {}
                elif tipo == "mira":
                    dados = cena["minijogo"]
                st.session_state.minijogo_dados = dados
            st.session_state.fase = "minijogo"
            st.rerun()

    # FASE: minijogo
    elif fase == "minijogo":
        tipo = cena["minijogo"]["tipo"]
        st.markdown(f'<div class="hacker-title">> Mini-jogo — {cena["titulo"]}</div>', unsafe_allow_html=True)
        st.divider()
        dados = st.session_state.minijogo_dados
        if tipo == "forca":
            minijogo_forca(dados)
        elif tipo == "verdadeiro_falso":
            minijogo_verdadeiro_falso(dados)
        elif tipo == "mira":
            minijogo_mira()

    # FASE: imagem pós-minijogo
    elif fase == "proxima":
        st.markdown(f'<div class="hacker-title">> {cena["titulo"]}</div>', unsafe_allow_html=True)
        st.divider()
        mostrar_imagem(cena.get("imagem", ""))
        st.divider()
        if st.button("Próxima cena →", use_container_width=True):
            st.session_state.cena_idx += 1
            st.session_state.fase = "texto"
            st.session_state.minijogo_dados = None
            st.session_state.forca_tentativas = []
            st.session_state.forca_erros = 0
            st.rerun()

# ── DESAFIO FINAL ─────────────────────────────────────────────────────────────
elif st.session_state.tela == "desafio_final":
    historia = historias_data[st.session_state.historia_idx]
    desafio = historia["desafio_final"]

    st.markdown(f'<div class="hacker-title">> {desafio["titulo"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hacker-ref">> {desafio["descricao"]}</div>', unsafe_allow_html=True)
    st.divider()

    if not st.session_state.desafio_concluido:
        if st.session_state.minijogo_dados is None:
            with st.spinner("A IA está preparando o desafio final..."):
                dados = ia.gerar_desafio_ordenacao(historia["titulo"])
                st.session_state.minijogo_dados = dados
                st.session_state.ordenacao_itens = []
            st.rerun()
        else:
            minijogo_ordenacao(st.session_state.minijogo_dados)
    else:
        if st.session_state.final_epico is None:
            with st.spinner("Gerando narrativa final..."):
                st.session_state.final_epico = ia.gerar_final_epico(historia["titulo"])

        st.markdown(f'<div class="hacker-text">{st.session_state.final_epico}</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown('<div class="hacker-label">> VÍDEO CINEMÁTICO:</div>', unsafe_allow_html=True)
        video_path = desafio.get("video", "")
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.info("🎬 Vídeo cinemático em breve.")

        st.divider()
        st.markdown('<div class="hacker-label">> HISTÓRIA EM QUADRINHOS:</div>', unsafe_allow_html=True)
        quadrinhos = desafio.get("quadrinhos", [])
        cols = st.columns(2)
        for i, q in enumerate(quadrinhos):
            with cols[i % 2]:
                if os.path.exists(q):
                    st.image(Image.open(q), use_container_width=True)
                else:
                    st.info(f"Quadrinho {i+1} em breve.")
        st.divider()

        if st.button("← Voltar ao início", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()