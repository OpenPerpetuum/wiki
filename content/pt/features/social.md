---
title: "Social"
description: "Comunicação e reputação: correio, canais de chat, amigos, reputações (standings), páginas amarelas, notícias e votações."
weight: 140
---

# Social

Esta página aborda comunicação e reputação: **correio (mail)**, **canais de chat**, **amigos**,
**reputações (standings)** e as **páginas amarelas / notícias / votações** públicas.

> Os locais da interface seguem a [visão geral da UI do cliente](/pt/features/ui/) (o botão **Mail** no canto superior esquerdo; o chat e o
> social têm suas próprias janelas). As mecânicas abaixo foram confirmadas com base no servidor.

## Correio (Mail)

**Correio pessoal:**
- **Listar** mensagens, **abrir** uma mensagem, **enviar** mensagem, **excluir** uma mensagem.
- **Contagem de novas** — quantas mensagens não lidas você possui.
- **Pastas** — ver **pastas utilizadas**, **mover** uma mensagem para uma pasta, **excluir** uma pasta.

**Correio em massa (corporação):** enviado para toda a sua corporação:
- **Enviar**, **listar**, **abrir**, **excluir**, **contagem de novas**.

## Canais de chat

**Canais** são salas de chat com nome:

- **Criar** um canal, **entrar** em um, **sair** de um, **falar** nele.
- **Listar** canais (todos ou apenas os seus).
- **Moderação** (como proprietário/oficial do canal): **expulsar (kick)**, **banir (ban)** / **desbanir (unban)**, **definir o papel de um membro**, **silenciamento global (global mute)**, ver membros **silenciados** / **banidos**.
- **Configurações**: **definir uma senha**, **definir um tópico**, preferências de **notificação**.

**Chat direto** — uma mensagem privada entre personagens.

## Amigos

- **Enviar um pedido de amizade**, **responder** a um, **confirmar** um pedido pendente.
- **Remover** um amigo, **bloquear** um personagem.
- **Listar** seus amigos.

Bloquear um personagem impede que ele negocie ou envie mensagens para você (consulte
[primeiros passos](/pt/features/getting-started/) para o bloqueio de comércio por personagem).

## Standings (Reputação)

**Standing** é uma reputação numérica entre entidades (personagens, corporações,
alianças):

- **Listar** suas reputações, ver o **histórico de standing**.
- **Definir standing** — onde permitido, definir um valor de standing. Restrições:
  - o **alvo** deve ser um personagem, uma corporação (privada) ou uma aliança (privada),
  - a **origem** deve ser igualmente uma entidade válida,
  - você não pode definir um standing para si mesmo.
- **Standings padrão** — as reputações base para alianças/corporações padrão.

Standing é um valor de **-10 a +10** (0 = neutro, o padrão; definir 0 limpa a
entrada). A **reputação** de uma entidade é a soma agregada do standing de todos em relação a ela.
O standing positivo é importante em situações concretas — por exemplo, durante uma [intrusão](/pt/features/intrusion/),
uma corporação com standing mútuo ≥ 10 conta como um **aliado** cuja vitória no SAP não
danifica sua estrutura.

O standing afeta como facções e outros jogadores tratam você e sua corporação
(consulte [grupos](/pt/features/groups/)).

## Páginas amarelas

Um diretório público (anúncios gerenciados por corporações):
- **Obter** um anúncio, **enviar** um, **excluir** um, **pesquisar** no diretório.

## Notícias e votações

- **Notícias** — ver **categorias** e a **lista de notícias**; **contagem de novas** para itens não lidos.
- **Votações** — **visualizar** uma votação e **respondê-la**.

## Notas práticas

- **Correio vs. chat** — o correio é persistente e privado; os canais são salas de grupo ao vivo.
- **Correio em massa é uma ferramenta de corporação** — oficiais a utilizam para transmitir mensagens aos membros.
- **Standings são direcionais** — o standing de A com B é separado do de B com A, e
  ele acompanha a sua corporação.
- **O bloqueio é seu escudo** — bloqueie spammers ou negociantes hostis.
- **Canais podem ser trancados** — senhas e permissões controlam quem pode entrar/falar.

<!-- TODO: only the mail/channel/social UI remains.
     Confirmed: standing range [-10,10], clamp in StandingHandler.SetStanding, 0 =
     neutral/clears the row (standings table empty on this deployment); reputation =
     aggregate toward a target (GetReputationFor); mission standing changes clamp to
     [0,10] (missionstandingchange/missionrequiredstanding); ally check = mutual
     standing >= 10 (intrusion).
     Developer notes: Mails/* (list/open/send/delete/folders, mass-mail variants);
     Channels/* (create/join/leave/talk, moderation, password/topic); Socials/* (friend
     request/reply/confirm/delete/block/list); Chat.cs; Standings/SetStanding.cs
     (entity-category + private-corp/alliance constraints, self-excluded),
     StandingHistory.cs, GetStandingForDefault*.cs; Corporations/YellowPages/*;
     GetNews.cs / NewsCategory.cs / FreshNewsCount.cs; PollGet.cs / PollAnswer.cs. -->