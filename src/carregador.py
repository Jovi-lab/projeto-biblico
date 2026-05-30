import json

class Carregador:
    def __init__(self, caminho):
        self.caminho = caminho

    def carregar(self):
        with open(self.caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return dados["historias"]

    def listar_titulos(self):
        historias = self.carregar()
        print("\n=== Histórias disponíveis ===")
        for i, h in enumerate(historias):
            print(f"{i + 1}. {h['titulo']} — {h['categoria']}")
        return historias