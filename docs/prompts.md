# Modelos de prompt / instrução de resposta

O protótipo não usa API paga. Os dois modelos abaixo são **instruções de resposta** implementadas por regras em `src/respostas.py`. O texto de cada modelo também pode ser usado, sem alteração, como *system prompt* de um LLM caso a equipe queira evoluir o projeto. Nesse caso, a resposta do modelo continua precisando ser conferida contra a base verificada.

Em ambos os modelos, **a busca é a mesma**: o modelo só muda a forma de apresentar o registro encontrado. Por isso a taxa de acerto é igual nos dois, e a comparação é feita sobre **clareza, consistência e transparência**.

---

## Modelo A: "Resposta direta"

```text
Responda à pergunta do usuário usando o texto da orientação encontrada.
Inclua o nome da fonte no final.
```

**Implementação:** devolve `orientacao + (Fonte: nome)` em um único parágrafo.

---

## Modelo B: "Assistente cidadão estruturado" (modelo adotado)

```text
PAPEL
Você é o Citizen Assist AI, um assistente INFORMATIVO e NÃO OFICIAL que ajuda
cidadãos a encontrar orientações sobre documentos, serviços e direitos.

REGRAS
1. Use SOMENTE o conteúdo da orientação recuperada da base. Não acrescente
   passos, prazos, valores ou documentos que não estejam nela.
2. Sempre cite a fonte: nome, link e data de verificação.
3. Se a orientação estiver marcada como "requer_confirmacao", exiba o aviso
   para confirmar requisitos atualizados.
4. Nunca diga que é um canal oficial nem que realiza atendimento/agendamento.
5. Não peça dados pessoais (CPF, telefone, e-mail, endereço).
6. Se não houver orientação suficiente, diga isso claramente, não invente,
   e sugira os temas disponíveis.
7. Se a pergunta puder ter mais de um sentido, liste as opções e peça que o
   usuário escolha.

FORMATO
📌 <título do assunto>
 • <frase curta 1>
 • <frase curta 2> ...
🔗 Fonte: <nome> / <url> / Verificado em: <data>
⚠️  <aviso de confirmação, quando aplicável>
➡️  Assuntos relacionados: [<id>] <título> ...
```

---

## Comparação

Executada por `python src/avaliacao.py` sobre todas as respostas encontradas nos dois conjuntos de perguntas. Resultado completo em [`resultados_testes.md`](resultados_testes.md).

| Critério | Modelo A | Modelo B |
|---|---|---|
| Cita a fonte com link verificável | 0/23 | 23/23 |
| Mostra a data de verificação | 0/23 | 23/23 |
| Exibe aviso quando a orientação exige confirmação | 9/23 | 23/23 |
| Sugere assuntos relacionados (continuidade) | 0/23 | 23/23 |
| Frases com até 25 palavras em média | 23/23 | 22/23 |
| **Total** | **32/115** | **114/115** |

**Justificativa da escolha do Modelo B:**

- **Comprovação da fonte:** o A cita só o nome da fonte; o B traz link e data, então o usuário consegue conferir.
- **Responsabilidade:** o A só "acerta" o aviso quando a orientação não exige confirmação (9 casos), porque nunca o exibe. O B exibe o aviso sempre que necessário.
- **Consistência:** o B tem sempre as mesmas seções na mesma ordem, o que facilita a leitura e o uso com leitor de tela.
- **Navegação:** o B oferece continuidade (assuntos relacionados), atendendo ao requisito de navegação entre assuntos.
- **Ponto fraco do B:** em um caso, a média de palavras por frase passou de 25, porque a linha do link é longa. O A é mais curto, mas perde justamente o que o desafio prioriza: fonte e limites.
