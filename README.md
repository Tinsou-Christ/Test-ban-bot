# Harassment Report Bot 🛡️

Bot Telegram qui aide les victimes de harcèlement à **documenter** les faits :
il génère un dossier texte structuré et horodaté, prêt à être envoyé
**manuellement** à Telegram (@notoscam) ou aux autorités compétentes.

## ⚠️ Ce que ce bot NE fait PAS

Ce bot n'envoie **aucun signalement automatique** à Telegram. Il ne contacte
aucune API de modération. Il produit uniquement un document texte que
l'utilisateur transmet lui-même, avec ses propres captures d'écran, aux
canaux officiels de signalement.

## Fonctionnalités utilisateur

- `/start` — présentation du bot
- `/nouveau` — créer un dossier de preuves (uid/username visé + description des faits)
- `/mes_dossiers` — voir son usage du jour
- `/aide` — aide

Limite : **10 dossiers par jour** par utilisateur (configurable via `DAILY_LIMIT`).

## Fonctionnalités admin

L'utilisateur dont l'ID correspond à `ADMIN_ID` a accès à :

- `/stats` — nombre total d'utilisateurs et de dossiers générés
- `/leaderboard` — classement des utilisateurs les plus actifs
- `/utilisateurs` — liste des utilisateurs enregistrés
- `/ban <id>` / `/unban <id>` — gérer l'accès au bot
- Usage **illimité** de `/nouveau` (pas de limite quotidienne)

## Installation locale

```bash
git clone <ton-repo>
cd harassment-report-bot
pip install -r requirements.txt
cp .env.example .env
# édite .env avec ton BOT_TOKEN (obtenu via @BotFather)
python bot.py
```

## Déploiement sur Render.com

1. Pousse ce projet sur GitHub.
2. Sur Render, crée un nouveau **Background Worker** (ou utilise `render.yaml`
   avec "New > Blueprint").
3. Renseigne la variable d'environnement `BOT_TOKEN` (le reste est déjà
   configuré dans `render.yaml`).
4. Déploie. Le bot tourne en polling, aucune configuration de port nécessaire.

## Structure du projet

```
harassment-report-bot/
├── bot.py                     # point d'entrée
├── database.py                # SQLite : utilisateurs, usage, dossiers
├── evidence.py                # génération du dossier texte
├── handlers/
│   ├── user_handlers.py       # commandes utilisateur
│   └── admin_handlers.py      # commandes admin
├── requirements.txt
├── render.yaml
├── .env.example
└── .gitignore
```
