from groq import Groq

class IAHelper:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def gerar_final_epico(self, usuario, historia, escolhas):
        escolhas_texto = "\n".join([f"- {e}" for e in escolhas])

        prompt = f"""Você é um narrador bíblico fiel às escrituras.

IMPORTANTE: 
- Seja 100% fiel ao texto bíblico. Use apenas fatos de 1 Samuel 17.
- NUNCA use o nome do jogador. Use sempre o nome bíblico original do personagem.
- Não invente detalhes que não existem na Bíblia.

A história concluída foi: "{historia.titulo}"

O jogador fez estas escolhas:
{escolhas_texto}

Narre o final épico em português, no máximo 3 parágrafos, usando apenas 
os nomes bíblicos originais. Seja preciso, bíblico e inspirador."""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return resposta.choices[0].message.content

    def gerar_descricao_cena(self, texto_cena):
        prompt = f"""Com base nesta cena bíblica:
"{texto_cena}"

Escreva uma descrição visual curta e poética em inglês (máximo 2 frases)
para gerar uma ilustração. Descreva cores, luz e personagens."""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return resposta.choices[0].message.content

    def gerar_url_imagem(self, texto_cena):
        descricao = self.gerar_descricao_cena(texto_cena)
        descricao_url = descricao.replace(" ", "%20").replace(",", "").replace(".", "")
        url = f"https://image.pollinations.ai/prompt/{descricao_url}?width=800&height=400&nologo=true"
        return url