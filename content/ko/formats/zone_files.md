---
title: "존 파일"
description: "이진 지형 레이어 파일: 이름 지정, 구조체 레이아웃, 플래그 비트, 저장 사이클, 그리고 DB에 대신 저장되는 항목."
weight: 50
---

# 존 파일

존의 지형은 레이어별로 하나씩, 존 데이터 옆에 **이진 레이어 파일** 집합으로 저장됩니다. 파일 이름은 `{layer}.{zoneid:0000}.bin`
(`Zone.CreateTerrainDataFilename`)이며, 예를 들어 42번 존의 경우 `plants.0042.bin`입니다. 레이어는 고정 크기 구조체의 평탄한 배열이며, **행 우선(row-major), 너비 × 높이**입니다(기본값 2048×2048 =
4,194,304 타일).

## 레이어

| 파일 | 구조체 | 타일당 바이트 | 내용 |
|---|---|---|---|
| `blocks.NNNN.bin` | `BlockingInfo` | 2 | `flags` (byte) + `height` (byte) — 장애물, 식물, 장식, 섬 |
| `control.NNNN.bin` | `TerrainControlFlags` | 2 (or 1) | 타일별 제어 비트(아래 특이사항 참조) |
| `plants.NNNN.bin` | `PlantInfo` | 7 | 타일별 식물 상태(아래) |
| `altitude.NNNN.bin` | `ushort` | 2 | 고도; 식물 검사에서 `value / 4`로 비교됨(클라이언트 좌표 스케일링) |
| `altitude_blend.NNNN.bin` | `ushort` | 2 | 지형 변형 가능 존 전용: 타일별 블렌드 마스크(아래) |
| `altitude_original.NNNN.bin` | `ushort` | 2 | 지형 변형 가능 존 전용: 디스크에 저장된 지형 변형 전 고도 — **서버가 읽지 않음**(아래) |

파생 레이어(로드 시 계산되며, **파일 아님**): `SlopeLayer`(고도에서 생성)와
`Passable`(blocks + slope + DB 통과 가능 위치에서 생성, 지형 변형 불가능 존 전용).
지형 변형 가능 존에서는 고도가 `TerraformableAltitude`로 감싸지며, 로드 시 타일별 **barrier** 범위를 계산합니다: `blend/65535`가 상수
1850 → 원래 고도(최소값)와 30000 → 원래 고도(최대값)를 혼합하고, 범위가 항상 현재 값을 포함하도록 클램프합니다. 지형 변형된 고도 업데이트는 해당 barrier로 클램프됩니다 — 따라서 `blend = 0`이면 타일이 1850과
30000 사이에서 자유롭게 지형 변형 가능하고, `blend = 65535`이면 원래 고도에 고정됩니다. (디스크의
`altitude_original.NNNN.bin` 파일은 외부 도구용 지형 변형 전 고도를 보관합니다. 서버는 로드된
`altitude.NNNN.bin`에서 메모리 내 원래 고도 스냅샷을 가져오고, 해당 파일 이름을 절대 읽지 않습니다.)

### `BlockingInfo` (2바이트)

`flags`는 `BlockingFlags`(byte)입니다:

| 비트 | 이름 |
|---|---|
| 1 | Obstacle |
| 2 | Plant |
| 4 | Decor |
| 8 | Island |

`NonNaturally` = Decor \| Island \| Obstacle입니다. `height`는 타일의 이동 차단 높이입니다(식물 성장 코드가 식물 차단 높이를 여기에 기록합니다).

### `TerrainControlFlags`(제어 레이어)

`ushort` 플래그 집합:

| 비트 | 이름 |
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

(512/1024 번호 체계는 `1 << n`을 따릅니다. bit 32는 미사용입니다.) 타일이 식물 허용 상태인 조건은
`!(AntiPlant || Roaming || Highway || PBSHighway || ConcreteA || ConcreteB)`일 때입니다.

**저장 특이사항**: 로더는 **1바이트/타일**과 **2바이트/타일** 제어 파일 모두를 받아들입니다 — 파일 길이가 타일 수와 같으면 각 바이트가
`TerrainControlFlags`로 확장되고, 그렇지 않으면 원본 `ushort` 배열이 읽힙니다
(`LayerFileIO.LoadLayerData`). 운영 중인 존은 모두 **2바이트 형식**을 사용합니다
(`control.0000.bin` = 8,388,608 B = 4,194,304 × 2). 1바이트 형식(4 MB)은 로더가 여전히 지원하는 레거시 폴백입니다.

### `PlantInfo` (7바이트) — 식물 타일 상태

