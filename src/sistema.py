"""Citizen Assist AI – interface textual.

Execução:
    python src/sistema.py            -> modo interativo (menu + perguntas)
    python src/sistema.py --avaliar  -> roda as perguntas de teste e gera indicadores
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assistente import Assistente  # noqa: E402
from base import ErroBase          # noqa: E402
import respostas                   # noqa: E402

LINHA = "─" * 78


def cabecalho():
    print(LINHA)
    print("  CITIZEN ASSIST AI · orientação cidadã (protótipo acadêmico FIAP)")
    print(LINHA)
    print("  " + respostas.AVISO_GERAL)
    print("  Não digite dados pessoais (CPF, telefone, e-mail): eles não são necessários.")
    print(LINHA)


def menu_principal(assistente):
    print("\nO que você quer fazer?")
    chaves = list(assistente.temas)
    for i, chave in enumerate(chaves, start=1):
        tema = assistente.temas[chave]
        print(f"  [{i}] {tema['nome']} — {tema['descricao']}")
    print("  [P] Fazer uma pergunta com suas palavras")
    print("  [S] Sair")
    return chaves


def ler(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return "S"


def navegar_tema(assistente, chave):
    tema = assistente.temas[chave]
    print(f"\n{LINHA}\n  {tema['nome'].upper()}\n{LINHA}")
    for subtema, registros in assistente.listar_tema(chave).items():
        print(f"  {tema['subtemas'].get(subtema, subtema)}")
        for r in registros:
            print(f"     [{r['id']}] {r['titulo']}")
    vizinhos = [assistente.temas[v]["nome"] for v in assistente.temas_vizinhos(chave)]
    if vizinhos:
        print(f"\n  Temas relacionados: {', '.join(vizinhos)}")
    print("\nDigite o código do assunto (ex.: D01), uma pergunta sobre este tema, ou [V] para voltar.")
    while True:
        entrada = ler("tema> ").strip()
        if entrada.upper() == "V":
            return
        if entrada.upper() == "S":
            raise SystemExit
        if not entrada:
            print(respostas.entrada_invalida())
            continue
        mostrar(assistente, entrada, tema=chave)
        print("\n[V] voltar ao menu · ou digite outro código/pergunta")


def mostrar(assistente, pergunta, tema=None):
    resultado = assistente.consultar(pergunta, modelo="B", tema=tema)
    # Se a busca restrita ao tema não achar nada, tenta na base inteira.
    if tema and resultado["status"] == "SEM_RESPOSTA":
        resultado = assistente.consultar(pergunta, modelo="B")
    print("\n" + resultado["texto"])
    if resultado["status"] == "ENCONTRADA":
        print("\nPara continuar, digite o código de um assunto relacionado ou faça outra pergunta.")


def modo_pergunta(assistente):
    print("\nDigite sua pergunta (ou [V] para voltar ao menu).")
    while True:
        pergunta = ler("pergunta> ")
        if pergunta.strip().upper() == "V":
            return
        if pergunta.strip().upper() == "S":
            raise SystemExit
        mostrar(assistente, pergunta)


def interativo():
    try:
        assistente = Assistente()
    except ErroBase as erro:
        print(f"Não foi possível iniciar o assistente: {erro}")
        print("Verifique o arquivo data/base_conhecimento.json.")
        sys.exit(1)

    cabecalho()
    for aviso in assistente.avisos:
        print(f"[aviso de manutenção] {aviso}")
    print(f"Base carregada: {len(assistente.registros)} orientações em {len(assistente.temas)} temas.")

    try:
        while True:
            chaves = menu_principal(assistente)
            opcao = ler("menu> ").strip().upper()
            if opcao == "S":
                break
            if opcao == "P":
                modo_pergunta(assistente)
            elif opcao.isdigit() and 1 <= int(opcao) <= len(chaves):
                navegar_tema(assistente, chaves[int(opcao) - 1])
            elif opcao == "":
                print(respostas.entrada_invalida())
            elif opcao.isdigit():
                print(f"Opção {opcao} não existe. Escolha entre 1 e {len(chaves)}, P ou S.")
            else:
                # Texto livre direto no menu também é aceito como pergunta.
                mostrar(assistente, opcao)
    except SystemExit:
        pass
    print("\nAté logo! Lembre-se de confirmar as informações nos canais oficiais.")


if __name__ == "__main__":
    if "--avaliar" in sys.argv:
        import avaliacao
        avaliacao.main()
    else:
        interativo()
