class MotorNarrativa:
    def __init__(self, usuario, historia):
        self.usuario = usuario
        self.historia = historia
        self.capitulo_atual = 0
        self.ativo = False

    def iniciar(self):
        if len(self.historia.capitulos) == 0:
            print("Esta história não tem capítulos ainda.")
            return
        self.ativo = True
        print(f"\nIniciando: {self.historia.titulo}")
        print(f"Bem-vindo, {self.usuario.nome}!\n")
        self.mostrar_capitulo_atual()

    def mostrar_capitulo_atual(self):
        self.historia.mostrar_capitulo(self.capitulo_atual)

    def validar_escolha(self, escolha):
        cap = self.historia.capitulos[self.capitulo_atual]
        total = len(cap["escolhas"])
        if escolha < 1 or escolha > total:
            print(f"Escolha inválida. Digite um número entre 1 e {total}.")
            return False
        return True

    def avancar(self, escolha):
        if not self.validar_escolha(escolha):
            return
        cap = self.historia.capitulos[self.capitulo_atual]
        print(f'\nVocê escolheu: "{cap["escolhas"][escolha - 1]}"')
        self.usuario.ganhar_pontos(10)
        self.capitulo_atual += 1
        progresso = int((self.capitulo_atual / len(self.historia.capitulos)) * 100)
        self.usuario.atualizar_progresso(self.historia.titulo, progresso)
        if self.capitulo_atual >= len(self.historia.capitulos):
            print("\nVocê chegou ao fim desta história! 🎉")
            self.ativo = False
        else:
            self.mostrar_capitulo_atual()