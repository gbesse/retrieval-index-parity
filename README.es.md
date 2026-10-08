# retrieval-index-parity

## Nuevo: ¿se utiliza realmente mi índice BM25?

`python3 bm25_plan.py demo --lang es` muestra un plan que no usa el índice esperado y otro que sí lo usa. Las capturas se han **reconstruido** a partir de [Hindsight #5408](https://github.com/vectorize-io/hindsight/issues/5408); los tiempos mostrados no son mediciones realizadas por esta herramienta. Para una captura real de `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` sobre una consulta SELECT que controle:

```sh
python3 bm25_plan.py check plan.json --index idx_memory_units_text_search --catalog indexes.json --lang es
```

`indexes.json` es una lista JSON de nombres de índices o de filas `pg_indexes` con `indexname`. Sin ese catálogo, la herramienta solo observa que el índice no aparece en la ejecución; no demuestra que exista. Códigos de salida: 0 utilizado, 2 no utilizado, 3 captura incompleta o índice ausente del catálogo, 1 entrada no válida. No se conecta a PostgreSQL ni imprime la consulta. Un plan por sí solo no explica *por qué* el planificador eligió otra ruta.

**Proyectos relacionados:** [Hindsight](https://github.com/vectorize-io/hindsight) utiliza la búsqueda BM25 en este caso; [VectorChord BM25](https://github.com/supervc-stack/VectorChord-bm25) proporciona el índice. Este control independiente lee planes exportados, sin integración directa ni afiliación.

## Nuevo: límite de grupos de Leviathan

`python3 tenant_scope.py tenant-demo --lang es` muestra un resultado de otro cliente en una búsqueda estricta (la demo correcta sale con código 0). Para la salida real de `leviathan --json search`, ejecute `python3 tenant_scope.py check search.json --leviathan --group customer-a --policy strict --lang es`. La política `labeled_fallback` permite `other_groups` solo si cada tarjeta tiene `other_group: true`. Sin `--leviathan`, el formato normalizado es `{requested_group, policy, results:[{group,label}]}`. Comprueba una captura, no las ACL previas; el repliegue documentado no demuestra por sí mismo una filtración.

**Proyecto relacionado:** [Leviathan](https://github.com/elstongun/leviathan) expone un repliegue `OTHER CUSTOMER` explícito. Esta orden lee su salida JSON, sin afiliación ni parche para Leviathan.

Comprueba ID, huellas y ACL entre fuente, FTS5 y metadatos vectoriales.

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Proyectos relacionados

- [sqlite-fts5-check — divergencia interna de FTS5](https://github.com/agentscope-ai-java/sqlite-fts5-check)
- [rag-staleness-check — documentos obsoletos en índices](https://pypi.org/project/rag-staleness-check/)
- [Truffler — búsqueda híbrida con etiquetas](https://github.com/kieranklaassen/truffler)

Estos proyectos documentan la necesidad o cubren parte del problema. No se afirma ninguna afiliación ni integración con ellos.

## Inicio rápido

```bash
python3 tool.py demo
python3 tool.py check examples/healthy.sql
```

Python 3.11+; no external package required. / Python 3.11+ ; aucune dépendance externe. / Python 3.11+; sin dependencias externas.

## Alcance actual

El comparador SQLite verifica ID activos, eliminaciones, huellas y ACL entre fuente y metadatos FTS y vectoriales, además de una búsqueda FTS5 por término testigo. Todavía no consulta un índice vectorial real.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```

## Licencia

MIT.
