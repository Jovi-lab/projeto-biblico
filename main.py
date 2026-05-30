from src.usuario import Usuario
from src.historia import Historia
from src.motor_narrativa import MotorNarrativa
from src.carregador import Carregador

nome = input("Digite seu nome: ")
usuario = Usuario(nome)

carregador = Carregador("data/historias.json")
historias_data = carregador.listar_titulos()

escolha = int(input("\nEscolha uma história: ")) - 1
dados = historias_data[escolha]

historia = Historia(
    titulo=dados["titulo"],
    categoria=dados["categoria"],
    narrativa=dados["narrativa"]
)

for cap in dados["capitulos"]:
    historia.adicionar_capitulo(cap)

usuario.iniciar_historia(historia.titulo)
motor = MotorNarrativa(usuario, historia)
motor.iniciar()

while motor.ativo:
    try:
        escolha = int(input("\nSua escolha: "))
        motor.avancar(escolha)
    except ValueError:
        print("Digite apenas números!")