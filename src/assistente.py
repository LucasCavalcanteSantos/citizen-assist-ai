"""Núcleo do Citizen Assist AI: une base, busca, navegação e respostas.

É usado tanto pela interface de texto (sistema.py) quanto pela avaliação
automática (avaliacao.py), garantindo que os testes medem o mesmo fluxo que
o usuário vê.
"""

import os
import re
import time

from base import carregar_base, indexar_por_id, agrupar_por_tema
from busca import MotorBusca
import respostas

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_BASE = os.path.join(RAIZ, "data", "base_conhecimento.json")

# Padrões de dados pessoais que o assistente NÃO precisa e não deve guardar.
PADROES_PESSOAIS = {
    "CPF": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "e-mail": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "telefone": re.compile(r"\b\(?\d{2}\)?\s?9?\d{4}-?\d{4}\b"),
}
CODIGO_REGISTRO = re.compile(r"^[A-Za-z]\d{2}$")


class Assistente:
    def __init__(self, caminho_base=CAMINHO_BASE):
        self.temas, self.registros, self.avisos = carregar_base(caminho_base)
        self.por_id = indexar_por_id(self.registros)
        self.arvore = agrupar_por_tema(self.registros)
        self.motor = MotorBusca(self.registros)

    # ---------------------------------------------------------------- privacidade
    @staticmethod
    def detectar_dados_pessoais(texto):
        """Lista os tipos de dado pessoal encontrados no texto."""
        return [nome for nome, padrao in PADROES_PESSOAIS.items() if padrao.search(texto or "")]

    @staticmethod
    def mascarar(texto):
        for padrao in PADROES_PESSOAIS.values():
            texto = padrao.sub("[removido]", texto)
        return texto

    # ---------------------------------------------------------------- navegação
    def relacionados(self, registro):
        """Arestas do grafo de assuntos: registro -> registros relacionados."""
        return [self.por_id[rid] for rid in registro.get("relacionados", []) if rid in self.por_id]

    def temas_vizinhos(self, tema):
        """Arestas do grafo de temas (ex.: documentos <-> servicos)."""
        return self.temas.get(tema, {}).get("relacionados", [])

    def listar_tema(self, tema):
        """Registros de um tema, agrupados por subtema (hierarquia)."""
        return self.arvore.get(tema, {})

    # ---------------------------------------------------------------- consulta
    def consultar(self, pergunta, modelo="B", tema=None):
        """Fluxo completo: valida, busca, decide e formata.

        Devolve dict com status, id (quando houver), texto da resposta e tempo em ms.
        """
        inicio = time.perf_counter()
        pergunta = (pergunta or "").strip()
        alerta_privacidade = self.detectar_dados_pessoais(pergunta)
        pergunta_limpa = self.mascarar(pergunta)

        # Atalho: usuário digitou um código de registro (ex.: D01)
        if CODIGO_REGISTRO.match(pergunta_limpa) and pergunta_limpa.upper() in self.por_id:
            registro = self.por_id[pergunta_limpa.upper()]
            resultado = {"status": "ENCONTRADA", "resultados": [{"id": registro["id"], "pontuacao": None}],
                         "correcoes": []}
        else:
            resultado = self.motor.buscar(pergunta_limpa, tema=tema)

        status = resultado["status"]
        id_resposta = None
        if status == "ENTRADA_INVALIDA":
            texto = respostas.entrada_invalida()
        elif status == "SEM_RESPOSTA":
            texto = respostas.sem_resposta(self.temas)
        elif status == "AMBIGUA":
            opcoes = [self.por_id[r["id"]] for r in resultado["resultados"][:4]]
            texto = respostas.ambigua(opcoes)
        else:
            id_resposta = resultado["resultados"][0]["id"]
            registro = self.por_id[id_resposta]
            texto = respostas.formatar(registro, modelo, self.relacionados(registro))
            if resultado.get("correcoes"):
                ajustes = ", ".join(f"'{a}' → '{b}'" for a, b in resultado["correcoes"])
                texto = f"(Entendi {ajustes})\n\n" + texto

        if alerta_privacidade:
            texto = ("🔒 Você não precisa informar " + ", ".join(alerta_privacidade) +
                     " para usar o assistente. Esse dado foi ignorado e não foi salvo.\n\n" + texto)

        tempo_ms = (time.perf_counter() - inicio) * 1000
        return {"status": status, "id": id_resposta, "texto": texto, "tempo_ms": tempo_ms,
                "ranking": resultado["resultados"], "correcoes": resultado.get("correcoes", [])}
