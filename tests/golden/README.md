# `tests/golden/` — copias congeladas de las salidas

Qué es: una foto de `data/processed/tabla_normalizada.xlsx` y
`vista_plana_tabla_consolidada.xlsx` en un momento dado. (Hasta 2026-10-25 también
guardaba `revision_duplicados.xlsx`, que es un insumo anotado y no una salida: se quitó.) `06_verificar` compara las salidas actuales contra esta foto, hoja por
hoja, y reporta las celdas que difieren.

**No es un test.** Un test afirma qué tiene que pasar; esto solo avisa si algo cambió.
Sirve exactamente para una cosa: detectar que un cambio en el pipeline movió una salida
sin que vos lo quisieras.

## La regla que lo hace útil

Vale como verificación **solo si el golden no se actualiza en el mismo commit que
cambia el pipeline**. Si se re-congela junto con la salida, `06_verificar` compara la
salida contra sí misma y no puede fallar nunca.

Cuando un cambio del pipeline modifica legítimamente una salida:

1. Commit A — el cambio en `src/pipeline/`, con `06_verificar` fallando y el diff a la
   vista.
2. Commit B — re-congelar el golden (`cp data/processed/*.xlsx tests/golden/`), con un
   mensaje que diga **por qué** cambió.

Dos commits, no uno. Así el `git log` conserva la evidencia de qué se movió y por qué.

## Estado

Snapshot a mitad de normalización: las decisiones de `docs/tareas_pendientes.md` todavía
no están aplicadas. Que `06_verificar` dé OK significa "nada cambió desde la última vez",
no "los datos están bien".

**Estado al 2026-10-25: desactualizado, y por eso `06_verificar` falla siempre.** El
golden es del 2026-09 y nunca se re-congeló: desde entonces las salidas sumaron
columnas (`lat`/`lon` y la ubicación de provincia en `Ciudades`; las marcas de
`04f` y `foto_album` en `Objetos`; la hoja `Premios` curada de `04e`; varias columnas en
la vista plana) y cambiaron filas (fusiones de expositoras, índice de páginas corregido):

```
tabla_normalizada.xlsx        [Expositoras] shape (459, 3) != golden (472, 3)
                              [Ciudades] shape (78, 10) != golden (78, 4)
                              [Objetos] shape (982, 12) != golden (982, 9)
                              [Premios] shape (103, 20) != golden (105, 17)
                              [Paginas_Catalogo] 5 celdas distintas
vista_plana_consolidada.xlsx  [Objetos - Concursos Tucumán] shape (982, 18) != golden (982, 7)
```

`Concursos`, `Categorías` y `Fuentes` dan OK. Re-congelarlo en un commit propio es una
tarea pendiente (`docs/tareas_pendientes.md`).

Mientras siga así, esta carpeta no cumple su función: un cambio del pipeline que mueva
una salida no se va a notar, porque la etapa 06 ya viene fallando.
