# Classe Usuario — gerencia nome e progresso do jogador
# Classe Historia — armazena titulo, categoria e narrativa
class Usuario:
    def __init__(self, nome):
        self.nome = nome
        self.pontos = 0
        self.historias_concluidas = []
        self.historias_em_andamento = {}

    def ganhar_pontos(self, quantidade):
        self.pontos += quantidade
        print(f"{self.nome} ganhou {quantidade} pontos! Total: {self.pontos}")

    def iniciar_historia(self, titulo):
        self.historias_em_andamento[titulo] = 0
        print(f'História "{titulo}" iniciada!')

    def atualizar_progresso(self, titulo, progresso):
        if titulo in self.historias_em_andamento:
            self.historias_em_andamento[titulo] = progresso
            if progresso >= 100:
                self.historias_concluidas.append(titulo)
                del self.historias_em_andamento[titulo]
                print(f'"{titulo}" concluída! Parabéns!')

    def status(self):
        print(f"\n=== {self.nome} ===")
        print(f"Pontos: {self.pontos}")
        print(f"Concluídas: {self.historias_concluidas}")
        print(f"Em andamento: {self.historias_em_andamento}")