---
title: "Servidor e referência"
description: "Informações do servidor, pontuações máximas, download de dados de referência e a loja do jogo."
weight: 170
---

# Servidor e referência

Esta página aborda os sistemas "meta": informações do servidor/sistema, pontuações máximas (high scores), os dados de referência que o cliente baixa e a loja do jogo.

> As localizações na interface seguem a [visão geral da interface do cliente](/pt/features/ui/). As mecânicas abaixo foram confirmadas em relação ao servidor.

## Informações do servidor e do sistema

- **Informações do servidor** — estado/informações gerais do servidor.
- **Informações do sistema** — detalhes em nível de sistema.
- **Estado de encerramento do servidor** — indica se há um desligamento programado em vigor (somente leitura para os jogadores; o encerramento em si é uma ação de administrador).

## Pontuações máximas

- **Pontuações máximas do servidor** — os melhores resultados de todo o servidor.
- **Minhas pontuações máximas** — seus recordes pessoais.

Consulte também [combate](/pt/features/combat/) para ver como as eliminações alimentam esses registros.

## Dados de referência

O cliente baixa dados de referência estáticos do servidor para renderizar o conteúdo corretamente. Estas são **consultas somente leitura**, não ações do jogador:

- **Efeitos** — as definições de efeitos.
- **Enumerações** — valores de enumeração.
- **Padrões de entidade** — definições base para entidades.
- **Campos agregados** — dados de campos agregados.
- **Unidades de configuração de definição** — configuração por definição.
- **Distâncias** — constantes de distância utilizadas pelo cliente.
- **Comandos** — a lista de comandos conhecidos (uma referência do lado do cliente).
- **Fendas (Rifts)** — definições de fendas (consulte também a lista de fendas da zona).

Você não "usa" esses dados diretamente; o cliente os obtém sob demanda. Eles estão listados aqui porque constam no inventário de comandos.

## A loja

A loja do jogo (uma integração de pagamentos):

- **Listar produtos** — ver o que está à venda.
- **Iniciar uma transação** — iniciar uma compra.
- **Concluir uma transação** — finalizar uma compra.

As compras na loja são transações com dinheiro real (ou equivalente); os produtos exatos e os preços fazem parte do conteúdo da loja.

## Notas práticas

- **Os dados de referência são obtidos automaticamente** — você nunca precisa acioná-los manualmente; eles mantêm o cliente sincronizado com o conteúdo do servidor.
- **As pontuações máximas são o seu orgulho** — confira seus recordes pessoais e os do servidor.
- **As transações da loja têm duas etapas** — iniciar e depois concluir; não presuma que uma compra foi realizada até que seja finalizada.
- **O estado de encerramento é informativo** — ele avisa se uma janela de manutenção está próxima.

<!-- TODO: only the reference-data payload list (client-side) remains.
     Confirmed: the real-money store is NOT active on this deployment — the Steam
     transaction commands (steamGetProducts / steamStartTransaction /
     steamFinishTransaction) are declared in Commands.cs but no handler is registered
     in the bootstrapper, and the store content tables (storeitems, storecategories)
     are empty.
     Developer notes: ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs;
     GetHighScores.cs / GetMyHighScores.cs; GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs; SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs. -->