"""Modelos de instrução de resposta (estratégias de prompt).

O protótipo não depende de API paga: cada "prompt" é implementado como um
modelo de instrução aplicado por regras. O texto dos modelos (que também pode
ser usado como system prompt de um LLM) está em docs/prompts.md.

MODELO_A – "Resposta direta"
    Papel: nenhum definido. Formato livre. Devolve só o texto da orientação e
    o nome da fonte em uma linha.

MODELO_B – "Assistente cidadão estruturado" (modelo adotado)
    Papel: assistente informativo NÃO oficial.
    Formato fixo: título > orientação em frases curtas > fonte com link e data
    > aviso de confirmação (quando exigido) > assuntos relacionados.
    Regras: sempre citar a fonte; nunca inventar passos; nunca se apresentar
    como canal oficial; quando não houver base, dizer isso e sugerir temas.
"""

import textwrap

AVISO_GERAL = ("Este assistente é um protótipo acadêmico e NÃO é um canal oficial. "
               "Confirme sempre no site do órgão responsável.")
AVISO_CONFIRMACAO = ("Requisitos, prazos e valores podem mudar. Confirme a informação "
                     "atualizada na fonte antes de ir ao atendimento.")
LARGURA = 78


# ----------------------------------------------------------------------------
# MODELO A
# ----------------------------------------------------------------------------
def modelo_a(registro, relacionados=None):
    return f"{registro['orientacao']} (Fonte: {registro['referencia']['fonte']})"


# ----------------------------------------------------------------------------
# MODELO B
# ----------------------------------------------------------------------------
def _frases(texto):
    """Divide a orientação em frases para exibir como passos curtos."""
    partes = []
    for trecho in texto.replace("\n", " ").split(". "):
        trecho = trecho.strip()
        if trecho:
            partes.append(trecho if trecho.endswith((".", "!", "?")) else trecho + ".")
    return partes or [texto]


def modelo_b(registro, relacionados=None):
    linhas = [f"📌 {registro['titulo']}", ""]
    for frase in _frases(registro["orientacao"]):
        linhas.append(textwrap.fill(frase, width=LARGURA, initial_indent=" • ", subsequent_indent="   "))
    ref = registro["referencia"]
    linhas += ["", f"🔗 Fonte: {ref['fonte']}", f"   {ref['url']}",
               f"   Verificado em: {registro['data_verificacao']}"]
    if registro.get("requer_confirmacao"):
        linhas += ["", "⚠️  " + AVISO_CONFIRMACAO]
    if relacionados:
        linhas += ["", "➡️  Assuntos relacionados:"]
        for rel in relacionados:
            linhas.append(f"   [{rel['id']}] {rel['titulo']}")
    return "\n".join(linhas)


MODELOS = {"A": modelo_a, "B": modelo_b}


def formatar(registro, modelo="B", relacionados=None):
    return MODELOS[modelo](registro, relacionados)


# ----------------------------------------------------------------------------
# Mensagens de limitação (iguais para os dois modelos)
# ----------------------------------------------------------------------------
def sem_resposta(temas):
    nomes = ", ".join(t["nome"] for t in temas.values())
    return ("Não encontrei uma orientação confiável sobre isso na minha base, então "
            "prefiro não arriscar uma resposta.\n"
            f"Posso ajudar com: {nomes}.\n"
            "Dica: tente usar palavras como 'CPF', 'identidade', 'cartão SUS', "
            "'INSS' ou 'reclamação'. Para outros assuntos, procure o portal gov.br "
            "ou o órgão responsável.")


def entrada_invalida():
    return "Não recebi nenhuma pergunta. Digite sua dúvida ou escolha um número do menu."


def ambigua(opcoes):
    linhas = ["Sua pergunta pode se referir a mais de um assunto. Qual deles?"]
    for op in opcoes:
        linhas.append(f"   [{op['id']}] {op['titulo']}")
    linhas.append("Digite o código (ex.: D01) ou reformule a pergunta.")
    return "\n".join(linhas)
