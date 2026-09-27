# retrieval-index-parity

Contrôle la parité des identifiants, empreintes et ACL entre source, FTS5 et métadonnées vectorielles.

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Projets voisins

- [sqlite-fts5-check — dérive interne FTS5](https://github.com/agentscope-ai-java/sqlite-fts5-check)
- [rag-staleness-check — documents périmés dans des index](https://pypi.org/project/rag-staleness-check/)
- [Truffler — recherche hybride avec labels](https://github.com/kieranklaassen/truffler)

Ces projets documentent le besoin ou couvrent une partie du problème. Aucun lien d’affiliation ni intégration avec eux n’est revendiqué.

## Démarrer

```bash
python3 tool.py demo
python3 tool.py check examples/healthy.sql
```

Python 3.11+; no external package required. / Python 3.11+ ; aucune dépendance externe. / Python 3.11+; sin dependencias externas.

## Portée actuelle

Le comparateur SQLite vérifie les identifiants actifs, tombstones, empreintes et ACL de la source, des métadonnées FTS et vectorielles, ainsi qu’une recherche FTS5 par terme témoin. Il ne cherche pas encore dans un index vectoriel réel.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Licence

MIT.
