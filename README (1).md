# FIAP - Faculdade de Informática e Administração Paulista

# Citizen Assist AI: assistente de orientação cidadã

**Global Solution 2026.2 · Desafio CitizenTech**

## Nome do grupo

Trabalho individual

## 👨‍🎓 Integrante

| Nome | RM |
|---|---|
| Lucas Davi | RM98799 |

## 👩‍🏫 Professores

### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

---

## 📜 1. Problema, público e temas

**Problema:** informações sobre documentos, serviços e direitos estão espalhadas em vários portais, usam termos técnicos e mudam com o tempo. O cidadão perde tempo, se confunde ou recorre a intermediários que cobram por serviços gratuitos.

**Público beneficiado:** pessoas que precisam de uma primeira orientação sobre serviços públicos comuns, especialmente quem tem pouca familiaridade com portais governamentais.

**Solução:** um assistente em modo texto que recebe uma pergunta ou a escolha de um tema, encontra a orientação correspondente em uma base verificada, mostra a **fonte oficial com link e data de verificação** e **avisa quando não sabe** em vez de inventar.

**Temas abordados (18 orientações):**

| Tema | Subtemas | Registros |
|---|---|---|
| Documentação | Carteira de Identidade Nacional, CPF, título de eleitor | D01 a D06 |
| Serviços sociais, saúde e previdência | Cadastro Único, Cartão SUS, INSS, conta gov.br | S01 a S06 |
| Direitos e orientações comunitárias | Disque 100, Ligue 180, emergência, Consumidor.gov.br, Anatel, Fala.BR | C01 a C06 |

## 📁 2. Estrutura de pastas

```text
citizen-assist-ai/
├── data/
│   ├── base_conhecimento.json   # temas + 18 orientações verificadas
│   ├── perguntas_teste.json     # 18 perguntas (usadas na calibração)
│   └── perguntas_validacao.json # 12 perguntas (NÃO usadas na calibração)
├── docs/
│   ├── prompts.md               # modelos de instrução A e B + comparação
│   ├── resultados_testes.md     # indicadores (gerado automaticamente)
│   ├── resultados_testes.csv    # registro linha a linha (gerado automaticamente)
│   ├── teste_usabilidade.md     # roteiro e registro do teste com usuário
│   └── uso_ia.md                # uso de IA e validação crítica
├── src/
│   ├── sistema.py               # ponto de entrada (interface textual)
│   ├── assistente.py            # fluxo de consulta, navegação e privacidade
│   ├── base.py                  # leitura e validação do JSON
│   ├── busca.py                 # algoritmo de busca e decisão
│   ├── respostas.py             # modelos de resposta A e B e mensagens de limite
│   └── avaliacao.py             # testes automatizados e indicadores
└── README.md
```

## 🗂️ 3. Base de conhecimento, estruturas e estratégia de busca

### 3.1 Organização da base

Arquivo único `data/base_conhecimento.json` com duas seções:

- **`temas`**: dicionário com nome, descrição, subtemas e temas relacionados.
- **`orientacoes`**: lista de registros com os campos abaixo.

| Campo | Obrigatório | Descrição |
|---|---|---|
| `id` | ✅ | Código único (D = documentos, S = serviços, C = comunidade/direitos) |
| `tema` | ✅ | Chave de um tema existente |
| `subtema` | | Agrupamento dentro do tema |
| `titulo` | ✅ | Nome curto do assunto |
| `palavras_chave` | ✅ | Lista de termos e frases usados na busca |
| `perguntas_exemplo` | | Formas comuns de perguntar (reforçam a busca) |
| `orientacao` | ✅ | Resumo da orientação, escrito a partir da fonte |
| `referencia.fonte` / `referencia.url` | ✅ | Fonte identificável com link `https://` |
| `data_verificacao` | ✅ | Data em que a fonte foi conferida (AAAA-MM-DD) |
| `requer_confirmacao` | | Se `true`, a resposta exibe aviso para confirmar requisitos atualizados |
| `relacionados` | | IDs de outros registros (arestas do grafo de navegação) |

