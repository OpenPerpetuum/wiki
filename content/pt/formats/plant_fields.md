---
title: "Campos de plantas"
description: "Formato do arquivo de regras das plantas (GenXY), cada campo de regra com tipo, valor padrão e consumidor, mais a máquina de estados de crescimento."
weight: 20
---

# Campos de plantas

O comportamento das plantas é definido por espécie por um **arquivo de regras** (texto puro) sob
`$GameRoot/plantrules/`. A determinação de quais arquivos pertencem a uma zona é feita pelo mapeamento no BD
`plantrules(idx, plantrule, rulesetid)` → `zones.plantruleset`; o carregamento e mesclagem ocorrem em
`PlantRuleLoader.cs`, e o mapeamento campo-a-objeto é feito em `PlantRule.cs`.

## Formato do arquivo

Uma chave e valor no padrão `key=value` por linha; comentários iniciados por `//` são descartados. Os valores utilizam **caracteres de token
GenXY** (`GenxyReader.cs` — o primeiro caractere define o tipo e a base numérica):

| Token | Analisado como | Exemplo |
|---|---|---|
| `n` | int, decimal | `n125`, `n-1` |
| `N` | int[], decimal, separados por vírgula | `N5,5,5,5` |
| `f` | double, decimal | `f0.1` |
| `$` | string | `$prismocitae` |
| `i` | int, **hexadecimal** | `iFF` |
| `L` | long, **hexadecimal** | `L100` |
| `4` | int[], **hexadecimal** | `41,2,3` → [1, 2, 3] |

### ⚠ A armadilha do "array puro" (bare array)

Os arquivos também contêm valores como `blockingHeight=40,3,3,4` sem **nenhum token explícito**.
O analisador não trata isso como exceção: o `4` inicial é interpretado como o token de
`IntegerArray` (hexadecimal), e o restante é processado em hexadecimal. Portanto:

```
blockingHeight=40,3,3,4   →  token '4' + array hex "0,3,3,4"   →  [0, 3, 3, 4]
blockingHeight=N0,8,11,14 →  token 'N' + array decimal         →  [0, 8, 11, 14]
```

Ambas as formas resultam em `int[]`, e o zero inicial é absorvido pelo `4`. É por isso que
todo array sem prefixo nos arquivos originais começa com `4` — uma convenção
que preserva o valor pretendido do primeiro elemento. **Ao criar novos arquivos de regras,
utilize sempre o prefixo `N` explicitamente**; valores ≥ 10 em um array puro seriam analisados como hex
e alterariam silenciosamente o seu significado.

### Herança

A instrução `source=$other_rule.txt` carrega `other_rule.txt` primeiro e aplica as chaves do arquivo
atual como substituições (`PlantRuleLoader.LoadRuleByName`). Exemplo:
`irontree_t2.txt` consiste simplesmente em:

```
source=$irontree_lo.txt
fruitAmount=n125
```

## Referência dos campos

Todos os campos são lidos do dicionário de configurações mesclado (`PlantRule.cs`). Chaves ausentes utilizam
o valor padrão exibido.

