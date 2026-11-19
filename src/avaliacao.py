"""Avaliação automática do Citizen Assist AI.

Gera:
  docs/resultados_testes.csv   -> uma linha por pergunta (esperado, obtido, acerto, tempo)
  docs/resultados_testes.md    -> indicadores, matriz por tipo e comparação dos modelos A e B

Uso: python src/avaliacao.py   (ou python src/sistema.py --avaliar)
"""

import csv
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assistente import Assistente, RAIZ  # noqa: E402

REPETICOES = 5  # cada pergunta é medida 5 vezes; usamos a média para reduzir ruído
CONJUNTOS = {
    "teste": os.path.join(RAIZ, "data", "perguntas_teste.json"),
    "validacao": os.path.join(RAIZ, "data", "perguntas_validacao.json"),
}
PASTA_DOCS = os.path.join(RAIZ, "docs")


def carregar_perguntas(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def executar(assistente, perguntas, conjunto):
    linhas = []
    for item in perguntas:
        tempos = []
        for _ in range(REPETICOES):
            resultado = assistente.consultar(item["pergunta"], modelo="B")
            tempos.append(resultado["tempo_ms"])
        obtido = resultado["id"] if resultado["status"] == "ENCONTRADA" else resultado["status"]
        linhas.append({
            "conjunto": conjunto,
            "id": item["id"],
            "tipo": item["tipo"],
            "pergunta": item["pergunta"] if item["pergunta"] else "(vazia)",
            "esperado": item["esperado"],
            "obtido": obtido,
            "acerto": "ACERTO" if obtido == item["esperado"] else "ERRO",
            "tempo_ms": round(statistics.mean(tempos), 3),
        })
    return linhas


def indicadores(linhas):
    total = len(linhas)
    acertos = sum(1 for l in linhas if l["acerto"] == "ACERTO")
    tempos = [l["tempo_ms"] for l in linhas]
    return {
        "total": total,
        "acertos": acertos,
        "taxa": 100 * acertos / total if total else 0,
        "tempo_medio": statistics.mean(tempos),
        "tempo_mediana": statistics.median(tempos),
        "tempo_max": max(tempos),
    }


# --------------------------------------------------------------------------
# Comparação dos modelos de instrução A e B
# --------------------------------------------------------------------------
CRITERIOS = [
    ("cita_fonte_com_link", "Cita a fonte com link verificável"),
    ("mostra_data_verificacao", "Mostra a data de verificação"),
    ("aviso_quando_necessario", "Exibe aviso quando a orientação exige confirmação"),
    ("sugere_continuidade", "Sugere assuntos relacionados (continuidade)"),
    ("frases_curtas", "Frases com até 25 palavras em média (clareza)"),
]


def avaliar_formato(texto, registro):
    frases = [f for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]
    media_palavras = statistics.mean(len(f.split()) for f in frases) if frases else 0
    return {
        "cita_fonte_com_link": registro["referencia"]["url"] in texto,
        "mostra_data_verificacao": registro["data_verificacao"] in texto,
        "aviso_quando_necessario": (not registro.get("requer_confirmacao")) or ("Confirme" in texto),
        "sugere_continuidade": (not registro.get("relacionados")) or ("relacionados" in texto.lower()),
        "frases_curtas": media_palavras <= 25,
    }


def comparar_modelos(assistente, linhas):
    encontrados = [l for l in linhas if l["obtido"] not in ("ENTRADA_INVALIDA", "SEM_RESPOSTA", "AMBIGUA")]
    placar = {"A": {c: 0 for c, _ in CRITERIOS}, "B": {c: 0 for c, _ in CRITERIOS}}
    exemplos = {}
    for l in encontrados:
        registro = assistente.por_id[l["obtido"]]
        for modelo in ("A", "B"):
            texto = assistente.consultar(registro["id"], modelo=modelo)["texto"]
            for criterio, ok in avaliar_formato(texto, registro).items():
                placar[modelo][criterio] += int(ok)
            exemplos.setdefault(modelo, texto)
    return placar, len(encontrados), exemplos


# --------------------------------------------------------------------------
def salvar_csv(linhas, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)


def salvar_markdown(caminho, linhas, ind, placar, n_comparados, exemplos):
    m = ["# Resultados dos testes – Citizen Assist AI", "",
         "> Arquivo gerado automaticamente por `python src/avaliacao.py`. Não edite à mão.", "",
         "## Indicadores", "",
         "| Conjunto | Perguntas | Acertos | Taxa de acerto | Tempo médio (ms) | Mediana (ms) | Máximo (ms) |",
         "|---|---|---|---|---|---|---|"]
    for nome, i in ind.items():
        m.append(f"| {nome} | {i['total']} | {i['acertos']} | {i['taxa']:.1f}% | "
                 f"{i['tempo_medio']:.3f} | {i['tempo_mediana']:.3f} | {i['tempo_max']:.3f} |")

    m += ["", "## Acerto por tipo de pergunta", "", "| Tipo | Acertos / Total |", "|---|---|"]
    por_tipo = {}
    for l in linhas:
        t = por_tipo.setdefault(l["tipo"], [0, 0])
        t[0] += l["acerto"] == "ACERTO"
        t[1] += 1
    for tipo, (a, t) in sorted(por_tipo.items()):
        m.append(f"| {tipo} | {a} / {t} |")

    m += ["", "## Registro detalhado", "",
          "| Conjunto | ID | Tipo | Pergunta | Esperado | Obtido | Resultado | Tempo (ms) |",
          "|---|---|---|---|---|---|---|---|"]
    for l in linhas:
        m.append(f"| {l['conjunto']} | {l['id']} | {l['tipo']} | {l['pergunta']} | {l['esperado']} | "
                 f"{l['obtido']} | {l['acerto']} | {l['tempo_ms']:.3f} |")

    m += ["", "## Comparação dos modelos de instrução (A x B)", "",
          f"Critérios verificados automaticamente em {n_comparados} respostas encontradas.", "",
          "| Critério | Modelo A | Modelo B |", "|---|---|---|"]
    for chave, descricao in CRITERIOS:
        m.append(f"| {descricao} | {placar['A'][chave]}/{n_comparados} | {placar['B'][chave]}/{n_comparados} |")
    total_a = sum(placar["A"].values())
    total_b = sum(placar["B"].values())
    maximo = n_comparados * len(CRITERIOS)
    m += [f"| **Total** | **{total_a}/{maximo}** | **{total_b}/{maximo}** |", "",
          "### Exemplo de saída – Modelo A", "", "```", exemplos.get("A", ""), "```", "",
          "### Exemplo de saída – Modelo B", "", "```", exemplos.get("B", ""), "```", ""]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(m))


