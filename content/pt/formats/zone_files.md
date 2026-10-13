---
title: "Arquivos de zona"
description: "Os arquivos binários de camadas de terreno: nomenclatura, layouts de struct, bits de flag, o ciclo de salvamento e o que reside no BD em vez disso."
weight: 50
---

# Arquivos de zona

O terreno de uma zona é armazenado como um conjunto de **arquivos binários de camadas**, um por camada, junto aos dados da zona. O nome segue o padrão `{layer}.{zoneid:0000}.bin` (`Zone.CreateTerrainDataFilename`) — por exemplo, `plants.0042.bin` para a zona 42. As camadas são arrays planos de uma struct de tamanho fixo, **row-major (ordem por linha), largura × altura** (o padrão é 2048×2048 = 4.194.304 tiles).

## As camadas

| Arquivo | Struct | Bytes/tile | Conteúdo |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (byte) + `height` (byte) — obstáculos, plantas, decoração, ilhas |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (ou 1) | bits de controle por tile (veja a peculiaridade abaixo) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | o estado da planta por tile (abaixo) |
| `altitude.NNNN.bin` | `ushort` | 2 | elevação; comparada como `value / 4` em verificações de plantas (escala de coordenadas do cliente) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | apenas zonas terraformáveis: máscara de mesclagem (blend) por tile (abaixo) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | apenas zonas terraformáveis: elevação pré-terraformação no disco — **não lida pelo servidor** (abaixo) |

Camadas derivadas (computadas no carregamento, **não** são arquivos): `SlopeLayer` (a partir da altitude) e `Passable` (a partir de blocos + inclinação + posições transitáveis do BD, apenas zonas não terraformáveis). Em zonas terraformáveis, a altitude é encapsulada em um `TerraformableAltitude`, que calcula um intervalo de **barreira** por tile no carregamento: `blend/65535` mistura as constantes 1850 → altitude original (mín.) e 30000 → altitude original (máx.), restringindo (clamp) o intervalo para sempre conter o valor atual. Atualizações de altitude terraformada são limitadas a essa barreira — assim, `blend = 0` deixa um tile livremente terraformável entre 1850 e 30000, enquanto `blend = 65535` o fixa em sua elevação original. (Os arquivos `altitude_original.NNNN.bin` no disco mantêm as elevações pré-terraformação para ferramentas externas; o servidor obtém seu snapshot de altitude original em memória a partir do `altitude.NNNN.bin` carregado e nunca lê esse nome de arquivo.)

### `BlockingInfo` (2 bytes)

`flags` é `BlockingFlags` (byte):

| Bit | Nome |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle. `height` é a altura de bloqueio de caminhada do tile (a altura de bloqueio da planta é gravada aqui pelo código de crescimento de plantas).

### `TerrainControlFlags` (camada de controle)

Conjunto de flags `ushort`:

| Bit | Nome |
|---|---|
| 1 | AntiPlant |
| 2 | TerraformProtected |
| 4 | SyndicateArea |
| 8 | ConcreteA |
| 16 | ConcreteB |
| 64 | Roaming |
| 128 | Highway |
| 256 | PBSHighway |
| 512 | PBSTerraformProtected |
| 1024 | NpcRestricted |

(A numeração 512/1024 segue `1 << n`; o bit 32 não é utilizado.) Um tile permite plantas quando `!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`.

**Peculiaridade de armazenamento**: o carregador aceita arquivos de controle tanto de **1 byte/tile** quanto de **2 bytes/tile** — se o tamanho do arquivo for igual à contagem de tiles, cada byte é expandido para um `TerrainControlFlags`; caso contrário, o array bruto de `ushort` é lido (`LayerFileIO.LoadLayerData`). As zonas ativas utilizam todas o **formato de 2 bytes** (`control.0000.bin` = 8.388.608 B = 4.194.304 × 2); o formato de 1 byte (4 MB) é um fallback legado que o carregador ainda suporta.

### `PlantInfo` (7 bytes) — o estado do tile de planta