**Origem das orientações:** todas foram resumidas de páginas de órgãos oficiais (gov.br, Receita Federal, TSE, Ministério da Saúde, MDHC, Ministério das Mulheres, Ministério da Justiça, Anatel, Serpro, Agência Gov). O texto foi reescrito em linguagem simples, sem acrescentar informação que não está na fonte.

**Validação ao carregar (`src/base.py`):** arquivo ausente, vazio ou com JSON malformado interrompe o programa com mensagem clara. Registros com campo obrigatório faltando, tema inexistente, ID duplicado, URL sem `https://` ou data fora do formato são **ignorados com aviso**, e o resto da base continua funcionando. Relacionados que apontam para IDs inexistentes são removidos.

**Manutenção:** para acrescentar ou corrigir uma orientação, basta editar o JSON. Nenhuma regra do programa precisa mudar: o índice de busca, os menus e o grafo são reconstruídos a partir do arquivo a cada execução.

### 3.2 Estruturas de dados

| Estrutura | Tipo Python | Uso |
|---|---|---|
| Registros | `list[dict]` | Base carregada |
| Índice por ID | `dict[id → registro]` | Recuperação direta em O(1) e atalho "digite D01" |
| Árvore de temas | `dict[tema → dict[subtema → list]]` | Menu hierárquico |
| Índice invertido | `dict[token → set(ids)]` | Encontrar candidatos sem percorrer toda a base |
| Grafo de assuntos | lista `relacionados` em cada registro | Sugerir continuidade (ex.: D03 → D04, S06) |
| Grafo de temas | lista `relacionados` em cada tema | Documentação ↔ Serviços ↔ Direitos |

**Relações do grafo:** dois assuntos são ligados quando um é pré-requisito ou passo seguinte do outro. Exemplos: o CPF (D03) é necessário para a conta gov.br (S06), que dá acesso ao Meu INSS (S05) e ao Meu SUS Digital (S03); a reclamação no Consumidor.gov.br (C03) se liga à Anatel (C04) e à ouvidoria Fala.BR (C06); o Ligue 180 (C02) se liga à emergência 190 (C05) e ao Disque 100 (C01).

### 3.3 Estratégia de busca (`src/busca.py`)

1. **Normalização:** minúsculas, sem acentos e sem pontuação ("Cartão" = "cartao").
2. **Tokenização:** remoção de palavras vazias ("como", "o", "meu"…) e redução simples de plural.
3. **Sinônimos:** termos populares viram o termo da base (`rg → identidade`, `loja → empresa`, `cadunico → cadastro unico`).
4. **Correção de digitação:** palavra desconhecida é aproximada do vocabulário da base com `difflib` (similaridade ≥ 0,8), por exemplo `identidadi → identidade`.
5. **Candidatos:** o índice invertido devolve só os registros que têm pelo menos um termo da pergunta.
6. **Pontuação ponderada:**
   - +3 por frase-chave inteira encontrada (ex.: "titulo eleitor")
   - +2 por termo presente nas palavras-chave
   - +1 por termo presente no título
   - +1 por termo presente nas perguntas de exemplo
   - multiplicada por `0,5 + 0,5 × cobertura`, em que cobertura = fração dos termos da pergunta reconhecidos pela base. Isso penaliza perguntas com muitos termos fora do tema.
7. **Decisão:**

| Situação | Resultado |
|---|---|
| Pergunta vazia ou só com palavras vazias | `ENTRADA_INVALIDA`: pede uma pergunta |
| Só palavras genéricas de tema ("documento", "saúde") | `AMBIGUA`: lista os assuntos do tema |
| Melhor pontuação < 3,0 | `SEM_RESPOSTA`: informa o limite e sugere temas |
| 2º colocado ≥ 90% da pontuação do 1º | `AMBIGUA`: mostra as opções e pede o código |
| Caso contrário | `ENCONTRADA`: mostra a orientação do 1º colocado |

