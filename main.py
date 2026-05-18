from src.usuario import Usuario
from src.historia import Historia
from src.motor_narrativa import MotorNarrativa

jovi = Usuario("Jovi")

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

davi.adicionar_capitulo({
    "titulo": "A Decisão",
    "texto": "Davi pega cinco pedras lisas do riacho e se aproxima de Golias com sua funda. O gigante o despreza ao vê-lo tão jovem...",
    "escolhas": [
        "Usar a funda com confiança em Deus",
        "Tentar negociar com Golias",
        "Recuar e pensar em outra estratégia"
    ]
})

jovi.iniciar_historia("Davi e Golias")
motor = MotorNarrativa(jovi, davi)
motor.iniciar()

while motor.ativo:
    try:
        escolha = int(input("\nSua escolha: "))
        motor.avancar(escolha)
    except ValueError:
        print("Digite apenas números!")