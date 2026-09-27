CREATE TABLE source (id TEXT PRIMARY KEY, body TEXT NOT NULL, acl TEXT NOT NULL, active INTEGER NOT NULL);
CREATE TABLE lexical_meta (id TEXT PRIMARY KEY, body_hash TEXT NOT NULL, acl TEXT NOT NULL, probe TEXT NOT NULL);
CREATE TABLE vector_meta (id TEXT PRIMARY KEY, body_hash TEXT NOT NULL, acl TEXT NOT NULL);
CREATE VIRTUAL TABLE lexical_fts USING fts5(id UNINDEXED, body);
INSERT INTO source VALUES ('doc-1','quartzalpha project guide','team-a',1);
INSERT INTO lexical_meta VALUES ('doc-1','34bd08ad98769e73073648f2246c5bf0d4963c40ba82107cfe229b9a28438cfe','team-a','quartzalpha');
INSERT INTO vector_meta VALUES ('doc-1','34bd08ad98769e73073648f2246c5bf0d4963c40ba82107cfe229b9a28438cfe','team-a');
INSERT INTO lexical_fts VALUES ('doc-1','quartzalpha project guide');
