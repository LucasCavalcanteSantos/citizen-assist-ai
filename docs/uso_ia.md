# Uso de Inteligência Artificial no projeto

## Onde a IA foi usada

| Etapa | Ferramenta | Como foi usada |
|---|---|---|
| Planejamento da estrutura do código e da base | Claude (Anthropic) | Sugestão da divisão em módulos (`base`, `busca`, `respostas`, `assistente`, `avaliacao`) e do formato JSON. |
| Levantamento de fontes | Claude com busca na web | Localização de páginas oficiais (gov.br, TSE, Ministérios, Anatel) para cada orientação. |
| Redação inicial dos modelos de prompt A e B | Claude | Primeira versão dos textos em `docs/prompts.md`. |
| Planejamento dos testes | Claude | Sugestão de separar conjunto de **teste** (usado na calibração) e conjunto de **validação** (não usado na calibração). |
| Revisão de textos | Claude | Revisão de clareza do README e das mensagens do sistema. |

**O protótipo em si não chama nenhum modelo de IA.** Todas as respostas vêm da base verificada em `data/base_conhecimento.json`, selecionadas por regras e pelo algoritmo de busca documentado.

## Validação crítica realizada pela equipe

> Ajustem esta seção para refletir o que a equipe realmente conferiu.

- [ ] Cada link da base foi aberto manualmente e o conteúdo resumido confere com a página oficial (preencher a data real em `data_verificacao`).
- [ ] Nenhuma orientação contém passos, valores ou prazos que não estejam na fonte.
- [ ] O código foi lido e executado pela equipe; cada integrante consegue explicar a pontuação da busca e os limiares.
- [ ] Os testes foram reexecutados (`python src/avaliacao.py`) e os números do README conferem com `docs/resultados_testes.md`.
- [ ] O teste de usabilidade foi feito com uma pessoa real (não simulado por IA).

## Correções feitas sobre sugestões da IA

- Na primeira rodada de testes, 3 das 18 perguntas falharam: uma palavra genérica ("documento") não era tratada como ambígua, uma pergunta fora do tema ("abrir empresa MEI") passava do limiar mínimo e "número do cartão SUS" empatava com "como obter o cartão SUS". A equipe ajustou o limiar (2,0 → 3,0), o fator de ambiguidade (0,85 → 0,90) e criou a regra de palavras genéricas de tema.
- Para não mascarar o desempenho com esses ajustes, foi criado um conjunto de validação separado, escrito antes de rodar a versão ajustada e não usado para calibrar. As 2 falhas desse conjunto foram mantidas e documentadas.

## Riscos considerados

- **Alucinação:** evitada porque o sistema só exibe texto da base; perguntas sem correspondência recebem mensagem de limite.
- **Informação desatualizada:** cada registro tem data de verificação e aviso de confirmação.
- **Aparência de canal oficial:** aviso fixo no início e na mensagem de saída.
- **Privacidade:** o sistema não pede dados pessoais, detecta CPF/e-mail/telefone digitados, remove esses dados da consulta e não grava histórico.
