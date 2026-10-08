# retrieval-index-parity

## Nouveau : mon index BM25 est-il réellement utilisé ?

`python3 bm25_plan.py demo --lang fr` montre en dix secondes un plan qui n’utilise pas l’index attendu, puis un plan qui l’utilise. Les captures sont **reconstruites** à partir du cas [Hindsight #5408](https://github.com/vectorize-io/hindsight/issues/5408) ; les temps affichés ne sont pas des mesures de cet outil. Pour une capture réelle de `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` sur une requête SELECT que vous contrôlez :

```sh
python3 bm25_plan.py check plan.json --index idx_memory_units_text_search --catalog indexes.json --lang fr
```

`indexes.json` est un tableau JSON de noms d’index ou de lignes `pg_indexes` avec `indexname`. Sans ce catalogue, l’outil constate seulement que l’index n’apparaît pas dans l’exécution ; il ne prouve pas son existence. Codes de sortie : 0 utilisé, 2 non utilisé, 3 capture incomplète ou index absent du catalogue, 1 entrée invalide. Aucun accès à PostgreSQL n’est effectué et aucun texte de requête n’est imprimé. Un plan ne suffit pas à expliquer *pourquoi* le planificateur a choisi un autre chemin.

**Projets voisins :** [Hindsight](https://github.com/vectorize-io/hindsight) utilise la recherche BM25 dans ce cas ; [VectorChord BM25](https://github.com/supervc-stack/VectorChord-bm25) fournit l’index. Ce contrôle indépendant lit des plans exportés, sans intégration directe ni affiliation.

## Nouveau : frontière des groupes Leviathan

`python3 tenant_scope.py tenant-demo --lang fr` montre une réponse d’un autre client dans une recherche stricte (démo réussie : code 0). Pour la sortie réelle de `leviathan --json search`, utilisez `python3 tenant_scope.py check search.json --leviathan --group customer-a --policy strict --lang fr`. La politique `labeled_fallback` autorise les résultats `other_groups` si chaque carte porte `other_group: true`. Le mode sans `--leviathan` accepte le format normalisé `{requested_group, policy, results:[{group,label}]}`. Il contrôle une capture, pas les ACL en amont ; ne concluez pas à une fuite à partir du repli documenté.

**Projet voisin :** [Leviathan](https://github.com/elstongun/leviathan) expose un repli `OTHER CUSTOMER` explicite. Cette commande lit sa sortie JSON, sans affiliation ni correctif de Leviathan.

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
