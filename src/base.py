"""Carga e validação da base de conhecimento (arquivo JSON).

Toda a regra de "o que é um registro válido" fica aqui. Para acrescentar ou
corrigir orientações basta editar data/base_conhecimento.json: nenhuma regra
do programa precisa ser reescrita.
"""

import json
import os
import re

CAMPOS_OBRIGATORIOS = [
    "id", "tema", "titulo", "palavras_chave",
    "orientacao", "referencia", "data_verificacao",
]
CAMPOS_REFERENCIA = ["fonte", "url"]
PADRAO_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ErroBase(Exception):
    """Erro que impede o uso da base (arquivo ausente, vazio ou ilegível)."""


def carregar_base(caminho):
    """Lê o JSON e devolve (temas, registros_validos, avisos).

    - Arquivo ausente, vazio ou JSON malformado -> ErroBase.
    - Registros inconsistentes são descartados e listados em `avisos`,
      para que um único erro de digitação não derrube o assistente.
    """
    if not os.path.exists(caminho):
        raise ErroBase(f"Arquivo da base não encontrado: {caminho}")
    if os.path.getsize(caminho) == 0:
        raise ErroBase(f"Arquivo da base está vazio: {caminho}")

    try:
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ErroBase(f"JSON inválido na linha {erro.lineno}: {erro.msg}")

    temas = dados.get("temas")
    registros = dados.get("orientacoes")
    if not isinstance(temas, dict) or not temas:
        raise ErroBase("A base não possui a seção 'temas'.")
    if not isinstance(registros, list) or not registros:
        raise ErroBase("A base não possui orientações cadastradas.")

    validos, avisos, ids_vistos = [], [], set()
    for posicao, registro in enumerate(registros, start=1):
        problemas = validar_registro(registro, temas, ids_vistos)
        if problemas:
            ident = registro.get("id", f"posição {posicao}") if isinstance(registro, dict) else f"posição {posicao}"
            avisos.append(f"Registro {ident} ignorado: " + "; ".join(problemas))
        else:
            ids_vistos.add(registro["id"])
            registro.setdefault("relacionados", [])
            registro.setdefault("perguntas_exemplo", [])
            registro.setdefault("requer_confirmacao", True)
            validos.append(registro)

    if not validos:
        raise ErroBase("Nenhum registro válido na base.")

    # Relacionados que apontam para ids inexistentes são removidos (com aviso).
    ids = {r["id"] for r in validos}
    for registro in validos:
        quebrados = [rel for rel in registro["relacionados"] if rel not in ids]
        if quebrados:
            avisos.append(f"Registro {registro['id']}: relacionados inexistentes removidos {quebrados}")
            registro["relacionados"] = [rel for rel in registro["relacionados"] if rel in ids]

    return temas, validos, avisos


def validar_registro(registro, temas, ids_vistos):
    """Devolve a lista de problemas encontrados (lista vazia = válido)."""
    if not isinstance(registro, dict):
        return ["não é um objeto JSON"]

    problemas = []
    for campo in CAMPOS_OBRIGATORIOS:
        valor = registro.get(campo)
        if valor is None or (isinstance(valor, (str, list, dict)) and not valor):
            problemas.append(f"campo '{campo}' ausente ou vazio")

    if registro.get("id") in ids_vistos:
        problemas.append("id duplicado")
    if registro.get("tema") and registro["tema"] not in temas:
        problemas.append(f"tema '{registro['tema']}' não existe")
    if registro.get("palavras_chave") and not isinstance(registro["palavras_chave"], list):
        problemas.append("'palavras_chave' deve ser uma lista")

    referencia = registro.get("referencia")
    if isinstance(referencia, dict):
        for campo in CAMPOS_REFERENCIA:
            if not referencia.get(campo):
                problemas.append(f"referência sem '{campo}'")
        url = referencia.get("url", "")
        if url and not url.startswith("https://"):
            problemas.append("url da referência deve começar com https://")
    elif referencia is not None:
        problemas.append("'referencia' deve ter 'fonte' e 'url'")

    data = registro.get("data_verificacao")
    if data and not PADRAO_DATA.match(str(data)):
        problemas.append("data_verificacao deve estar no formato AAAA-MM-DD")

    return problemas


def indexar_por_id(registros):
    """Dicionário id -> registro (recuperação direta em O(1))."""
    return {r["id"]: r for r in registros}


def agrupar_por_tema(registros):
    """Dicionário tema -> {subtema -> [registros]} (organização hierárquica)."""
    arvore = {}
    for r in registros:
        arvore.setdefault(r["tema"], {}).setdefault(r.get("subtema", "geral"), []).append(r)
    return arvore
