"""Motor de busca do Citizen Assist AI.

Estratégia (explicada no README):
1. Normalização: minúsculas, sem acentos, sem pontuação.
2. Tokenização + remoção de stopwords + redução simples de plural.
3. Sinônimos: termos populares são trocados pelo termo da base (rg -> identidade).
4. Correção de digitação: palavras desconhecidas são aproximadas do vocabulário
   da base com difflib (similaridade >= 0,8).
5. Índice invertido (dicionário token -> conjunto de ids) para achar candidatos.
6. Pontuação ponderada de cada candidato:
      frase-chave inteira encontrada na pergunta ... +3 por frase
      token presente nas palavras-chave ............ +2
      token presente no título ..................... +1
      token presente nas perguntas de exemplo ...... +1
   A pontuação final é multiplicada pela cobertura (fração dos tokens da
   pergunta que foram reconhecidos), o que penaliza perguntas fora do tema.
7. Decisão:
      - pergunta vazia/sem conteúdo ............... ENTRADA_INVALIDA
      - só palavras genéricas de tema ("documento") AMBIGUA (lista o tema)
      - melhor pontuação < LIMIAR_MINIMO ........... SEM_RESPOSTA
      - 2º colocado >= 90% do 1º (registros dif.) . AMBIGUA (mostra opções)
      - caso contrário ............................. ENCONTRADA
"""

import difflib
import re
import unicodedata

LIMIAR_MINIMO = 3.0        # calibrado na rodada 1 (ver docs/resultados_testes.md)
FATOR_AMBIGUIDADE = 0.9    # calibrado na rodada 1
SIMILARIDADE_DIGITACAO = 0.8

# Palavras genéricas que nomeiam um TEMA inteiro, não um assunto específico.
# Se a pergunta tiver só esse tipo de palavra, ela é ambígua.
PALAVRAS_DE_TEMA = {
    "documento": "documentos", "documentacao": "documentos",
    "servico": "servicos", "beneficio": "servicos", "saude": "servicos",
    "direito": "direitos", "denuncia": "direitos", "reclamacao": "direitos",
}

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "por", "para", "pra", "pro", "com", "sem", "e", "ou",
    "que", "qual", "quais", "como", "onde", "quando", "quanto", "porque", "se", "eu",
    "me", "meu", "minha", "meus", "minhas", "voce", "seu", "sua", "isso", "esse", "essa",
    "este", "esta", "ele", "ela", "ao", "aos", "ja", "mais", "muito", "faco", "fazer",
    "preciso", "precisa", "quero", "gostaria", "posso", "pode", "consigo", "tem", "ter",
    "ser", "sao", "e", "foi", "vai", "nao", "sim", "outro", "outra", "agora", "favor",
    "ola", "oi", "bom", "dia", "tarde", "noite", "obrigado", "obrigada", "ajuda",
}

# termo popular -> termo usado na base
SINONIMOS = {
    "rg": "identidade",
    "cin": "identidade",
    "cnh": "habilitacao",
    "cadunico": "cadastro unico",
    "bolsa": "bolsa familia",
    "loja": "empresa",
    "comprei": "compra",
    "golpe": "denuncia",
    "aposentar": "aposentadoria",
    "zap": "whatsapp",
    "eleitoral": "eleitor",
    "imprimo": "imprimir",
    "denuncio": "denunciar",
    "inscrevo": "inscrever",
    "reclamo": "reclamar",
}


def normalizar(texto):
    """Minúsculas, sem acento e sem pontuação (mantém ponto de 'gov.br')."""
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9.\s]", " ", texto)
    texto = re.sub(r"(?<![a-z0-9])\.|\.(?![a-z0-9])", " ", texto)  # remove ponto solto
    return re.sub(r"\s+", " ", texto).strip()


def singular(token):
    """Redução simples de plural ('cartoes' -> 'cartao', 'dados' -> 'dado')."""
    if len(token) > 4 and token.endswith("oes"):
        return token[:-3] + "ao"
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenizar(texto):
    tokens = []
    for palavra in normalizar(texto).split():
        palavra = SINONIMOS.get(palavra, palavra)
        for parte in palavra.split():
            if parte not in STOPWORDS:
                tokens.append(singular(parte))
    return tokens