**Várias correspondências:** o ranking é ordenado por pontuação (desempate por ID). Se a diferença entre os dois primeiros for grande, o assistente responde com o primeiro e mostra os relacionados; se for pequena, ele **não escolhe sozinho** e pede que o usuário decida.

**Busca dentro de um tema:** ao navegar pelo menu, a busca é restrita ao tema escolhido; se nada for encontrado ali, o sistema tenta na base inteira.

## 💬 4. Regras de resposta, prompts e limitações

As regras e os dois modelos estão detalhados em [`docs/prompts.md`](docs/prompts.md).

- **Modelo A (resposta direta):** texto da orientação + nome da fonte.
- **Modelo B (estruturado, adotado):** papel de assistente não oficial; formato fixo com título, frases curtas, fonte com link e data, aviso de confirmação e assuntos relacionados; proibido inventar passos ou se apresentar como canal oficial.

Na comparação automática sobre 23 respostas, o **Modelo B obteve 114/115 pontos e o A, 32/115**. O B é mais longo, mas é o único que permite conferir a fonte e deixa claros os limites da informação.

**Tratamento de limitações:**

| Caso | Comportamento |
|---|---|
| Entrada vazia | "Não recebi nenhuma pergunta. Digite sua dúvida ou escolha um número do menu." |
| Opção de menu inexistente | "Opção 9 não existe. Escolha entre 1 e 3, P ou S." |
| Pergunta fora da base | Informa que não há orientação confiável, não inventa e lista os temas disponíveis |
| Pergunta ambígua | Lista as opções com código para o usuário escolher |
| Orientação que pode mudar | Aviso: "Requisitos, prazos e valores podem mudar. Confirme…" |
| Usuário digita CPF, e-mail ou telefone | Avisa que o dado não é necessário, remove-o da consulta e não grava nada |

## 🧪 5. Plano de testes, indicadores e resultados

### Plano

- **Conjunto de teste** (`data/perguntas_teste.json`, 18 perguntas): diretas, reformulações, erro de digitação, entrada vazia, consulta ambígua e duas perguntas fora do tema. **Foi usado para calibrar** o limiar e o fator de ambiguidade.
- **Conjunto de validação** (`data/perguntas_validacao.json`, 12 perguntas): escrito antes da versão final e **não usado para calibrar**. Mede como o assistente lida com perguntas novas.
- Cada pergunta é executada 5 vezes; o tempo registrado é a média (`time.perf_counter`).
- **Acerto** = resposta obtida igual à esperada (ID do registro, ou `ENTRADA_INVALIDA`, `AMBIGUA` ou `SEM_RESPOSTA`).
- **Usabilidade:** roteiro de 8 tarefas executado no sistema real, documentado em [`docs/teste_usabilidade.md`](docs/teste_usabilidade.md).

### Resultados

Gerados por `python src/avaliacao.py` (detalhes em [`docs/resultados_testes.md`](docs/resultados_testes.md)):

| Conjunto | Perguntas | Acertos | Taxa de acerto | Tempo médio |
|---|---|---|---|---|
| Teste (calibração) | 18 | 18 | **100,0%** | ~0,13 ms |
| Validação (não calibrado) | 12 | 10 | **83,3%** | ~0,22 ms |
| Geral | 30 | 28 | **93,3%** | ~0,16 ms |

*Os tempos variam conforme o computador; os valores acima são de uma execução de referência.*

**Rodada 1 (antes da calibração):** 15/18 no conjunto de teste (83,3%). As falhas e as correções estão registradas em [`docs/uso_ia.md`](docs/uso_ia.md).

**Usabilidade (roteiro de 8 tarefas):** 8/8 tarefas concluídas (100%), com média de 2,0 interações por tarefa. Principais dificuldades: navegação por códigos (ex.: S03), número digitado no modo pergunta e lista de opções cortada em perguntas genéricas. Detalhes em [`docs/teste_usabilidade.md`](docs/teste_usabilidade.md).