| Chave | Tipo / padrão | Consumido por | Efeito |
|---|---|---|---|
| `index` | int (0) | `PlantRule.Type` | O valor enum `PlantType` desta espécie (1=GrassA … 19=Devrinol). Também o byte `PlantInfo.type` armazenado por bloco (tile). |
| `name` | string | payload de informações do cliente | Nome de exibição. |
| `fertility` | int (0) | `PlantRuleExtensions.GetWinnerPlantTypeBasedOnFertility` | Peso no sorteio ponderado que escolhe uma espécie para um bloco **sem** plantas vizinhas. 0 = nunca nasce naturalmente. |
| `spreading` | int (0) | `GetSpreadingBasedWinnerPlantType` | Multiplicador de peso quando um bloco **possui** vizinhos: peso do candidato = `contagemVizinhos × spreading`. 0 = nunca vence a propagação. |
| `killDistance` | int (0) | `NatureCube.CheckKillDistance` | Distância mínima em relação a qualquer planta existente do mesmo tipo; 0/negativo = sem limite. |
| `growRate` | int (0) | `GrowPlantOnTile` | Número de ciclos (ticks) do cubo que o byte `PlantInfo.time` deve acumular antes de rodar a máquina de estados. Maior = mais lento. |
| `slope` / `minSlope` | int (0) | `ValidateTile` | Faixa de inclinação permitida da camada derivada de inclinação. Fora dessa faixa a planta é removida. |
| `allowedAltitudeLow/High` | int (0) | `ValidateTile` | Faixa de altitude, comparada com `Altitude / 4` (a divisão por 4 alinha com as coordenadas do cliente). Escalonada pelo `plantaltitudescale` da zona. |
| `allowedWaterLevelLow/High` | int (0) | `ValidateTile` | Faixa para `altitude/4 − waterLevel/4` — cria vegetação costeira. Também escalonada pela altitude. |
| `allowedTerrainTypes` | int[] (vazio) | `ValidateTile` | Bytes permitidos de `groundType` (veja [Arquivos de zona](/pt/formats/zone-files/)). Vazio = em nenhum lugar. Ignorado totalmente quando `allowedOnNonNatural` estiver ativo. |
| `fruitingState` | int (−1) | `GrowPlantOnTile` | Primeiro estado que produz frutos. −1 ⇒ `NotFruiting` (nunca colhível). |
| `fruitDefinition` | int (−1) | colheita | Definição de item do fruto gerado. |
| `fruitMaterialName` | string | exibição | Nome do fruto (ex.: `$prismocitae`). |
| `fruitAmount` | byte (0), limitado a 0–255 | `GrowPlantOnTile` | Quantidade máxima de frutos por planta. A primeira entrada no estado de frutificação preenche de 5% a 15%; cada tick de crescimento posterior adiciona 15% a 25%, limitado a 100%. |
| `health` | byte[] por estado | `GrowPlantOnTile`, combate | Pontos de vida por estado de crescimento. Na mudança de estado, a **proporção** de vida atual é transferida para o novo estado. |
| `blockingHeight` | int[] por estado | `GrowPlantOnTile`, contagem de spawn | Altura de bloqueio por estado; valores `>0` ativam o bit `Plant` na camada de blocos (intransitável) e fazem a planta contar para a meta de fertilidade da zona. |
| `maxAmount` | int (−1) | `SpawnPlants` | Limite máximo desta espécie por zona; −1 = ilimitado. |
| `playerSeeded` | bool (0) | `GetNewPlantRule`, sorteio de fertilidade | Excluída de **todos** os surgimentos naturais; só existe onde um jogador a plantou. |
| `damageScale` | double (1.0) | combate de plantas | Multiplicador de dano recebido. |
| `onlyOnUnprotectedZone` | bool (0) | validação de spawn | Só se desenvolve em zonas desprotegidas. |
| `allowedOnNonNatural` | bool (0) | `ValidateTile` | Ignora verificações de bits de controle, tipo de terreno e inclinação (cresce em blocos "artificiais"). |
| `placesConcrete` | bool (0) | `GrowPlantOnTile` (morte) | Ao morrer, limpa os bits de controle ConcreteA/B sob o bloco. |
| `state_N` | int[] | `GetNextState` | Opções de próximo estado para o estado `N` — cada elemento é escolhido de forma **uniformemente aleatória**. |
| `action_N` | int[] | `GetNextState` | Próximas escolhas de `PlantType` para o estado `N` (distribuição uniforme). Um valor de ação `0` (NotDefined) significa a **morte** da planta. |

A consistência é validada durante o carregamento (`CheckConsistency`): `tamanho(health) == tamanho(blockingHeight) == número de estados`.

## A máquina de estados de crescimento

A cada ciclo de cubo 32×32, para cada bloco com planta (`GrowPlantOnTile`):

