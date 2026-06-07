from groq import Groq

class IAHelper:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def gerar_final_epico(self, usuario, historia, escolhas):
        escolhas_texto = "\n".join([f"- {e}" for e in escolhas])

        prompt = f"""Você é um narrador bíblico fiel às escrituras.

IMPORTANTE:
- Seja 100% fiel ao texto bíblico.
- NUNCA use o nome do jogador. Use sempre o nome bíblico original.
- Não invente detalhes que não existem na Bíblia.

A história concluída foi: "{historia.titulo}"

Escolhas feitas:
{escolhas_texto}

Narre o final épico em português, no máximo 3 parágrafos,
usando apenas os nomes bíblicos originais."""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return resposta.choices[0].message.content