| Byte | Campo | Significado |
|---|---|---|
| 0 | `type` | `PlantType` (0 = vazio; 1..19 conforme [Plant fields](/pt/formats/plant-fields/)) |
| 1 | `state` | Índice de estado de crescimento (na tabela `state_N` da regra) |
| 2 | `time` | Acumulador de ticks de crescimento (comparado contra o `growRate` da regra) |
| 3 | `spawn` | **Probabilidade de spawn por tile, pré-calculada (baked) no arquivo da zona; o servidor nunca a grava** (não existe atribuição em nenhum lugar do código — `PlantInfo.Clear()` a preserva deliberadamente). 0 = tile estéril: qualquer planta existente nele é imediatamente removida durante a validação, e nunca brota. Caso contrário, funciona como um filtro por tentativa: durante a etapa de regeneração de plantas, um tile vazio aleatório só é aceito se `FastRandom.NextByte() < spawn`, ou seja, chance de sucesso por tile ≈ `spawn/256`. |
| 4 | `health` | HP atual (proporção da vida por estado da regra) |
| 5 | `material` | Quantidade atual de frutos (0–255) |
| 6 | `groundType` | Byte `GroundType` (0=Darkrocks … 17=Sand-ish, 20=undefined) — a classe de terreno contra a qual o `allowedTerrainTypes` da regra de planta faz a verificação |

### Exemplo prático — tamanhos de arquivo para uma zona de 2048×2048 (verificado contra arquivos reais)

```
blocks    4.194.304 tiles × 2 B = 8.388.608 B (8 MB)
plants    4.194.304 tiles × 7 B = 29.360.128 B (28 MB)
altitude  4.194.304 tiles × 2 B = 8.388.608 B (8 MB)
control   4.194.304 tiles × 2 B = 8.388.608 B (8 MB, formato de 2 bytes; um arquivo legado de 1 byte teria 4 MB)
```

**Verificação de dados reais** (`plants.0106.bin`, a zona gamma terraformável): todos os 4.194.304 tiles possuem `spawn = 0x83` (131/256 ≈ 51% de chance por tentativa) e `type = 0`, exceto 10 tiles contendo plantas vivas — o mapa de spawn é um campo de probabilidade pré-calculado para toda a zona, independente de onde as plantas estão atualmente.

Nem toda zona possui todos os arquivos: 66 das 84 zonas distribuem um `plants.NNNN.bin`. As 18 sem esse arquivo são as variantes legadas substituídas de gamma (`zone_tm_g_*`, `zone_ics_g_*`, `zone_asi_g_*`, ids 20–43), que não são carregadas. O diretório das camadas é `$GameRoot/layers/`.

## O ciclo de salvamento (`IntervalLayerSaver.cs`)

- Cada camada mutável (blocks, control, plants, altitude) é monitorada por um `IntervalLayerSaver<T>`; qualquer escrita em tile/área define uma flag de modificação (dirty flag).
- O gravador é registrado como um processo em um temporizador de **2 horas** (`TerrainsModule`); uma camada modificada é gravada quando o tick é acionado.
- As gravações vão para um arquivo `.tmp<ticks>.bin`, são **verificadas via MD5** contra uma releitura e, somente então, substituem o arquivo real.
- Ao parar o servidor, as camadas modificadas são salvas mais uma vez.
- Nós de minério **não** estão nesses arquivos — eles persistem na tabela `mineralnodes` do BD (flush a cada 30 minutos, veja [Ore fields](/pt/formats/ore-fields/)).

## O que é e o que não é um arquivo

| Dado | Onde |
|---|---|
| Camadas de terreno (blocks/control/plants/altitude) | Arquivos `.bin` |
| Estado de nós de minério | BD `mineralnodes` |
| Espécies de plantas por zona | BD `plantrules` + **arquivos** de regras (`$GameRoot/plantrules/*.txt`) |
| Configuração de zona (fertilidade, tamanho, tipo, conjunto de regras) | BD `zones` |
| Configuração de minério | BD `mineralconfigs` |

<!-- Developer notes: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1-vs-2 byte control handling, safe zero-fill on size mismatch);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty flag, MD5 + tmp rename, stop-save);
     Bootstrapper/Modules/TerrainsModule.cs (layer load order: blocks, control, plants,
     altitude, blend; slope + passable derivation; 2h saver + 2h material process). -->