import streamlit as st
import json
from src.usuario import Usuario
from src.historia import Historia
from src.motor_narrativa import MotorNarrativa
from src.carregador import Carregador

st.set_page_config(
    page_title="Projeto Bíblico",
    page_icon="✝",
    layout="centered"
)

carregador = Carregador("data/historias.json")
historias_data = carregador.carregar()

if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "historia" not in st.session_state:
    st.session_state.historia = None
if "motor" not in st.session_state:
    st.session_state.motor = None
if "capitulo" not in st.session_state:
    st.session_state.capitulo = 0

if st.session_state.usuario is None:
    st.title("✝ Projeto Bíblico")
    st.markdown("Explore histórias sagradas de um jeito diferente.")
    st.divider()
    nome = st.text_input("Digite seu nome para começar:")
    if st.button("Entrar") and nome:
        st.session_state.usuario = Usuario(nome)
        st.rerun()

elif st.session_state.historia is None:
    st.title(f"Olá, {st.session_state.usuario.nome}! 👋")
    st.markdown("Escolha uma história para começar:")
    st.divider()
    for i, h in enumerate(historias_data):
        with st.container(border=True):
            st.markdown(f"### {h['titulo']}")
            st.caption(f"Categoria: {h['categoria']}")
            st.write(h['narrativa'])
            if st.button(f"Jogar", key=f"historia_{i}"):
                historia = Historia(h['titulo'], h['categoria'], h['narrativa'])
                for cap in h['capitulos']:
                    historia.adicionar_capitulo(cap)
                st.session_state.historia = historia
                st.session_state.usuario.iniciar_historia(historia.titulo)
                st.session_state.motor = MotorNarrativa(
                    st.session_state.usuario, historia
                )
                st.session_state.capitulo = 0
                st.rerun()

else:
    motor = st.session_state.motor
    historia = st.session_state.historia
    usuario = st.session_state.usuario
    capitulo_idx = st.session_state.capitulo

    st.title(f"✝ {historia.titulo}")
    progresso = int((capitulo_idx / len(historia.capitulos)) * 100)
    st.progress(progresso, text=f"Progresso: {progresso}%")
    st.caption(f"Pontos: {usuario.pontos} ⭐")
    st.divider()

    if capitulo_idx < len(historia.capitulos):
        cap = historia.capitulos[capitulo_idx]
        st.subheader(cap['titulo'])
        st.write(cap['texto'])
        st.divider()
        st.markdown("**O que você faz?**")
        for i, escolha in enumerate(cap['escolhas']):
            if st.button(escolha, key=f"escolha_{i}"):
                usuario.ganhar_pontos(10)
                st.session_state.capitulo += 1
                novo_progresso = int(
                    (st.session_state.capitulo / len(historia.capitulos)) * 100
                )
                usuario.atualizar_progresso(historia.titulo, novo_progresso)
                st.rerun()
    else:
        st.success(f"Você concluiu '{historia.titulo}'! 🎉")
        st.metric("Pontos ganhos", usuario.pontos)
        if st.button("Escolher outra história"):
            st.session_state.historia = None
            st.session_state.motor = None
            st.session_state.capitulo = 0
            st.rerun()