class MotorBusca:
    def __init__(self, registros):
        self.registros = {r["id"]: r for r in registros}
        self.indice = {}          # token -> set(ids)
        self.campos = {}          # id -> {"chave": set, "titulo": set, "exemplos": set, "frases": list}
        for r in registros:
            chave = set()
            frases = []
            for termo in r["palavras_chave"]:
                toks = tokenizar(termo)
                chave.update(toks)
                if len(toks) > 1:
                    frases.append(" ".join(toks))
            titulo = set(tokenizar(r["titulo"]))
            exemplos = set()
            for pergunta in r.get("perguntas_exemplo", []):
                exemplos.update(tokenizar(pergunta))
            self.campos[r["id"]] = {"chave": chave, "titulo": titulo, "exemplos": exemplos, "frases": frases}
            for token in chave | titulo | exemplos:
                self.indice.setdefault(token, set()).add(r["id"])
        self.vocabulario = sorted(self.indice)

    # ------------------------------------------------------------------
    def corrigir(self, tokens):
        """Troca tokens desconhecidos pelo termo mais parecido do vocabulário."""
        corrigidos, correcoes = [], []
        for token in tokens:
            if token in self.indice or len(token) < 4:
                corrigidos.append(token)
                continue
            parecido = difflib.get_close_matches(token, self.vocabulario, n=1, cutoff=SIMILARIDADE_DIGITACAO)
            if parecido:
                corrigidos.append(parecido[0])
                correcoes.append((token, parecido[0]))
            else:
                corrigidos.append(token)
        return corrigidos, correcoes

    def pontuar(self, id_registro, tokens):
        campos = self.campos[id_registro]
        frase_consulta = " ".join(tokens)
        pontos = 3 * sum(1 for frase in campos["frases"] if frase in frase_consulta)
        for token in set(tokens):
            if token in campos["chave"]:
                pontos += 2
            if token in campos["titulo"]:
                pontos += 1
            if token in campos["exemplos"]:
                pontos += 1
        return pontos

    def buscar(self, pergunta, tema=None):
        """Devolve um dicionário com status, resultados ordenados e diagnóstico."""
        if pergunta is None or not str(pergunta).strip():
            return {"status": "ENTRADA_INVALIDA", "resultados": [], "correcoes": []}

        tokens = tokenizar(pergunta)
        if not tokens:
            return {"status": "ENTRADA_INVALIDA", "resultados": [], "correcoes": []}

        # Pergunta formada só por palavras genéricas de tema -> ambígua.
        if all(t in PALAVRAS_DE_TEMA for t in tokens):
            tema_generico = PALAVRAS_DE_TEMA[tokens[0]]
            ids = [i for i, r in self.registros.items() if r["tema"] == tema_generico]
            return {"status": "AMBIGUA", "resultados": [{"id": i, "pontuacao": None} for i in sorted(ids)],
                    "correcoes": [], "cobertura": 1.0}

        tokens, correcoes = self.corrigir(tokens)
        reconhecidos = [t for t in tokens if t in self.indice]
        cobertura = len(reconhecidos) / len(tokens)

        candidatos = set()
        for token in reconhecidos:
            candidatos |= self.indice[token]
        if tema:
            candidatos = {c for c in candidatos if self.registros[c]["tema"] == tema}

        ranking = []
        for cid in candidatos:
            bruto = self.pontuar(cid, tokens)
            final = round(bruto * (0.5 + 0.5 * cobertura), 2)
            ranking.append((final, cid))
        # desempate estável: maior pontuação, depois id em ordem alfabética
        ranking.sort(key=lambda par: (-par[0], par[1]))

        resultados = [{"id": cid, "pontuacao": p} for p, cid in ranking]
        if not ranking or ranking[0][0] < LIMIAR_MINIMO:
            status = "SEM_RESPOSTA"
        elif len(ranking) > 1 and ranking[1][0] >= FATOR_AMBIGUIDADE * ranking[0][0]:
            status = "AMBIGUA"
        else:
            status = "ENCONTRADA"
        return {"status": status, "resultados": resultados[:5], "correcoes": correcoes,
                "cobertura": round(cobertura, 2)}
