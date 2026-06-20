import json

from groq import Groq


class IAHelper:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key) if api_key else None

    def _fallback_forca(self, jogo_base=None):
        if jogo_base:
            return jogo_base
        return {
            "versiculo_completo": "O SENHOR nao ve como o homem ve, pois o homem olha para a aparencia, mas o SENHOR olha para o coracao",
            "referencia": "1 Samuel 16:7",
            "palavra_oculta": "CORACAO",
            "versiculo_com_lacuna": "o homem olha para a aparencia, mas o SENHOR olha para o ___",
            "dica": "Parte do ser humano onde Deus enxerga a verdade",
        }

    def _fallback_vf(self, jogo_base=None):
        if jogo_base:
            return jogo_base
        return {
            "perguntas": [
                {
                    "pergunta": "Golias desafiou Israel por quarenta dias.",
                    "resposta": True,
                    "explicacao": "Correto. O periodo aparece em 1 Samuel 17:16.",
                },
                {
                    "pergunta": "Golias era de Belem.",
                    "resposta": False,
                    "explicacao": "Errado. Golias era de Gate, conforme 1 Samuel 17:4.",
                },
            ]
        }

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

    def gerar_jogo_forca(self, cena_titulo, referencia_biblica="", cena_texto="", jogo_base=None):
        fallback = self._fallback_forca(jogo_base)
        prompt = f"""Gere um jogo da forca baseado somente no contexto abaixo.

CENA: {cena_titulo}
REFERENCIA BIBLICA: {referencia_biblica}
TEXTO DA CENA:
{cena_texto}

REGRAS OBRIGATORIAS:
- Use apenas um versiculo real ligado diretamente a referencia e ao texto da cena.
- Nao use versiculos fora do trecho informado.
- A palavra oculta deve aparecer literalmente no versiculo_completo.
- A palavra oculta deve ter entre 4 e 10 letras, sem espacos.
- versiculo_com_lacuna deve substituir apenas a palavra oculta por ___.
- A dica deve explicar a palavra dentro do contexto da cena.
- Responda apenas em JSON valido, sem markdown.

Formato exato:
{{
    "versiculo_completo": "texto completo do versiculo",
    "referencia": "Livro Capitulo:Versiculo",
    "palavra_oculta": "PALAVRA",
    "versiculo_com_lacuna": "texto com ___ no lugar da palavra",
    "dica": "dica curta"
}}"""
        dados = self._gerar(prompt, 450, fallback)
        campos = ["versiculo_completo", "referencia", "palavra_oculta", "versiculo_com_lacuna", "dica"]
        if not all(dados.get(campo) for campo in campos):
            return fallback
        return dados

    def gerar_verdadeiro_falso(self, cena_titulo, referencia_biblica="", cena_texto="", jogo_base=None):
        fallback = self._fallback_vf(jogo_base)
        prompt = f"""Gere 5 perguntas de verdadeiro ou falso baseadas somente no contexto abaixo.

CENA: {cena_titulo}
REFERENCIA BIBLICA: {referencia_biblica}
TEXTO DA CENA:
{cena_texto}

REGRAS OBRIGATORIAS:
- Use apenas fatos presentes no texto da cena ou na referencia biblica indicada.
- Nao acrescente nomes, numeros, falas ou detalhes que nao aparecam no contexto.
- Misture perguntas verdadeiras e falsas.
- As falsas devem ser plausiveis, mas claramente corrigidas pela explicacao.
- Cada explicacao deve citar a referencia biblica quando possivel.
- Responda apenas em JSON valido, sem markdown.

Formato exato:
{{
    "perguntas": [
        {{
            "pergunta": "texto da pergunta",
            "resposta": true,
            "explicacao": "explicacao com referencia biblica"
        }}
    ]
}}"""
        dados = self._gerar(prompt, 750, fallback)
        perguntas = dados.get("perguntas", [])
        if not perguntas or not all("pergunta" in p and "resposta" in p and "explicacao" in p for p in perguntas):
            return fallback
        return dados

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
