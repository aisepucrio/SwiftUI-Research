# Analise qualitativa consolidada do Reddit

## Escopo
- Corpus qualitativo: 60 unidades, sendo 30 posts e 30 comentarios.
- Selecionadas por relevancia/engajamento e diversificacao entre arquiteturas detectadas.
- Analise baseada em codificacao tematica inicial por regras, seguida de consolidacao interpretativa.

## Procedimento
1. Selecionar amostra intencional de posts e comentarios.
2. Aplicar codigos tematicos iniciais.
3. Agrupar os codigos em categorias analiticas.
4. Interpretar frequencias e trechos representativos.

## Distribuicao da amostra
- MVVM: 38 unidades (63,3%)
- TCA: 9 unidades (15,0%)
- MV: 6 unidades (10,0%)
- MVP: 4 unidades (6,7%)
- VIPER: 3 unidades (5,0%)

## Categorias mais recorrentes
- Beneficio percebido: 24 ocorrencias (40,0%)
- Adequacao tecnica: 19 ocorrencias (31,7%)
- Percepcao geral: 18 ocorrencias (30,0%)
- Estrutura arquitetural: 18 ocorrencias (30,0%)
- Custo percebido: 12 ocorrencias (20,0%)
- Adocao e aprendizado: 10 ocorrencias (16,7%)

## Codigos mais recorrentes
- Gestao de estado: 18 ocorrencias (30,0%)
- Avaliacao geral da arquitetura: 18 ocorrencias (30,0%)
- Organizacao de camadas: 18 ocorrencias (30,0%)
- Simplicidade: 12 ocorrencias (20,0%)
- Complexidade excessiva: 11 ocorrencias (18,3%)
- Curva de aprendizado: 10 ocorrencias (16,7%)
- Testabilidade: 10 ocorrencias (16,7%)
- Escalabilidade: 7 ocorrencias (11,7%)

## Achados centrais

### Pragmatismo e simplicidade favorecem MVVM

Evidencias:
- "Hey there, I was tired of the existing (online) image converters. Most are slow, clunky, or have major privacy question marks. So, I decided to build my own from scratch, focusi..." (post / MVVM)
- "After getting my first official job in iOS development with no degree and being self taught I've been repeatedly asked questions like "How do I know I'm ready?", "How do I get o..." (post / MVVM)
### Gestao de estado e navegacao concentram a tensao tecnica

Evidencias:
- "TL;DR: Shipped a SwiftUI app after 9 months. SwiftUI is amazing for iteration speed and simplicity, but watch out for state management complexity and missing UIKit features. Sta..." (post / MVVM)
- "Hi! I built a complete app using only and exclusively SwiftUI and Combine. I'm posting a series of tutorials in which I explain how we can develop *Booklist.* This is a store ap..." (post / MVVM)
### Teste e escala aparecem como justificativa para mais estrutura

Evidencias:
- "I’ve decided to post this here just to counterbalance the current trend of depressing posts about the current job market for iOS devs. First, here is the data: * Total applicati..." (post / MVVM)
- "https://github.com/nalexn/clean-architecture-swiftui/tree/mvvm I learned a lot from it. Key features (copied from that repo readme): * Vanilla SwiftUI + Combine implementation *..." (comment / MVVM)
### Arquiteturas mais sofisticadas cobram custo de adocao

Evidencias:
- "Four months ago i decided to create my next [project](https://apps.apple.com/app/find-xur/id1494638784?ls=1) entirely in SwiftUI. SwiftUI is a really young framework, and I was..." (post / MVVM)
- "# A Word Game in 7 Days - A Developer's Reality Check Hey fellow devs! I just wanted to share my experience of building the game with AI, along with some brutal honesty about in..." (post / MVVM)

## Perfis por arquitetura

### MVVM
- Presenca na amostra: 38 de 60 unidades (63,3%)
- Categoria predominante: Beneficio percebido
- Codigo predominante: Gestao de estado
- Exemplo: "Hey there, I was tired of the existing (online) image converters. Most are slow, clunky, or have major privacy question marks. So, I decided to build my own from scratch, focusi..." (post / MVVM)
### TCA
- Presenca na amostra: 9 de 60 unidades (15,0%)
- Categoria predominante: Percepcao geral
- Codigo predominante: Avaliacao geral da arquitetura
- Exemplo: "Browser Company CEO Josh Miller put out a postmortem blog post today on Arc. In it, he specifically points to sunsetting SwiftUI and TCA as a big performance win in their new br..." (post / TCA)
### MV
- Presenca na amostra: 6 de 60 unidades (10,0%)
- Categoria predominante: Beneficio percebido
- Codigo predominante: Escalabilidade
- Exemplo: "I've been exploring ways to structure SwiftUI apps beyond MVVM, and I came up with **PAG-MV**: **P**rotocols • **A**bstractions • **G**enerics • **M**odel • **V**iew. This appro..." (post / MV)
### MVP
- Presenca na amostra: 4 de 60 unidades (6,7%)
- Categoria predominante: Beneficio percebido
- Codigo predominante: Curva de aprendizado
- Exemplo: "Hi everyone! Last week I launched my first iOS app called 'Rollers'. It's an app that lets you do photoshoots of your your car at any location instantly. https://apps.apple.com/..." (post / MVP)
### VIPER
- Presenca na amostra: 3 de 60 unidades (5,0%)
- Categoria predominante: Adocao e aprendizado
- Codigo predominante: Curva de aprendizado
- Exemplo: "Hey guys, we are 2 developers and develop mobile games. One of us is an iOS Developer (I) and last year I was bored and wanted to try out widgets... so I released an OKR Trackin..." (post / VIPER)

## Sintese interpretativa
- MVVM domina o corpus e aparece associado a simplicidade, organizacao e uso pragmatico.
- TCA tem visibilidade relevante, mas aparece cercado por disputa, defesa tecnica e critica a complexidade.
- Estado, navegacao e separacao de responsabilidades sao o centro da tensao arquitetural em SwiftUI.
- Em projetos maiores, a conversa se desloca para teste, manutenibilidade e escalabilidade.

## O que esta analise permite afirmar
- Nao ha uma arquitetura unica tratada como consenso absoluto.
- A escolha arquitetural e apresentada como equilibrio entre simplicidade, controle de estado e capacidade de escala.
- O ecossistema SwiftUI valoriza solucoes pragmaticas, mas nao elimina a busca por mais estrutura em cenarios complexos.

## Limitacoes
- Codificacao inicial automatizada por regras.
- Amostra qualitativa intencional, nao probabilistica.
- O material e adequado para discussao e apresentacao, mas ainda comporta refinamento manual posterior.