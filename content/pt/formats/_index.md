---
title: "Formatos"
description: "Referência para desenvolvedores: como cada campo de atributo é armazenado, analisado e utilizado pelo servidor."
weight: 60
---

# Formatos

Referência de campos voltada para desenvolvedores. Cada página rastreia um campo de atributo desde seu armazenamento
(coluna do BD, chave de arquivo de regras ou byte da camada binária) até o código que o consome,
com exemplos numéricos detalhados. Resumos voltados para jogadores sobre "o que isso significa no jogo" encontram-se
nas seções de [funcionalidades](/pt/features/) e [conteúdo](/content/) — aqui é onde estão os
tipos exatos, padrões, fórmulas e caminhos de código.

| Página | Conteúdo |
|---|---|
| [Campos de plantas](/pt/formats/plant-fields/) | Formato de arquivo de regras de plantas (GenXY), cada campo de regra com tipo/padrão/consumidor, a máquina de estados de crescimento, verificações de validação |
| [Campos de minérios](/pt/formats/ore-fields/) | Colunas de `minerals` + `mineralconfigs`, as fórmulas de geração de nós, ciclo de vida e persistência de nós, mecânicas de extração |
| [Campos de estruturas implantáveis](/pt/formats/deployable-fields/) | Como as estruturas implantáveis são identificadas, pareamento cápsula↔objeto e os campos agregados que controlam objetos posicionados |
| [Arquivos de zona](/pt/formats/zone-files/) | Os arquivos binários de camadas de terreno: layouts de struct, bits de flags, ciclo de salvamento e o que reside no BD em vez disso |

Convenções:

- **GenXY** é a serialização de configurações usada para arquivos de regras e `entitydefaults.options`
  (caracteres de token de acordo com `GenxyToken.cs`; consulte [Campos de plantas → formato do arquivo](/pt/formats/plant-fields/)).
- Os caminhos de código são relativos a `src/`.
- Onde um valor for uma **constante** (não dados), o arquivo e o nome da constante são fornecidos.