### Interpretação

- A taxa de **100% no conjunto de teste é otimista**, porque o limiar foi ajustado olhando para essas perguntas. O número mais honesto é o da **validação (83,3%)**.
- Todos os casos de limitação (vazio, ambíguo, fora do tema, dado pessoal) foram tratados corretamente: **o assistente não inventou nenhuma resposta** para perguntas fora da base.
- As duas falhas de validação mostram limites reais do método por palavras:
  - **V03 "app do titulo de eleitor"** → respondeu D05 (primeiro título) em vez de D06 (e-Título). A palavra "app" não estava nas palavras-chave de D06.
  - **V05 "como pedir aposentadoria"** → a correção de digitação trocou "pedir" por "perdi" e levou a D06. A correção automática pode gerar falsos positivos.
- O tempo de consulta fica abaixo de 1 ms, porque a busca usa índice invertido e a base é pequena; não é um gargalo.

## ▶️ 6. Como executar

**Pré-requisito:** Python 3.8 ou superior. Não há bibliotecas externas: apenas a biblioteca padrão (`json`, `re`, `difflib`, `unicodedata`, `statistics`, `csv`, `time`).

```bash
# 1. Clonar o repositório
git clone https://github.com/LucasCavalcanteSantos/citizen-assist-ai.git
cd citizen-assist-ai

# 2. Rodar o assistente (modo interativo)
python src/sistema.py

# 3. Rodar os testes e gerar os indicadores
python src/sistema.py --avaliar
#    ou
python src/avaliacao.py
```

No Linux/macOS, use `python3` se `python` não estiver disponível.

**Uso do menu:** digite `1`, `2` ou `3` para navegar por tema, `P` para perguntar com suas palavras, um código como `D03` para abrir um assunto direto, `V` para voltar e `S` para sair. Texto livre digitado direto no menu também é aceito como pergunta.

## 💡 7. Exemplos

**Pergunta direta**

```text
pergunta> Precisa pagar para fazer o CPF?

📌 Inscrição no CPF

 • A inscrição no CPF é gratuita pelo serviço 'Inscrever no CPF' no portal
   gov.br.
 • Em unidades conveniadas é cobrada uma taxa de R$ 7,00.
 • Não são necessários intermediários: desconfie de quem cobra para fazer o
   cadastro.

🔗 Fonte: gov.br – Inscrever no CPF (Receita Federal)
   https://www.gov.br/pt-br/servicos/inscrever-no-cpf
   Verificado em: 2026-11-19

⚠️  Requisitos, prazos e valores podem mudar. Confirme a informação atualizada na fonte antes de ir ao atendimento.

➡️  Assuntos relacionados:
   [D04] Consultar ou regularizar a situação do CPF
   [S06] Conta gov.br
```

**Erro de digitação**

```text
pergunta> como tirar identidadi nova
(Entendi 'identidadi' → 'identidade')

📌 Como emitir a Carteira de Identidade Nacional (CIN)
...
```

**Consulta ambígua**

```text
pergunta> documento
Sua pergunta pode se referir a mais de um assunto. Qual deles?
   [D01] Como emitir a Carteira de Identidade Nacional (CIN)
   [D02] CIN digital no aplicativo gov.br
   [D03] Inscrição no CPF
   [D04] Consultar ou regularizar a situação do CPF
Digite o código (ex.: D01) ou reformule a pergunta.
```

**Fora do tema**

```text
pergunta> como abrir uma empresa MEI?
Não encontrei uma orientação confiável sobre isso na minha base, então prefiro não arriscar uma resposta.
Posso ajudar com: Documentação, Serviços sociais, saúde e previdência, Direitos e orientações comunitárias.
Dica: tente usar palavras como 'CPF', 'identidade', 'cartão SUS', 'INSS' ou 'reclamação'. Para outros assuntos, procure o portal gov.br ou o órgão responsável.
```

