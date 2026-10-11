# `tests/golden/` — copias congeladas de las salidas

Qué es: una foto de `data/processed/tabla_normalizada.xlsx`,
`vista_plana_tabla_consolidada.xlsx` y `data/interim/revision_duplicados.xlsx` en un
momento dado. `06_verificar` compara las salidas actuales contra esta foto, hoja por
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

**Al 2026-09-18 el snapshot está atrasado y `06_verificar` falla siempre.** Se agregaron
columnas a las salidas (`lat`/`lon` en `Ciudades`, por `04d_coordenadas`; `Imagen` en la
vista plana, por `04c_vincular_imagenes`) y el golden nunca se re-congeló:

```
tabla_normalizada.xlsx        [Ciudades] shape (78, 6) != golden (78, 4)
vista_plana_consolidada.xlsx  [Objetos - Concursos Tucumán] shape (982, 10) != golden (982, 7)
```

El resto de las hojas da OK. Mientras siga así, esta carpeta no cumple su función: un
cambio del pipeline que mueva una salida no se va a notar, porque la etapa 06 ya viene
fallando. Re-congelarlo —en un commit propio, con estas dos líneas como justificación—
es el primer paso antes de encarar las tareas de `docs/tareas_pendientes.md`.
