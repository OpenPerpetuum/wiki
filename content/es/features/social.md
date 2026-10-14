---
title: "Social"
description: "Comunicación y reputación: correo, canales de chat, amigos, relaciones (standings), páginas amarillas, noticias y encuestas."
weight: 140
---

# Social

Esta página cubre la comunicación y la reputación: **correo**, **canales de chat**, **amigos**,
**relaciones (standings)**, y las opciones públicas de **páginas amarillas / noticias / encuestas**.

> Las ubicaciones de la interfaz siguen el [resumen de la interfaz del cliente](/es/features/ui/) (el botón **Correo** arriba a la izquierda; el chat y
> social disponen de sus propias ventanas). Las mecánicas siguientes han sido confirmadas contra el servidor.

## Correo

**Correo personal:**
- **Listar** correos, **abrir** un mensaje, **enviar** correo, **eliminar** un mensaje.
- **Recuento de nuevos** — cuántos mensajes no leídos tienes.
- **Carpetas** — ver **carpetas en uso**, **mover** un mensaje a una carpeta, **eliminar** una carpeta.

**Correo masivo (corporación):** enviado a toda tu corporación:
- **Enviar**, **listar**, **abrir**, **eliminar**, **recuento de nuevos**.

## Canales de chat

Los **canales** son salas de chat con nombre:

- **Crear** un canal, **unirse** a uno, **salir** de uno, **hablar** en él.
- **Listar** canales (todos, o solo los tuyos).
- **Moderación** (como propietario/oficial del canal): **expulsar (kick)**, **bloquear (ban)** / **desbloquear (unban)**, **establecer el
  rol de un miembro**, **silenciar globalmente (global mute)**, ver miembros **silenciados** / **bloqueados**.
- **Configuración**: **establecer contraseña**, **establecer tema**, preferencias de **notificaciones**.

**Chat directo** — un mensaje privado entre personajes.

## Amigos

- **Enviar solicitud de amistad**, **responder** a una, **confirmar** una solicitud pendiente.
- **Eliminar** un amigo, **bloquear** a un personaje.
- **Listar** tus amigos.

Bloquear a un personaje impide que comercie o te envíe mensajes (ver
[primeros pasos](/es/features/getting-started/) para el bloqueo de comercio por personaje).

## Relaciones (reputación / standings)

La **relación (standing)** es una reputación numérica entre entidades (personajes, corporaciones,
alianzas):

- **Listar** tus relaciones, ver el **historial de relaciones**.
- **Establecer relación** — donde esté permitido, definir un valor de relación. Restricciones:
  - el **objetivo** debe ser un personaje, una corporación (privada) o una alianza (privada),
  - el **origen** debe ser igualmente una entidad válida,
  - no puedes establecer una relación hacia ti mismo.
- **Relaciones predeterminadas** — las relaciones base para alianzas/corporaciones por defecto.

La relación es un valor de **-10 a +10** (0 = neutral, el valor predeterminado; asignar 0 borra la
entrada). La **reputación** de una entidad es el agregado de las relaciones de todos hacia ella.
Las relaciones positivas importan en situaciones concretas — p. ej., durante una [intrusión](/es/features/intrusion/)
una corporación con relación mutua ≥ 10 cuenta como un **aliado** cuya victoria en SAP no
daña tu base.

La relación influye en el trato que facciones y otros jugadores te dan a ti y a tu corporación
(ver [grupos](/es/features/groups/)).

## Páginas amarillas

Un directorio público (anuncios gestionados por corporaciones):
- **Obtener** un anuncio, **enviar** uno, **eliminar** uno, **buscar** en el directorio.

## Noticias y encuestas

- **Noticias** — ver **categorías** y la **lista de noticias**; **recuento de nuevas** para elementos no leídos.
- **Encuestas** — **ver** una encuesta y **responderla**.

## Notas prácticas

- **Correo vs. chat** — el correo es persistente y privado; los canales son salas grupales en tiempo real.
- **El correo masivo es una herramienta corporativa** — los oficiales lo usan para difundir mensajes a los miembros.
- **Las relaciones son direccionales** — la relación de A hacia B es independiente de la de B hacia A, y
  sigue a tu corporación.
- **El bloqueo es tu escudo** — bloquea a spammers o comerciantes hostiles.
- **Los canales se pueden bloquear** — las contraseñas y los roles regulan quién puede unirse/hablar.

<!-- Developer notes: Mails/* (list/open/send/delete/folders, mass-mail variants);
     Channels/* (create/join/leave/talk, moderation, password/topic); Socials/* (friend
     request/reply/confirm/delete/block/list); Chat.cs; Standings/SetStanding.cs
     (entity-category + private-corp/alliance constraints, self-excluded),
     StandingHistory.cs, GetStandingForDefault*.cs; Corporations/YellowPages/*;
     GetNews.cs / NewsCategory.cs / FreshNewsCount.cs; PollGet.cs / PollAnswer.cs. -->