1. Se `time < growRate`: `time++`, concluído.
2. Caso contrário: `time = 0`, sorteia `state_N` e `action_N` para o estado atual:
   - `action == 0` → a planta morre (sinal de morte `type:0, state:1` enviado ao cliente);
     se `placesConcrete`, remove o concreto sob o bloco.
   - caso contrário → `type = action`, `state = next`, `health = healthRatio ×
     Health[newState]` (proporção de dano preservada).
   - Fruto: se `newState == fruitingState`, `material = fruitAmount ×
     uniform(0.05, 0.15)`; se `newState > fruitingState`, `material += fruitAmount ×
     uniform(0.15, 0.25)` (limitado a `fruitAmount`); caso contrário `material = 0`.
   - Altura de bloqueio = `blockingHeight[newState]`; o bit `Plant` da camada de bloqueios segue
     `height > 0`.

### Exemplo prático — `grass_a.txt`

```
index=n1            → GrassA
fertility=n1        → peso 1/… no sorteio sem vizinhos
spreading=n2        → peso no grupo = 2 × vizinhos
growRate=n1         → avalia o estado a cada tick de cubo (rápido)
maxAmount=n190      → no máximo 190 por cubo
health=N5,5,5,5     → 5 HP em todos os estados
blockingHeight=40,0,0,0 → analisado como [0,0,0,0]: grama NUNCA bloqueia passagem
fruitingState=n-1   → NotFruiting: grama nunca produz frutos
state_0=40,0,1      → [0,0,1]: 2/3 permanecem no estado 0, 1/3 avança
state_1=41,1,2      → [1,1,2]
state_2=42,2,3      → [2,2,3]
state_3=43          → [3]
action_3=N1,1,1,0   → no último estado: 3/4 permanecem, 1/4 morre
```

Dessa forma, um bloco de grama avança aproximadamente um estado a cada 3 ticks em média e, no último
estado, tem 25% de chance por tick de morrer e reiniciar o ciclo — uma espécie de cobertura
contínua e sem frutos.

### Exemplo prático — `wall.txt` (12 estados, prefixo `N`)

`blockingHeight=N0,0,2,3,4,7,9,10,10,13,13,14`, `health=N20,60,80,…,255`,
`state_7=N7,7,8,8,6` (pode regredir um estado), `playerSeeded=n1`,
`onlyOnUnprotectedZone=n1`, `maxAmount=n15`: uma fortificação plantada por jogador que só
existe em zonas desprotegidas, limitada a 15 por cubo, que cresce (e ocasionalmente
encolhe) através de 12 estados até uma altura de 14 e 255 HP.

## Onde reside o estado por bloco

O estado em tempo de execução por bloco é a struct `PlantInfo` de 7 bytes no arquivo da camada de plantas da zona
(`type, state, time, spawn, health, material, groundType`) — consulte
[Arquivos de zona](/pt/formats/zone-files/). O byte `spawn` é uma probabilidade de surgimento por bloco
gravada no próprio arquivo da zona — `0` marca um bloco estéril (plantas existentes nele são removidas na
validação, nunca brotando); qualquer outro valor faz com que tentativas de regeneração naquele bloco
passem por uma verificação aleatória com chance ≈ `spawn/256`. O servidor nunca altera esse
byte. Dados reais: todos os blocos de `plants.0106.bin` possuem `0x83` (≈ 51%).

## Carga útil do cliente (Client payload)

`PlantRuleExtensions.GetPlantInfoForClient` envia, por espécie: `index`, `mineral`
(= fruitDefinition), `name`, `blocks` (blockingHeight), `health`.

<!-- Developer notes: Materials/Plants/PlantRule.cs (field getters, GetNextState,
     CheckConsistency); PlantRuleLoader.cs (file load, source: override,
     plantAltitudeScale applied to allowedAltitudeLow/High + allowedWaterLevelLow);
     PlantRuleExtensions.cs (fertility + spreading weighted draws);
     NatureCube.cs (ValidateTile checks order: block flags -> spawn byte -> rule
     existence -> control bits -> altitude/4 -> water level -> terrain type ->
     slope; GrowPlantOnTile state machine + fruit math); Common/SettingsLoader.cs
     (line join with '#' then GenxyConverter.Deserialize); GenXY/GenxyReader.cs +
     GenxyToken.cs (token characters; '4' = hex int array, 'N' = decimal int array,
     'n' = int decimal). Rule files live at $GameRoot/plantrules (plantrules table
     maps rulesetid -> file names). -->
