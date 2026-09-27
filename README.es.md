# retrieval-index-parity

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
