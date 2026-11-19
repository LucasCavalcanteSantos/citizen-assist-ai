# Teste de facilidade de uso

## Método

O enunciado permite avaliar a facilidade de uso "com pelo menos um usuário de teste **ou roteiro de tarefas**". Este projeto foi feito individualmente e usou a segunda opção: um **roteiro de 8 tarefas**, executado no sistema real (`python src/sistema.py`), simulando o que um cidadão faria.

Para cada tarefa foram registrados:
- **Concluiu?** O sistema exibiu a resposta correta.
- **Interações:** quantas entradas o usuário precisou digitar (sem contar "voltar" e "sair"). Quanto menos, mais fácil.
- **Observações:** atritos percebidos durante a execução.

> **Limitação:** o roteiro foi executado pelo próprio autor, que conhece os comandos. Uma pessoa sem esse conhecimento provavelmente levaria mais tempo e cometeria mais erros. Por isso o resultado indica que o fluxo **funciona**, mas não mede com precisão a experiência de um usuário leigo.

## Roteiro e resultados

| # | Tarefa | Concluiu? | Interações | Observações |
|---|---|---|---|---|
| 1 | Descobrir se é preciso pagar para tirar o CPF (pergunta livre) | Sim | 2 | Resposta direta, com o valor da taxa em unidades conveniadas e o link da fonte. |
| 2 | Pelo menu, achar a 2ª via do título de eleitor | Sim | 2 | O menu por tema mostra os subtemas em ordem e deixa a navegação clara. |
| 3 | Perguntar onde ver o número do cartão do SUS | Sim | 2 | Encontrou o registro certo (S04), apesar de ser muito parecido com "como obter o cartão" (S03). |
| 4 | Ir para um assunto relacionado a partir da resposta anterior | Sim | 3 | **Atrito:** é preciso digitar o código (ex.: `S03`), não há atalho numérico. |
| 5 | Perguntar algo fora da base ("como renovar minha CNH?") | Sim | 2 | Informou o limite, não inventou e sugeriu os temas disponíveis. |
| 6 | Encontrar a fonte oficial da resposta | Sim | 2 | A linha "🔗 Fonte" aparece sempre na mesma posição, com link e data. |
| 7 | Pergunta genérica: "documento" | Sim | 2 | **Atrito:** a lista de opções mostra só 4 assuntos (D01 a D04); quem procura o título de eleitor (D05/D06) não o vê e precisa reformular. |
| 8 | Digitar uma opção inexistente no menu ("7") | Sim | 1 | Mensagem clara: indica as opções válidas. |

## Indicadores

| Indicador | Valor |
|---|---|
| Taxa de conclusão das tarefas | **8/8 = 100%** |
| Média de interações por tarefa | **2,0** (16 interações ÷ 8 tarefas) |
| Tarefas concluídas em até 2 interações | 7 de 8 (87,5%) |

## Dificuldades observadas

1. **Navegação por código:** para seguir um assunto relacionado é preciso digitar códigos como `S03`. Para quem não está acostumado, números (1, 2, 3) seriam mais naturais.
2. **Número digitado no modo pergunta:** no modo "Fazer uma pergunta", se a pessoa digita `1` achando que é o menu, recebe "não encontrei uma orientação". O sistema deveria lembrar de usar `V` para voltar ao menu.
3. **Lista de ambiguidade cortada:** perguntas genéricas mostram no máximo 4 opções, então parte do tema fica escondida.
4. **Comandos para memorizar:** `P`, `V` e `S` aparecem no menu principal, mas dentro dos modos o usuário precisa lembrar deles.
5. **Aparência no terminal:** links longos quebram a linha em janelas estreitas, e os ícones (📌 🔗 ⚠️) podem aparecer como quadrados em terminais antigos do Windows. O texto ao lado de cada ícone mantém o sentido.

## Melhorias propostas a partir do teste

- Numerar os assuntos relacionados e aceitar `1`, `2`, `3` além do código.
- No modo pergunta, tratar números isolados com a mensagem "Para usar o menu, digite V".
- Mostrar todos os assuntos do tema na lista de ambiguidade, agrupados por subtema.
- Repetir a linha de comandos (`[V] voltar · [S] sair`) ao final de cada resposta.
- Fazer o teste com pelo menos uma pessoa sem conhecimento do sistema, medindo tempo por tarefa.
