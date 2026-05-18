class Historia:
    def __init__(self, titulo, categoria, narrativa):
        self.titulo = titulo
        self.categoria = categoria
        self.narrativa = narrativa
        self.capitulos = []
        self.pontos_interacao = 0

    def adicionar_capitulo(self, capitulo):
        self.capitulos.append(capitulo)
        print(f'Capítulo "{capitulo["titulo"]}" adicionado!')

    def mostrar_info(self):
        print(f"\n=== {self.titulo} ===")
        print(f"Categoria: {self.categoria}")
        print(f"Narrativa: {self.narrativa}")
        print(f"Capítulos: {len(self.capitulos)}")
        print(f"Pontos de interação: {self.pontos_interacao}")

    def mostrar_capitulo(self, numero):
        if numero < 0 or numero >= len(self.capitulos):
            print("Capítulo não encontrado.")
            return
        cap = self.capitulos[numero]
        print(f"\n--- {cap['titulo']} ---")
        print(cap["texto"])
        print("\nEscolhas disponíveis:")
        for i, escolha in enumerate(cap["escolhas"]):
            print(f"{i + 1}. {escolha}")