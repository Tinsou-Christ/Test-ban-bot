"""
bot.py
Point d'entrée du bot. Lance le polling Telegram.

Variables d'environnement attendues :
- BOT_TOKEN : token du bot Telegram (obtenu via @BotFather)
- ADMIN_ID  : ID Telegram de l'administrateur (par défaut 8294554523)
- DAILY_LIMIT : nombre de dossiers autorisés par jour pour un utilisateur normal
"""

import os
import logging
from telegram.ext import Application, CommandHandler

import database as db
from handlers import user_handlers, admin_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("La variable d'environnement BOT_TOKEN est manquante.")

    db.init_db()

    app = Application.builder().token(token).build()

    # Commandes utilisateur
    app.add_handler(CommandHandler("start", user_handlers.start))
    app.add_handler(CommandHandler("aide", user_handlers.aide))
    app.add_handler(CommandHandler("mes_dossiers", user_handlers.mes_dossiers))
    app.add_handler(user_handlers.get_conversation_handler())

    # Commandes admin
    app.add_handler(CommandHandler("stats", admin_handlers.stats))
    app.add_handler(CommandHandler("leaderboard", admin_handlers.leaderboard))
    app.add_handler(CommandHandler("utilisateurs", admin_handlers.utilisateurs))
    app.add_handler(CommandHandler("ban", admin_handlers.ban))
    app.add_handler(CommandHandler("unban", admin_handlers.unban))
    app.add_handler(CommandHandler("adminhelp", admin_handlers.admin_help))

    logger.info("Bot démarré, en attente de messages...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
