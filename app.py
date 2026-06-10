import streamlit as st
import os
import json
import random
from PIL import Image
from dotenv import load_dotenv
from src.usuario import Usuario
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

carregador = Carregador("data/historias.json")
historias_data = carregador.carregar()

def init_state():
    defaults = {
        "tela": "inicio",
        "usuario": None,
        "historia_idx": None,
        "cena_idx": 0,
        "minijogo_ativo": False,
        "minijogo_concluido": False,
        "minijogo_dados": None,
        "forca_tentativas": [],
        "forca_erros": 0,
        "vf_idx": 0,
        "vf_acertos": 0,
        "vf_respondidas": [],
        "ordenacao_itens": [],
        "ordenacao_concluida": False,
        "desafio_concluido": False,
        "final_epico": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def mostrar_imagem(caminho, use_container_width=True):
    if caminho and os.path.exists(caminho):
        st.image(Image.open(caminho), use_container_width=use_container_width)

def minijogo_forca(dados):
    palavra = dados["palavra_oculta"].upper()
    tentativas = st.session_state.forca_tentativas
    erros = st.session_state.forca_erros
    max_erros = 6

    st.markdown(f"**Versículo:** _{dados['versiculo_com_lacuna']}_")
    st.caption(f"Referência: {dados['referencia']}")
    st.caption(f"Dica: {dados['dica']}")
    st.divider()

    display = ""
    acertou_tudo = True
    for letra in palavra:
        if letra in tentativas:
            display += f"**{letra}** "
        else:
            display += "\\_ "
            acertou_tudo = False

    st.markdown(f"### {display}")
    st.caption(f"Erros: {erros}/{max_erros}")

    letras_erradas = [l for l in tentativas if l not in palavra]
    if letras_erradas:
        st.caption(f"Letras erradas: {' '.join(letras_erradas)}")

    if acertou_tudo:
        st.success("Você completou o versículo! 🎉")
        if st.button("Continuar a história →"):
            st.session_state.minijogo_concluido = True
            st.session_state.minijogo_ativo = False
            st.rerun()
        return

    if erros >= max_erros:
        st.error(f"Fim de jogo! A palavra era: **{palavra}**")
        st.info(f"Versículo completo: {dados['versiculo_completo']}")
        if st.button("Tentar novamente"):
            st.session_state.forca_tentativas = []
            st.session_state.forca_erros = 0
            st.rerun()
        return

    cols = st.columns(9)
    alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, letra in enumerate(alfabeto):
        col = cols[i % 9]
        if letra not in tentativas:
            if col.button(letra, key=f"forca_{letra}"):
                st.session_state.forca_tentativas.append(letra)
                if letra not in palavra:
                    st.session_state.forca_erros += 1
                st.rerun()

def minijogo_verdadeiro_falso(dados):
    perguntas = dados["perguntas"]
    idx = st.session_state.vf_idx
    respondidas = st.session_state.vf_respondidas

    if idx >= len(perguntas):
        acertos = st.session_state.vf_acertos
        st.success(f"Você acertou {acertos} de {len(perguntas)} perguntas! 🎉")
        if st.button("Continuar a história →"):
            st.session_state.minijogo_concluido = True
            st.session_state.minijogo_ativo = False
            st.rerun()
        return

    pergunta = perguntas[idx]
    st.markdown(f"**Pergunta {idx + 1} de {len(perguntas)}:**")
    st.markdown(f"### {pergunta['pergunta']}")
    st.divider()

    if idx in respondidas:
        resp = respondidas[idx]
        correta = pergunta["resposta"]
        if resp == correta:
            st.success(f"Correto! ✅")
        else:
            st.error(f"Errado! ❌")
        st.info(pergunta["explicacao"])
        if st.button("Próxima pergunta →"):
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
    st.markdown("**Davi confiou em Deus e lançou a pedra com precisão!**")
    st.caption("Clique no alvo no momento certo para acertar Golias.")

    mira_html = """
    <div style="background:#1a0800;border-radius:12px;padding:1rem;text-align:center;margin-bottom:1rem;">
        <canvas id="miraCanvas" width="400" height="250"
            style="border-radius:8px;cursor:crosshair;max-width:100%;"></canvas>
        <div id="resultado" style="margin-top:12px;font-size:16px;font-weight:500;color:#FAC775;min-height:24px;"></div>
        <div id="tentativas" style="font-size:13px;color:rgba(255,255,255,0.5);margin-top:4px;"></div>
    </div>
    <script>
    (function(){
        const canvas = document.getElementById('miraCanvas');
        const ctx = canvas.getContext('2d');
        const res = document.getElementById('resultado');
        const tent = document.getElementById('tentativas');
        let x = 200, y = 125, dx = 3, dy = 2;
        let raio = 30, tentativas = 3, acertos = 0, jogando = true;

        function desenhar(){
            ctx.fillStyle = '#2a1200';
            ctx.fillRect(0,0,canvas.width,canvas.height);
            ctx.beginPath();
            ctx.arc(x,y,raio,0,Math.PI*2);
            ctx.fillStyle='#8B0000';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(x,y,raio*0.65,0,Math.PI*2);
            ctx.fillStyle='#CC0000';
            ctx.fill();
            ctx.beginPath();
            ctx.arc(x,y,raio*0.35,0,Math.PI*2);
            ctx.fillStyle='#FF4444';
            ctx.fill();
            ctx.strokeStyle='rgba(255,255,255,0.3)';
            ctx.lineWidth=1;
            ctx.beginPath();ctx.moveTo(x-raio-10,y);ctx.lineTo(x+raio+10,y);ctx.stroke();
            ctx.beginPath();ctx.moveTo(x,y-raio-10);ctx.lineTo(x,y+raio+10);ctx.stroke();
            tent.textContent = 'Tentativas restantes: ' + tentativas;
        }

        function animar(){
            if(!jogando) return;
            x += dx; y += dy;
            if(x+raio>canvas.width||x-raio<0) dx=-dx;
            if(y+raio>canvas.height||y-raio<0) dy=-dy;
            dx += (Math.random()-0.5)*0.3;
            dy += (Math.random()-0.5)*0.3;
            dx = Math.max(-5,Math.min(5,dx));
            dy = Math.max(-4,Math.min(4,dy));
            desenhar();
            requestAnimationFrame(animar);
        }

        canvas.addEventListener('click', function(e){
            if(!jogando) return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const cx = (e.clientX-rect.left)*scaleX;
            const cy = (e.clientY-rect.top)*scaleY;
            const dist = Math.sqrt((cx-x)**2+(cy-y)**2);
            tentativas--;
            if(dist<=raio){
                acertos++;
                res.style.color='#90EE90';
                res.textContent = '⚡ Acertou! A pedra atingiu Golias!';
                jogando=false;
                setTimeout(()=>{
                    window.parent.postMessage({type:'mira_acertou'}, '*');
                }, 1500);
            } else {
                if(tentativas<=0){
                    jogando=false;
                    res.style.color='#FF6B6B';
                    res.textContent = 'Suas tentativas acabaram. Tente novamente!';
                    setTimeout(()=>{
                        window.parent.postMessage({type:'mira_errou'}, '*');
                    }, 1500);
                } else {
                    res.style.color='#FAC775';
                    res.textContent = 'Errou! O alvo continua se movendo...';
                }
            }
        });
        animar();
    })();
    </script>
    """
    st.components.v1.html(mira_html, height=320)

    col1, col2 = st.columns(2)
    if col1.button("✅ Acertei o alvo!", use_container_width=True):
        st.session_state.minijogo_concluido = True
        st.session_state.minijogo_ativo = False
        st.rerun()
    if col2.button("🔄 Tentar novamente", use_container_width=True):
        st.rerun()

def minijogo_ordenacao(dados):
    eventos_corretos = dados["eventos"]

    if not st.session_state.ordenacao_itens:
        embaralhado = eventos_corretos.copy()
        random.shuffle(embaralhado)
        st.session_state.ordenacao_itens = embaralhado

    st.markdown("**Coloque os eventos na ordem correta:**")
    st.caption("Use os botões ↑ ↓ para reordenar os eventos.")
    st.divider()

    itens = st.session_state.ordenacao_itens
    for i, evento in enumerate(itens):
        col1, col2, col3 = st.columns([6, 1, 1])
        col1.markdown(f"**{i+1}.** {evento}")
        if i > 0:
            if col2.button("↑", key=f"up_{i}"):
                itens[i], itens[i-1] = itens[i-1], itens[i]
                st.rerun()
        if i < len(itens) - 1:
            if col3.button("↓", key=f"down_{i}"):
                itens[i], itens[i+1] = itens[i+1], itens[i]
                st.rerun()

    st.divider()
    if st.button("Verificar ordem", use_container_width=True):
        if itens == eventos_corretos:
            st.session_state.ordenacao_concluida = True
            st.rerun()
        else:
            st.error("A ordem não está correta. Tente novamente!")

    if st.session_state.ordenacao_concluida:
        st.success("Ordem correta! Você conhece bem a história! 🎉")
        if st.button("Ver o final completo →"):
            st.session_state.desafio_concluido = True
            st.rerun()

# ─── TELAS ────────────────────────────────────────────────────────────────────

if st.session_state.tela == "inicio":
    img = Image.open("assets/static/capa.jpg")
    st.image(img, use_container_width=True)
    st.title("✝ Projeto Bíblico")
    st.markdown("Explore histórias sagradas de um jeito diferente.")
    st.divider()
    st.markdown("**Escolha uma história:**")
    for i, h in enumerate(historias_data):
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                imagem_capa = h.get("imagem_capa", "")
                if imagem_capa and os.path.exists(imagem_capa):
                    st.image(Image.open(imagem_capa), use_container_width=True)
                else:
                    st.markdown("### ✝")
            with col2:
                st.markdown(f"### {h['titulo']}")
                st.caption(h["categoria"])
                st.write(h["narrativa"])
                if st.button("Jogar", key=f"historia_{i}"):
                    st.session_state.historia_idx = i
                    st.session_state.cena_idx = 0
                    st.session_state.tela = "cena"
                    st.session_state.minijogo_ativo = False
                    st.session_state.minijogo_concluido = False
                    st.rerun()

elif st.session_state.tela == "cena":
    historia = historias_data[st.session_state.historia_idx]
    cenas = historia["cenas"]
    idx = st.session_state.cena_idx

    if idx >= len(cenas):
        st.session_state.tela = "desafio_final"
        st.rerun()

    cena = cenas[idx]

    st.title(f"✝ {historia['titulo']}")
    st.divider()

    if not st.session_state.minijogo_ativo and not st.session_state.minijogo_concluido:
        mostrar_imagem(cena.get("imagem", ""))
        st.subheader(cena["titulo"])
        st.write(cena["texto"])
        st.caption(f"Referência: {cena['referencia']}")
        st.divider()
        if st.button("Iniciar mini-jogo →", use_container_width=True):
            with st.spinner("A IA está preparando o mini-jogo..."):
                tipo = cena["minijogo"]["tipo"]
                if tipo == "forca":
                    dados = ia.gerar_jogo_forca(cena["titulo"])
                elif tipo == "verdadeiro_falso":
                    dados = ia.gerar_verdadeiro_falso(cena["titulo"], cena["referencia"])
                    st.session_state.vf_idx = 0
                    st.session_state.vf_acertos = 0
                    st.session_state.vf_respondidas = {}
                elif tipo == "mira":
                    dados = cena["minijogo"]
                st.session_state.minijogo_dados = dados
            st.session_state.minijogo_ativo = True
            st.rerun()

    elif st.session_state.minijogo_ativo:
        tipo = cena["minijogo"]["tipo"]
        st.subheader(f"Mini-jogo — {cena['titulo']}")
        st.divider()
        dados = st.session_state.minijogo_dados
        if tipo == "forca":
            minijogo_forca(dados)
        elif tipo == "verdadeiro_falso":
            minijogo_verdadeiro_falso(dados)
        elif tipo == "mira":
            minijogo_mira()

    elif st.session_state.minijogo_concluido:
        st.success("Mini-jogo concluído! ✅")
        mostrar_imagem(cena.get("imagem", ""))
        st.divider()
        if st.button("Próxima cena →", use_container_width=True):
            st.session_state.cena_idx += 1
            st.session_state.minijogo_ativo = False
            st.session_state.minijogo_concluido = False
            st.session_state.forca_tentativas = []
            st.session_state.forca_erros = 0
            st.rerun()

elif st.session_state.tela == "desafio_final":
    historia = historias_data[st.session_state.historia_idx]
    desafio = historia["desafio_final"]

    st.title(f"✝ {desafio['titulo']}")
    st.caption(desafio["descricao"])
    st.divider()

    if not st.session_state.desafio_concluido:
        if st.session_state.minijogo_dados is None:
            with st.spinner("A IA está preparando o desafio final..."):
                dados = ia.gerar_desafio_ordenacao(historia["titulo"])
                st.session_state.minijogo_dados = dados
                st.session_state.ordenacao_itens = []
        minijogo_ordenacao(st.session_state.minijogo_dados)
    else:
        st.success(f"Você completou '{historia['titulo']}'! 🎉")
        st.divider()

        if st.session_state.final_epico is None:
            with st.spinner("A IA está narrando o final..."):
                st.session_state.final_epico = ia.gerar_final_epico(historia["titulo"])

        st.subheader("✝ Narrativa Final")
        st.write(st.session_state.final_epico)
        st.divider()

        video_path = desafio.get("video", "")
        st.subheader("🎬 Vídeo Cinemático")
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.info("Vídeo cinemático em breve.")
        st.divider()

        st.subheader("🖼️ História em Quadrinhos")
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