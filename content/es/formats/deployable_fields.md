---
title: "Campos de los desplegables"
description: "Formato de las datos de los desplegables, tipos de estructuras, y las reglas de desmontaje."
weight: 410
---

# Campos de los desplegables

Los **desplegables** son objetos colocados en las zonas. Incluyen las estructuras
PBS, los teletransportadores, los kioscos, y otros objetos.

## Tipos de desplegables

| Tipo | Descripción |
|---|---|
| **PBS** | Estaciones de base de poder |
| **Teletransportador** | Estructuras de teletransporte |
| **Kiosco** | Estructuras de misión |
| **Terminal** | Terminales de terreno |
| **Puerta** | Puertas de zona |
| **Torreta** | Torretas de defensa |

## Campos de datos

| Campo | Tipo | Descripción |
|---|---|---|
| `definition` | int | ID de la definición |
| `definitionname` | string | Nombre de la definición |
| `type` | string | Tipo de desplegable |
| `position` | (x, y) | Posición en la zona |
| `owner` | int | ID del propietario (corporación) |
| `health` | # | Puntos de vida |
| `energy` | # | Energía |

## Desmontaje

Algunos desplegables pueden ser **desmontados** para materiales:

- El desmontaje **destruye** el objeto.
- Los materiales se añaden a la **carga** del robot.
- Los rendimientos están definidos por tipo en la base de datos.

## Notas prácticas

- **Los desplegables son objetos** — tienen stats y componentes.
- **El desmontaje es destructivo** — el objeto es destruido.
- **Los rendimientos varían** según el tipo de desplegable.
- **Las PBS son desplegables** — ver [PBS](/es/features/pbs/).
