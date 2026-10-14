---
title: "Servidor y referencia"
description: "Información del servidor, puntuaciones más altas, descargas de datos de referencia y la tienda del juego."
weight: 170
---

# Servidor y referencia

Esta página cubre los sistemas "meta": información del servidor/sistema, puntuaciones más altas, los datos de referencia
que descarga el cliente y la tienda del juego.

> Las ubicaciones de la interfaz siguen el [resumen de la interfaz del cliente](/es/features/ui/). Las mecánicas siguientes han sido confirmadas contra
> el servidor.

## Información del servidor y del sistema

- **Información del servidor** — estado/información general del servidor.
- **Información del sistema** — detalles a nivel de sistema.
- **Estado de apagado del servidor** — si un apagado programado está en vigor (de solo lectura para
  los jugadores; el apagado en sí es una acción de administración).

## Puntuaciones más altas

- **Puntuaciones del servidor** — los mejores resultados de todo el servidor.
- **Mis puntuaciones** — tus mejores marcas personales.

Consulta también [combate](/es/features/combat/) para ver cómo las bajas nutren estas estadísticas.

## Datos de referencia

El cliente descarga datos de referencia estáticos del servidor para renderizar el contenido correctamente.
Son **consultas de solo lectura**, no acciones de los jugadores:

- **Efectos** — las definiciones de efectos.
- **Enums** — valores de enumeración.
- **Valores por defecto de entidades** — definiciones base de entidades.
- **Campos agregados** — datos de campos agregados.
- **Unidades de configuración de definiciones** — configuración por definición.
- **Distancias** — constantes de distancia utilizadas por el cliente.
- **Comandos** — la lista de comandos conocidos (una referencia del lado del cliente).
- **Fisuras** — definiciones de fisuras (consulta también la lista de fisuras de zonas).

No "utilizas" estos datos directamente; el cliente los obtiene bajo demanda. Se enumeran aquí porque
aparecen en el inventario de comandos.

## La tienda

La tienda del juego (una integración de pagos):

- **Listar productos** — ver qué está a la venta.
- **Iniciar una transacción** — comenzar una compra.
- **Finalizar una transacción** — completar una compra.

Las compras en la tienda son transacciones con dinero real (o equivalente); los productos exactos y
los precios forman parte del contenido de la tienda.

## Notas prácticas

- **Los datos de referencia se obtienen automáticamente** — nunca los activas manualmente; mantienen el cliente
  sincronizado con el contenido del servidor.
- **Las puntuaciones más altas son tu prestigio** — consulta tus marcas personales y las del servidor.
- **Las transacciones de la tienda tienen dos pasos** — iniciar y finalizar; no des por sentado que una compra está
  completa hasta que se haya finalizado.
- **El estado de apagado es informativo** — te avisa si se aproxima una ventana de mantenimiento.

<!-- Developer notes: ServerInfoGet.cs / SystemInfo.cs / ServerShutDownState.cs;
     GetHighScores.cs / GetMyHighScores.cs; GetEffects.cs / GetEnums.cs /
     GetEntityDefaults.cs / GetAggregateFields.cs / GetDefinitionConfigUnits.cs /
     GetDistances.cs / GetCommands.cs / GetRifts.cs; SteamGetProducts.cs /
     SteamStartTransaction.cs / SteamFinishTransaction.cs. -->
