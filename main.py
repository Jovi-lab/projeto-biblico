from src.usuario import Usuario
from src.historia import Historia

jovi = Usuario("Jovi")
jovi.iniciar_historia("Davi e Golias")
jovi.ganhar_pontos(50)

davi = Historia(
    titulo="Davi e Golias",
    categoria="Coragem",
    narrativa="A história de um jovem pastor que enfrentou um gigante com fé."
)

davi.adicionar_capitulo({
    "titulo": "O Desafio",
    "texto": "Golias avança e desafia o exército israelita. Ninguém tem coragem de enfrentá-lo. Davi, ainda jovem, ouve as palavras do gigante...",
    "escolhas": [
        "Aceitar o desafio e enfrentar Golias",
        "Falar com o rei Saul primeiro",
        "Observar o gigante por mais tempo"
    ]
})

davi.mostrar_info()
davi.mostrar_capitulo(0)