def main():
    assistente = Assistente()
    todas, ind = [], {}
    for nome, caminho in CONJUNTOS.items():
        linhas = executar(assistente, carregar_perguntas(caminho), nome)
        ind[nome] = indicadores(linhas)
        todas += linhas
    ind["geral"] = indicadores(todas)

    placar, n, exemplos = comparar_modelos(assistente, todas)

    os.makedirs(PASTA_DOCS, exist_ok=True)
    salvar_csv(todas, os.path.join(PASTA_DOCS, "resultados_testes.csv"))
    salvar_markdown(os.path.join(PASTA_DOCS, "resultados_testes.md"), todas, ind, placar, n, exemplos)

    print("=" * 70)
    print("AVALIAÇÃO DO CITIZEN ASSIST AI")
    print("=" * 70)
    for nome, i in ind.items():
        print(f"{nome:<10} {i['acertos']:>2}/{i['total']:<2} acertos  "
              f"taxa = {i['taxa']:5.1f}%   tempo médio = {i['tempo_medio']:.3f} ms")
    print("-" * 70)
    for l in todas:
        if l["acerto"] == "ERRO":
            print(f"ERRO {l['id']}: '{l['pergunta']}' esperado={l['esperado']} obtido={l['obtido']}")
    print("-" * 70)
    print(f"Modelo A: {sum(placar['A'].values())} pts | Modelo B: {sum(placar['B'].values())} pts "
          f"(máx. {n * len(CRITERIOS)})")
    print("Relatórios salvos em docs/resultados_testes.md e docs/resultados_testes.csv")


if __name__ == "__main__":
    main()
