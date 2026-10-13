---
title: "배치 가능 필드"
description: "배치 가능 항목이 식별되는 방식, 캡슐-오브젝트 페어링, 그리고 구역에 배치된 오브젝트를 구동하는 집계 필드."
weight: 40
---

# 배치 가능 필드

**배치 가능 항목**은 구역에 유닛으로 배치할 수 있는 아이템입니다(모바일 텔레포트,
지뢰, 필드 효과 발신기, PBS 구조물, …). 플래그로 식별되며, 캡슐↔오브젝트 정의와
페어링되고, 런타임에는 집계 필드에 의해 구동됩니다.

## 식별

- **카테고리 플래그** `cf_deployable_structure` = `0x998` (비트마스크) —
  `entitydefaults.categoryflags`에 설정되며, 엔티티 레지스트리가 배치기 아이템 클래스를
  등록하기 위해 스캔하는 집합입니다(`EntitiesModule.cs`, 예: `PlantSeedDeployer`는
  이 카테고리로 등록됨).
- **속성 플래그** `deployable` = `entitydefaults.attributeflags`의 **23** 비트
  (마스크 `1 << 23`).
- 전체 카탈로그(스탯 포함)는 [Deployables](/content/deployables/)에서 생성됩니다.

## 캡슐 ↔ 오브젝트 페어링

배치 가능 항목은 쌍으로 존재합니다: **캡슐**(인벤토리에 휴대하는 아이템)과
**오브젝트**(구역에 나타나는 유닛). 이 페어링은 DB 컬럼
`entitydefaults.targetdefinition`이며, **양방향**입니다:

- capsule.`targetdefinition` → 오브젝트의 정의
- object.`targetdefinition` → 캡슐의 정의

`PBSHelper.GetPBSObjectDefinitionFromCapsule` / `ItemDeployerHelper`는 어느 방향이든
해석합니다. 예시 페어: `def_mobile_field_eccm_capsule` ⇄ `def_mobile_field_eccm`.

## 배치 흐름

`ItemDeployer.cs`(비 PBS 배치 가능 항목의 베이스):

1. `Deploy(zone, player)`는 플레이어 중심에서 스폰 위치를 계산합니다.
2. `CreateDeployableItem`는 **오브젝트** 유닛(캡슐이 아님)을 생성하고 저장합니다.
3. 5초짜리 "배치 빔"이 렌더링됩니다.
4. 트랜잭션 커밋 시 오브젝트가 구역에 추가됩니다(`ZoneEnterType.Deploy`).

PBS 구조물은 별도의 `PBSDeployer` / `PBSObjectHelper` 경로를 사용합니다. PBS
오브젝트가 해체되면 구역에서 제거되고, 해당 **캡슐**이 로트에 추가됩니다
(`PBSObjectHelper.cs`).

## 런타임 집계 필드

이 필드들은(`aggregatevalues`에서, 정의별로) 오브젝트가 구역에 배치된 후 해당
오브젝트를 구동합니다. 소비자는 아래에 제시되어 있습니다.

| 필드 | 의미 | 소비자 |
|---|---|---|
| `despawn_time` | 배치된 오브젝트의 수명, **밀리초**. 만료 시 유닛이 구역에서 제거됩니다(원격 제어되는 경우 처치됨). | `UnitDespawnHelper.Create(unit, TimeSpan.FromMilliseconds(despawn_time))` → `effect_despawn_timer` 적용. |
| `armor_max` | 배치된 유닛의 최대 방어력. | 유닛 전투 |
| `resist_chemical/explosive/kinetic/thermal` | 피해 저항. | 유닛 전투 |
| `signature_radius` | 스캔 시그니처 크기. | 스캐너 / 스텔스 |
| `stealth_strength` | 스텔스 강도. | 스캐너 / 스텔스 |
| `effect_*` (예: `effect_field_sensor_strength_modifier`, `effect_stealth_strength_modifier`, `effect_field_reactor_radiation_modifier`) | 오브젝트가 방출하는 필드 효과 수정자. | `FieldEffectGenerators/*` (예: `FieldEccmEffectGeneratorDeployer`는 `GetPropertyModifier`를 통해 `despawn_time`과 효과 필드를 읽음). |
| `mobile_teleport_cooldown` | 모바일 텔레포트 사용 간 쿨다운(밀리초). | 모바일 텔레포트 유닛 |
| `trigger_mass` | 지뢰 트리거를 무장시키는 질량 임계값. | 지뢰 유닛 |
| `damage_kinetic/thermal/explosive/chemical/toxic` | 지뢰가 속성별로 주는 피해. | 지뢰 유닛 |

`despawn_time`은 핵심 필드입니다: 배치된 모든 오브젝트는 `UnitDespawnHelper`를
가지며, 그 `IntervalTimer`(650ms 틱)는 `effect_despawn_timer` 효과를 다시 확인하고,
효과가 사라지면 디스폰 전략을 실행합니다.

### 작동 예시 — `def_mobile_field_eccm`

[Deployables](/content/deployables/)에서:

```
armor_max=15000
resist_chemical=150  resist_explosive=150  resist_kinetic=150  resist_thermal=150
signature_radius=20
stealth_strength=80  (오브젝트) / 50 (방어 캡슐)
despawn_time=900000          → 900초 = 15분 수명
effect_field_sensor_strength_modifier=100
effect_field_reactor_radiation_modifier=0.75
```

캡슐을 배치하면 로봇 위치에 오브젝트가 스폰됩니다. 15분간 유지되며, 150% 저항을
가진 15,000 방어력을 갖추고, 생존 중에는 센서 강도를 100% 높이고 반응로 방사선을
25% 줄이는 필드를 방출합니다.

<!-- 개발자 노트: EntitiesModule.cs:449 (ByCategoryFlags<PlantSeedDeployer>
     cf_deployable_structure); ExportedTypes/CategoryFlags.cs (cf_deployable_structure
     = 0x998), ExportedTypes/AttributeFlags.cs (deployable = 23);
     EntityFramework/DefinitionConfig.cs (targetdefinition 컬럼, TargetEntityDefault);
     Deployers/ItemDeployer.cs (배치 흐름, 5초 빔, ZoneEnterType.Deploy);
     Zones/PBS/PBSHelper.cs (capsule<->object), Zones/PBS/PBSObjectHelper.cs
     (해체 -> 캡슐 로트); Units/UnitDespawnHelper.cs (despawn_time ->
     effect_despawn_timer, 650ms 틱, 요새용 CancellableDespawnHelper);
     Zones/FieldEffectGenerators/FieldEccmEffectGeneratorDeployer.cs
     (GetPropertyModifier(AggregateField.despawn_time) + effect_* 필드). -->