**Entrada vazia / opção inexistente / dado pessoal**

```text
menu>
Não recebi nenhuma pergunta. Digite sua dúvida ou escolha um número do menu.

menu> 9
Opção 9 não existe. Escolha entre 1 e 3, P ou S.

pergunta> meu email é a@b.com, como faço o cartao sus
🔒 Você não precisa informar e-mail para usar o assistente. Esse dado foi ignorado e não foi salvo.
📌 Como obter o Cartão Nacional de Saúde (Cartão SUS)
...
```

## ♿ 8. Clareza, acessibilidade, privacidade e informação não oficial

- **Clareza:** orientações reescritas em frases curtas, uma ideia por linha, sem jargão; termos populares (RG, Cadúnico) são reconhecidos.
- **Acessibilidade:** interface só em texto, compatível com leitores de tela; seções sempre na mesma ordem; navegação por número **ou** por linguagem natural; tolerância a acentos e erros de digitação. Ícones são complementares; o texto ao lado de cada um já explica a seção.
- **Privacidade:** o sistema não pede nenhum dado pessoal, detecta e remove CPF, e-mail e telefone digitados por engano e não grava histórico de consultas.
- **Informação não oficial:** aviso fixo na abertura e no encerramento; cada resposta traz a fonte oficial com link e data; o sistema não promete atendimento, agendamento nem integração com órgãos públicos.

## 🧠 9. Decisões técnicas

- **JSON** em vez de CSV: permite listas (palavras-chave, relacionados) e objetos aninhados (referência) sem gambiarras.
- **Busca por regras em vez de LLM:** garante que toda resposta venha de conteúdo verificado e torna o comportamento explicável e testável. Os prompts estão prontos caso a equipe queira acoplar um modelo no futuro.
- **Somente biblioteca padrão:** roda em qualquer máquina com Python, sem instalação.
- **Módulos separados:** a interface (`sistema.py`) e os testes (`avaliacao.py`) usam o mesmo núcleo (`assistente.py`), então os testes medem exatamente o que o usuário vê.

### 📢 Observações gerais

- **Participação na Competição:** Não vamos participar.

## 🏁 10. Conclusões, limitações e melhorias

**Conclusões:** o protótipo cumpre o fluxo completo (pergunta → validação → busca → orientação com fonte → continuidade) e trata entradas vazias, ambíguas, fora do tema e com dados pessoais. A taxa de acerto em perguntas novas foi de 83,3%, sem nenhuma resposta inventada.

**Limitações:**

- A busca é **léxica**: depende de as palavras do usuário (ou seus sinônimos) estarem na base. Perguntas com sentido parecido e palavras diferentes podem falhar (caso V03).
- A correção de digitação pode trocar uma palavra válida por outra parecida (caso V05).
- A base é pequena (18 registros) e de abrangência federal; regras estaduais e municipais (ex.: agendamento da CIN em cada estado) não estão cobertas.
- As orientações envelhecem: dependem de reverificação periódica das fontes.
- A avaliação usa perguntas escritas pela própria equipe, o que tende a favorecer o sistema; o teste de usabilidade tem amostra mínima.

**Melhorias possíveis:**

1. **Busca semântica:** usar TF-IDF ou embeddings para comparar o sentido da pergunta, mantendo o limiar de confiança e a resposta sempre vinda da base.
2. **Correção de digitação mais segura:** só corrigir palavras que não existem no português comum (com um dicionário) e pedir confirmação ("Você quis dizer…?").
3. **Ampliar sinônimos e palavras-chave** a partir das perguntas que caírem em `SEM_RESPOSTA` durante o uso real.
4. **Rotina de reverificação:** script que lista registros com `data_verificacao` antiga e testa se os links ainda respondem.
5. **Avaliação com mais usuários** e perguntas coletadas de pessoas de fora da equipe.

---

## 📋 Licença

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
