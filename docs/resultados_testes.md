# Resultados dos testes – Citizen Assist AI

> Arquivo gerado automaticamente por `python src/avaliacao.py`. Não edite à mão.

## Indicadores

| Conjunto | Perguntas | Acertos | Taxa de acerto | Tempo médio (ms) | Mediana (ms) | Máximo (ms) |
|---|---|---|---|---|---|---|
| teste | 18 | 18 | 100.0% | 0.132 | 0.092 | 0.510 |
| validacao | 12 | 10 | 83.3% | 0.214 | 0.245 | 0.398 |
| geral | 30 | 28 | 93.3% | 0.165 | 0.109 | 0.510 |

## Acerto por tipo de pergunta

| Tipo | Acertos / Total |
|---|---|
| direta | 6 / 6 |
| erro_digitacao | 1 / 1 |
| fora_do_tema | 4 / 4 |
| limitacao | 3 / 3 |
| privacidade | 1 / 1 |
| reformulacao | 13 / 15 |

## Registro detalhado

| Conjunto | ID | Tipo | Pergunta | Esperado | Obtido | Resultado | Tempo (ms) |
|---|---|---|---|---|---|---|---|
| teste | T01 | direta | Como tiro a nova carteira de identidade? | D01 | D01 | ACERTO | 0.135 |
| teste | T02 | reformulacao | quero fazer meu RG novo | D01 | D01 | ACERTO | 0.086 |
| teste | T03 | direta | Precisa pagar para fazer o CPF? | D03 | D03 | ACERTO | 0.090 |
| teste | T04 | reformulacao | como colocar a identidade no celular | D02 | D02 | ACERTO | 0.252 |
| teste | T05 | direta | Como tirar o primeiro título de eleitor? | D05 | D05 | ACERTO | 0.102 |
| teste | T06 | reformulacao | perdi meu titulo, como imprimo outro? | D06 | D06 | ACERTO | 0.084 |
| teste | T07 | direta | Como me inscrever no Cadastro Único? | S01 | S01 | ACERTO | 0.114 |
| teste | T08 | reformulacao | onde vejo o numero do meu cartao do sus | S04 | S04 | ACERTO | 0.084 |
| teste | T09 | direta | Qual o telefone do INSS? | S05 | S05 | ACERTO | 0.097 |
| teste | T10 | direta | Como denunciar violação de direitos humanos? | C01 | C01 | ACERTO | 0.088 |
| teste | T11 | reformulacao | a loja não resolveu meu problema com uma compra | C03 | C03 | ACERTO | 0.095 |
| teste | T12 | reformulacao | minha operadora de internet está cobrando errado | C04 | C04 | ACERTO | 0.079 |
| teste | T13 | reformulacao | mudei de endereço, preciso atualizar o cadunico | S02 | S02 | ACERTO | 0.087 |
| teste | T14 | erro_digitacao | como tirar identidadi nova | D01 | D01 | ACERTO | 0.298 |
| teste | T15 | limitacao | (vazia) | ENTRADA_INVALIDA | ENTRADA_INVALIDA | ACERTO | 0.002 |
| teste | T16 | limitacao | documento | AMBIGUA | AMBIGUA | ACERTO | 0.016 |
| teste | T17 | fora_do_tema | qual a previsão do tempo para amanhã? | SEM_RESPOSTA | SEM_RESPOSTA | ACERTO | 0.510 |
| teste | T18 | fora_do_tema | como abrir uma empresa MEI? | SEM_RESPOSTA | SEM_RESPOSTA | ACERTO | 0.158 |
| validacao | V01 | reformulacao | a identidade nova é de graça? | D01 | D01 | ACERTO | 0.232 |
| validacao | V02 | reformulacao | meu cpf está irregular | D04 | D04 | ACERTO | 0.104 |
| validacao | V03 | reformulacao | app do titulo de eleitor | D06 | D05 | ERRO | 0.096 |
| validacao | V04 | reformulacao | quero receber bolsa familia, onde vou? | S01 | S01 | ACERTO | 0.259 |
| validacao | V05 | reformulacao | como pedir aposentadoria | S05 | D06 | ERRO | 0.228 |
| validacao | V06 | reformulacao | esqueci a senha do gov.br | S06 | S06 | ACERTO | 0.264 |
| validacao | V07 | reformulacao | vizinho maltrata idoso, como denunciar | C01 | C01 | ACERTO | 0.398 |
| validacao | V08 | reformulacao | quero reclamar de um órgão do governo | C06 | C06 | ACERTO | 0.195 |
| validacao | V09 | limitacao | saude | AMBIGUA | AMBIGUA | ACERTO | 0.009 |
| validacao | V10 | fora_do_tema | como renovar minha CNH? | SEM_RESPOSTA | SEM_RESPOSTA | ACERTO | 0.261 |
| validacao | V11 | fora_do_tema | receita de bolo de cenoura | SEM_RESPOSTA | SEM_RESPOSTA | ACERTO | 0.260 |
| validacao | V12 | privacidade | meu cpf é 123.456.789-09, ele está suspenso? | D04 | D04 | ACERTO | 0.260 |

## Comparação dos modelos de instrução (A x B)

Critérios verificados automaticamente em 23 respostas encontradas.

| Critério | Modelo A | Modelo B |
|---|---|---|
| Cita a fonte com link verificável | 0/23 | 23/23 |
| Mostra a data de verificação | 0/23 | 23/23 |
| Exibe aviso quando a orientação exige confirmação | 9/23 | 23/23 |
| Sugere assuntos relacionados (continuidade) | 0/23 | 23/23 |
| Frases com até 25 palavras em média (clareza) | 23/23 | 22/23 |
| **Total** | **32/115** | **114/115** |

### Exemplo de saída – Modelo A

```
A CIN substitui o antigo RG e usa o número do CPF como identificador. Acesse gov.br/identidade, escolha o seu estado e agende o atendimento para coleta da biometria. No dia, leve a certidão de nascimento ou de casamento original. A primeira via é gratuita. (Fonte: Agência Gov / Ministério da Gestão e da Inovação – emissão da nova CIN)
```

### Exemplo de saída – Modelo B

```
📌 Como emitir a Carteira de Identidade Nacional (CIN)

 • A CIN substitui o antigo RG e usa o número do CPF como identificador.
 • Acesse gov.br/identidade, escolha o seu estado e agende o atendimento para
   coleta da biometria.
 • No dia, leve a certidão de nascimento ou de casamento original.
 • A primeira via é gratuita.

🔗 Fonte: Agência Gov / Ministério da Gestão e da Inovação – emissão da nova CIN
   https://agenciagov.ebc.com.br/noticias/202605/semana-do-trabalhador-e-da-trabalhadora-aproxima-estado-da-populacao-com-emissao-da-nova-cin
   Verificado em: 2026-11-19

⚠️  Requisitos, prazos e valores podem mudar. Confirme a informação atualizada na fonte antes de ir ao atendimento.

➡️  Assuntos relacionados:
   [D02] CIN digital no aplicativo gov.br
   [D03] Inscrição no CPF
```
