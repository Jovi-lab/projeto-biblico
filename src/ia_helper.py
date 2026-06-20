import json

from groq import Groq


class IAHelper:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key) if api_key else None

    def _extrair_json(self, texto, fallback):
        try:
            inicio = texto.find("{")
            fim = texto.rfind("}") + 1
            if inicio < 0 or fim <= inicio:
                return fallback
            return json.loads(texto[inicio:fim])
        except (json.JSONDecodeError, TypeError):
            return fallback

    def _gerar(self, prompt, max_tokens, fallback):
        if not self.client:
            return fallback

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Voce responde em portugues do Brasil, com fidelidade estrita ao texto biblico "
                        "fornecido pelo usuario. Quando houver duvida, nao invente."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        texto = resposta.choices[0].message.content
        return self._extrair_json(texto, fallback)

    def gerar_desafio_ordenacao(self, historia_titulo, eventos_base=None):
        if eventos_base:
            return {"eventos": eventos_base}

        fallback = {
            "eventos": [
                "Samuel unge Davi como rei em Belem",
                "Golias desafia Israel por quarenta dias",
                "Davi chega ao acampamento com comida",
                "Davi recusa a armadura de Saul",
                "Davi acerta Golias na testa com a funda",
                "Os filisteus fogem ao ver Golias cair",
            ]
        }
        prompt = f"""Gere 6 eventos da historia "{historia_titulo}" para um jogo de ordenacao cronologica.

REGRAS:
- Use apenas eventos biblicos reais.
- Os eventos devem estar em ordem cronologica.
- Cada evento deve ser curto, claro e sem detalhes inventados.
- Responda apenas em JSON valido, sem markdown.

Formato exato:
{{
    "eventos": [
        "primeiro evento",
        "segundo evento",
        "terceiro evento",
        "quarto evento",
        "quinto evento",
        "sexto evento"
    ]
}}"""
        dados = self._gerar(prompt, 450, fallback)
        if not dados.get("eventos"):
            return fallback
        return dados

    def gerar_final_epico(self, historia_titulo, desafio=None, cenas=None):
        referencias = []
        trechos = []
        for cena in cenas or []:
            if cena.get("referencia"):
                referencias.append(cena["referencia"])
            if cena.get("texto"):
                trechos.append(cena["texto"])

        eventos = (desafio or {}).get("eventos", [])
        contexto = "\n".join(trechos)
        eventos_txt = "\n".join(f"- {evento}" for evento in eventos)
        referencias_txt = ", ".join(referencias)

        fallback = (
            "Davi enfrentou Golias confiando no SENHOR, nao na forca humana. "
            "Com uma pedra lancada pela funda, atingiu o filisteu na testa, e Golias caiu com o rosto em terra. "
            "Ao verem que o seu campeao estava morto, os filisteus fugiram, conforme o relato de 1 Samuel 17."
        )

        if not self.client:
            return fallback

        prompt = f"""Narre o final da historia "{historia_titulo}" em no maximo 3 paragrafos.

REFERENCIAS: {referencias_txt}
EVENTOS CONFIRMADOS:
{eventos_txt}

CONTEXTO DA HISTORIA:
{contexto}

REGRAS:
- Seja fiel ao texto biblico e ao contexto fornecido.
- Nao invente detalhes, emocoes, falas ou personagens.
- Use apenas os nomes biblicos originais, nunca o nome do jogador.
- Se houver duvida, escreva de forma mais simples e factual.
- Responda apenas com a narrativa final, sem JSON."""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Voce e um narrador biblico fiel as Escrituras. Nao invente detalhes.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.25,
            max_tokens=520,
        )
        return resposta.choices[0].message.content
