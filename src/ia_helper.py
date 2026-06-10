from groq import Groq
import json

class IAHelper:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def gerar_jogo_forca(self, cena_titulo):
        prompt = f"""Você é um especialista em Bíblia. Gere um jogo da forca baseado em um versículo bíblico relacionado à cena: "{cena_titulo}".

REGRAS:
- Use apenas versículos reais da Bíblia
- Escolha uma palavra importante do versículo para ocultar
- A palavra deve ter entre 4 e 10 letras
- Responda APENAS em JSON válido, sem texto antes ou depois

Formato exato:
{{
    "versiculo_completo": "texto completo do versículo",
    "referencia": "Livro Capítulo:Versículo",
    "palavra_oculta": "PALAVRA",
    "versiculo_com_lacuna": "texto com ___ no lugar da palavra",
    "dica": "dica sobre o significado da palavra no contexto"
}}"""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        texto = resposta.choices[0].message.content
        try:
            inicio = texto.find('{')
            fim = texto.rfind('}') + 1
            return json.loads(texto[inicio:fim])
        except:
            return {
                "versiculo_completo": "O SENHOR não vê como o homem vê, pois o homem olha para a aparência, mas o SENHOR olha para o coração",
                "referencia": "1 Samuel 16:7",
                "palavra_oculta": "CORAÇÃO",
                "versiculo_com_lacuna": "o homem olha para a aparência, mas o SENHOR olha para o ___",
                "dica": "Parte do ser humano onde Deus enxerga a verdade"
            }

    def gerar_verdadeiro_falso(self, cena_titulo, referencia_biblica):
        prompt = f"""Você é um especialista em Bíblia. Gere 5 perguntas de verdadeiro ou falso sobre: "{cena_titulo}" com base em {referencia_biblica}.

REGRAS:
- Use apenas fatos reais da Bíblia
- Misture perguntas verdadeiras e falsas
- As falsas devem ser plausíveis mas incorretas
- Responda APENAS em JSON válido, sem texto antes ou depois

Formato exato:
{{
    "perguntas": [
        {{
            "pergunta": "texto da pergunta",
            "resposta": true,
            "explicacao": "explicação com referência bíblica"
        }}
    ]
}}"""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        texto = resposta.choices[0].message.content
        try:
            inicio = texto.find('{')
            fim = texto.rfind('}') + 1
            return json.loads(texto[inicio:fim])
        except:
            return {
                "perguntas": [
                    {
                        "pergunta": "Golias media cerca de três metros de altura",
                        "resposta": True,
                        "explicacao": "Correto! 1 Samuel 17:4 descreve Golias com seis côvados e um palmo."
                    },
                    {
                        "pergunta": "Golias desafiou Israel por vinte dias",
                        "resposta": False,
                        "explicacao": "Errado! Golias desafiou por quarenta dias (1 Samuel 17:16)."
                    }
                ]
            }

    def gerar_desafio_ordenacao(self, historia_titulo):
        prompt = f"""Você é um especialista em Bíblia. Gere 6 eventos da história "{historia_titulo}" para um jogo de ordenação cronológica.

REGRAS:
- Use apenas eventos reais e fiéis à Bíblia
- Os eventos devem estar em ordem lógica e cronológica
- Cada evento deve ser uma frase curta e clara
- Responda APENAS em JSON válido, sem texto antes ou depois

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

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        texto = resposta.choices[0].message.content
        try:
            inicio = texto.find('{')
            fim = texto.rfind('}') + 1
            return json.loads(texto[inicio:fim])
        except:
            return {
                "eventos": [
                    "Samuel unge Davi como rei em Belém",
                    "Golias desafia Israel por quarenta dias",
                    "Davi chega ao acampamento com comida",
                    "Davi recusa a armadura de Saul",
                    "Davi acerta Golias na testa com a funda",
                    "Os filisteus fogem ao ver Golias cair"
                ]
            }

    def gerar_final_epico(self, historia_titulo):
        prompt = f"""Você é um narrador bíblico fiel às escrituras.

IMPORTANTE:
- Seja 100% fiel ao texto bíblico
- Use apenas os nomes bíblicos originais, NUNCA o nome do jogador
- Não invente detalhes que não existem na Bíblia

Narre o final da história "{historia_titulo}" em português,
no máximo 3 parágrafos, usando apenas os nomes bíblicos originais.
Seja preciso, bíblico e inspirador."""

        resposta = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return resposta.choices[0].message.content