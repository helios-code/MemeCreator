# Dossier de données

Ce dossier contient les données persistantes utilisées par le générateur de mèmes "L'ARROGANCE!".

## Contenu

- `quality_data.db` : Base de données SQLite contenant les punchlines générées et leurs évaluations
  - Table `punchlines` : Stocke les punchlines générées avec leurs scores de qualité
  - Table `stats` : Stocke des statistiques agrégées sur les punchlines

## Sauvegarde

Il est recommandé de sauvegarder régulièrement ce dossier, en particulier le fichier `quality_data.db`, car il contient l'historique des punchlines générées et leurs évaluations.

## Restauration

Pour restaurer une sauvegarde, il suffit de remplacer le fichier `quality_data.db` par la version sauvegardée. 