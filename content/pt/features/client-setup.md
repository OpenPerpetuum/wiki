---
title: "Configuração do cliente e do PC"
description: "Executando o cliente no Windows e Linux, multi-boxing dentro das regras, dimensionamento de interface (UI) e inicialização sem privilégios de administrador."
weight: 24
---

# Configuração do cliente e do PC

Notas práticas para executar o cliente do Perpetuum.

## As regras primeiro

O multi-boxing (vários clientes controlando múltiplos personagens) é permitido
**dentro de limites**. Regras de fair play que você deve conhecer antes de fazê-lo:

- **Nenhum software de automação ou de controle de múltiplos clientes** — em hipótese alguma.
- **No máximo 5 contas ativas simultaneamente.**
- Nenhuma conta registrada com endereços de e-mail falsos, inválidos ou inacessíveis —
  o endereço deve ser de sua propriedade.

Violações podem resultar em banimento imediato e permanente.

## Windows: múltiplos clientes

1. Instale o cliente Steam do Perpetuum.
2. Verifique se a pasta do jogo contém um arquivo `steam_appid.txt` com o conteúdo
   `223410`.
3. Copie toda a pasta `Perpetuum` uma vez para cada cliente adicional.
4. Execute o `Perpetuum.exe` em cada cópia (opcionalmente, adicione as cópias à Steam como
   jogos que não são da Steam).

**Espaço em disco:** `Layers.gbf` e `Perpetuum.gbf` são grandes e idênticos em
todas as cópias — crie links simbólicos (`mklink`) ou atalhos para que sejam
armazenados apenas uma vez.

## Linux: múltiplos clientes

Cada cópia do cliente precisa de uma **versão diferente do Proton**, caso contrário ela se recusará a rodar:

1. Instale a Steam e o Perpetuum normalmente; verifique o `steam_appid.txt` (`223410`).
2. Copie a pasta `Perpetuum` para cada cliente.
3. Conectado à Steam, instale várias versões recentes do Proton (via Steam,
   manualmente ou através de builds GloriousEggroll).
4. Adicione cada cópia à Steam como um jogo que não é da Steam apontando para o seu `Perpetuum.exe`.
5. Force uma **versão diferente do Proton** para cada cópia em suas opções de inicialização.
6. Inicie o aplicativo oficial da Steam primeiro e, em seguida, abra as cópias.

Solução de problemas:

- Selecionar uma versão do Proton **não** a instala — você precisa iniciar o
  jogo uma vez com ela selecionada.
- Se o aplicativo oficial da Steam não iniciar, abra-o no modo de segurança primeiro.
- A partir do Proton 5.0, a emulação de DirectX 9/12 roda em **Vulkan**. Não possui
  GPU compatível com Vulkan? Adicione `PROTON_USE_WINED3D=1 %command%` às opções de
  inicialização de cada cópia.
- Caixa de texto vazia com aviso vermelho: instale `libfreetype6:i386`
  (distribuições baseadas em Debian/Ubuntu).

## Dimensionamento de interface (UI)

O cliente usa uma interface com pixels fixos sem dimensionamento dinâmico. Soluções alternativas:

- **Tela cheia em baixa resolução** — use o modo de tela cheia em uma resolução inferior à da sua
  tela e deixe a interface esticar para preenchê-la (os modos janela e sem bordas
  sempre usam a resolução nativa). Reduzir a própria resolução do monitor gera
  o mesmo efeito.
- **Aplicativos de redimensionamento de UI** — ex.: Lossless Scaling (Steam, Windows): execute o cliente
  em modo janela no tamanho base, defina uma escala personalizada no redimensionador, ative
  a ampliação e foque na janela do cliente. Espere o equilíbrio comum entre fluidez e
  nitidez do texto.
- **Lente de aumento do sistema operacional** — a Lupa do Windows (ou equivalente) para uma leitura
  mais detalhada ocasional.

## Inicializando sem privilégios de administrador

1. Copie os arquivos do cliente para fora da pasta da Steam, em um local com permissão de gravação.
2. Crie um arquivo `Perpetuum.bat` nesse local contendo
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Inicie através do arquivo de lote (batch).

<!--
Developer notes: rewritten 2026 in original prose. An earlier version was adapted from the
Open Perpetuum community wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); that text was
fully replaced, not reused. These are client-side procedures for the retail Steam client build;
nothing here is verifiable from this server's backend, and no server feature is
claimed. The Reshader (graphics mod) was intentionally left out: it targets the
retail client build and is not an OPP-server feature.
-->