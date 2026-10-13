---
title: "Configuración de PC y cliente"
description: "Ejecución del cliente en Windows y Linux, uso de varias cuentas dentro de las normas, escalado de la interfaz y ejecución sin derechos de administrador."
weight: 24
---

# Configuración de PC y cliente

Notas prácticas para ejecutar el cliente de Perpetuum.

## Las normas primero

El uso de varias cuentas simultáneas (varios clientes controlando varios personajes) está permitido
**dentro de unos límites**. Reglas de juego limpio que debes conocer antes de hacerlo:

- **Prohibido el software de automatización o de control multicliente** — terminantemente.
- **No más de 5 cuentas activas simultáneamente.**
- Ninguna cuenta registrada con correos electrónicos falsos, inválidos o inaccesibles —
  la dirección debe ser de tu propiedad.

Las infracciones pueden conllevar un bloqueo inmediato y permanente.

## Windows: varios clientes

1. Instala el cliente de Perpetuum en Steam.
2. Comprueba que la carpeta del juego contiene un archivo `steam_appid.txt` cuyo contenido sea
   `223410`.
3. Copia toda la carpeta `Perpetuum` una vez por cada cliente adicional.
4. Ejecuta `Perpetuum.exe` en cada copia (opcionalmente añade las copias a Steam como
   juegos que no son de Steam).

**Espacio en disco:** `Layers.gbf` y `Perpetuum.gbf` son archivos grandes e idénticos en
cada copia — haz enlaces simbólicos (`mklink`) o accesos directos para que solo se
almacenen una vez.

## Linux: varios clientes

Cada copia del cliente necesita una **versión diferente de Proton**, o se negará a ejecutarse:

1. Instala Steam y Perpetuum de la forma habitual; verifica `steam_appid.txt` (`223410`).
2. Copia la carpeta `Perpetuum` para cada cliente.
3. Con la sesión iniciada en Steam, instala varias versiones recientes de Proton (a través de Steam,
   manualmente o mediante compilaciones GloriousEggroll).
4. Añade cada copia a Steam como un juego que no es de Steam apuntando a su `Perpetuum.exe`.
5. Fuerza una **versión diferente de Proton** para cada copia en sus parámetros de lanzamiento.
6. Inicia primero la aplicación real de Steam y luego ejecuta las copias.

Resolución de problemas:

- Seleccionar una versión de Proton **no** la instala; debes iniciar el
  juego una vez teniéndola seleccionada.
- Si la aplicación real de Steam no se inicia, iníciala primero en modo seguro.
- Desde Proton 5.0, la emulación de DirectX 9/12 se ejecuta sobre **Vulkan**. ¿No tienes
  una GPU compatible con Vulkan? Añade `PROTON_USE_WINED3D=1 %command%` a los parámetros
  de lanzamiento de cada copia.
- Cuadro de texto vacío con advertencia roja: instala `libfreetype6:i386`
  (distribuciones basadas en Debian/Ubuntu).

## Escalado de la interfaz de usuario

El cliente utiliza una interfaz de píxeles fijos sin escalado dinámico. Soluciones provisionales:

- **Pantalla completa a baja resolución** — pasa a pantalla completa a una resolución inferior a la de tu
  pantalla y deja que la interfaz se estire para llenarla (los modos en ventana y sin bordes
  siempre utilizan la resolución nativa). Reducir la propia resolución de la pantalla produce
  el mismo efecto.
- **Aplicaciones de escalado de interfaz** — p. ej., Lossless Scaling (Steam, Windows): ejecuta el cliente
  en ventana a tu tamaño base, establece una escala personalizada en la aplicación, activa
  el escalado y enfoca la ventana del cliente. Ten en cuenta la habitual pérdida de nitidez del texto.
- **Lupa del sistema operativo** — la Lupa de Windows (o equivalente) para lecturas
  detalladas puntuales.

## Ejecución sin derechos de administrador

1. Copia los archivos del cliente fuera de la carpeta de Steam a una ubicación con permisos de escritura.
2. Crea allí un archivo `Perpetuum.bat` que contenga
   `cmd /min /C "set __COMPAT_LAYER=RUNASINVOKER && start Perpetuum.exe"`.
3. Inicia el juego a través del archivo por lotes (.bat).

<!--
Developer notes: rewritten 2026 in original prose. An earlier version was adapted from the
Open Perpetuum community wiki (perpetuum.miraheze.org: Multi-Boxing, Linux
Setup, Client UI Scaling, Launching without Admin Rights); that text was
fully replaced, not reused. These are client-side procedures for the retail Steam client build;
nothing here is verifiable from this server's backend, and no server feature is
claimed. The Reshader (graphics mod) was intentionally left out: it targets the
retail client build and is not an OPP-server feature.
-->