| 바이트 | 필드 | 의미 |
|---|---|---|
| 0 | `type` | `PlantType`(0 = 비어 있음; 1..19는 [식물 필드](/ko/formats/plant-fields/) 참조) |
| 1 | `state` | 성장 상태 인덱스(규칙의 `state_N` 테이블을 가리킴) |
| 2 | `time` | 성장 틱 누적값(규칙의 `growRate`와 비교) |
| 3 | `spawn` | **타일별 생성 확률로, 존 파일에 미리 고정되어 있으며 서버는 절대 기록하지 않음**(코드 어디에도 할당이 존재하지 않음 — `PlantInfo.Clear()`는 의도적으로 이를 보존함). 0 = 불모 타일: 이미 있는 식물은 검증 중 즉시 제거되고, 절대 싹이 트지 않음. 그 외에는 시도별 게이트: 식물 재생성 패스에서 무작위 빈 타일은 `FastRandom.NextByte() < spawn`일 때만 허용되며, 즉 타일별 통과 확률 ≈ `spawn/256`. |
| 4 | `health` | 현재 HP(규칙의 상태별 HP 비율) |
| 5 | `material` | 현재 과일 양(0–255) |
| 6 | `groundType` | `GroundType` byte(0=Darkrocks … 17=Sand-ish, 20=undefined) — 식물 규칙의 `allowedTerrainTypes`가 검사하는 지형 클래스 |

### 예시 — 2048×2048 존의 파일 크기(운영 파일과 대조 확인)

```
blocks    4,194,304 타일 × 2 B = 8,388,608 B (8 MB)
plants    4,194,304 타일 × 7 B = 29,360,128 B (28 MB)
altitude  4,194,304 타일 × 2 B = 8,388,608 B (8 MB)
control   4,194,304 타일 × 2 B = 8,388,608 B (8 MB, 2바이트 형식; 1바이트 레거시 파일이면 4 MB)
```

**실데이터 확인**(`plants.0106.bin`, 지형 변형 가능 gamma 존): 4,194,304개 타일 모두 `spawn = 0x83`(131/256 ≈ 시도별 51% 확률)이며, 실제 식물이 있는 10개 타일을 제외하면 `type = 0`입니다 — spawn 맵은 현재 식물이 어디에 있는지와 무관한 존 전체의 고정 확률 필드입니다.

모든 존에 모든 파일이 있는 것은 아닙니다: 84개 존 중 66개가 `plants.NNNN.bin`을 포함합니다. 없는 18개는 대체된 레거시 gamma 변형(`zone_tm_g_*`, `zone_ics_g_*`,
`zone_asi_g_*`, id 20–43)이며, 로드되지 않습니다. 레이어 디렉터리는
`$GameRoot/layers/`입니다.

## 저장 사이클(`IntervalLayerSaver.cs`)

- 각 변경 가능한 레이어(blocks, control, plants, altitude)는
  `IntervalLayerSaver<T>`에 의해 감시됩니다. 타일/영역 쓰기가 발생하면 dirty 플래그가 설정됩니다.
- 저장기는 **2시간** 타이머의 프로세스로 등록됩니다
  (`TerrainsModule`). tick이 발생하면 dirty 레이어가 기록됩니다.
- 쓰기는 `.tmp<ticks>.bin` 파일로 이루어지며, 다시 읽은 결과와 **MD5 검증**을 거친
  후에야 실제 파일을 대체합니다.
- 서버 종료 시 dirty 레이어가 한 번 더 저장됩니다.
- 광물 노드는 **이 파일들에 있지 않습니다** — `mineralnodes` DB
  테이블에 영속화됩니다(30분 플러시, [광석 필드](/ko/formats/ore-fields/) 참조).

## 파일이 되고 안 되는 항목

| 데이터 | 위치 |
|---|---|
| 지형 레이어(blocks/control/plants/altitude) | `.bin` 파일 |
| 광물 노드 상태 | DB `mineralnodes` |
| 존별 식물 종 | DB `plantrules` + 규칙 **파일**(`$GameRoot/plantrules/*.txt`) |
| 존 설정(비옥도, 크기, 유형, 규칙 세트) | DB `zones` |
| 광석 설정 | DB `mineralconfigs` |

<!-- 개발자 노트: Zones/ZoneExtensions.cs (LayerFileIO, CreateTerrainDataFilename,
     1바이트 대 2바이트 제어 처리, 크기 불일치 시 안전한 0 채움);
     Zones/Terrains/BlockingInfo.cs + BlockingFlags.cs; TerrainControlInfo.cs +
     TerrainControlFlags.cs; Materials/Plants/PlantInfo.cs; Zones/Terrains/GroundType.cs;
     Zones/Terrains/Layer.cs (RawData, SizeInBytes = Marshal.SizeOf<T>);
     Zones/Terrains/IntervalLayerSaver.cs (dirty 플래그, MD5 + tmp 이름 변경, 종료 시 저장);
     Bootstrapper/Modules/TerrainsModule.cs (레이어 로드 순서: blocks, control, plants,
     altitude, blend; slope + passable 파생; 2시간 저장기 + 2시간 material 프로세스). -->