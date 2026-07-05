"""
handlers/user_handlers.py
Commandes disponibles pour tout utilisateur du bot.

Flux principal :
  /nouveau -> demande le uid/username visé
           -> demande une description des faits
           -> génère un dossier texte et le renvoie à l'utilisateur

Une limite quotidienne (par défaut 10) s'applique à chaque utilisateur,
sauf à l'administrateur défini par ADMIN_ID (illimité).
"""

import os
from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)

import database as db
import evidence

ADMIN_ID = int(os.environ.get("ADMIN_ID", "8294554523"))
DAILY_LIMIT = int(os.environ.get("DAILY_LIMIT", "10"))

# États de la conversation
ASK_TARGET, ASK_DESCRIPTION = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.register_user(user.id, user.username or "")
    await update.message.reply_text(
        "👋 Bienvenue.\n\n"
        "Ce bot t'aide à *documenter* un cas de harcèlement Telegram : "
        "il génère un dossier texte structuré et horodaté que tu peux "
        "ensuite envoyer toi-même à Telegram (@notoscam) ou aux autorités.\n\n"
        "⚠️ Ce bot n'envoie aucun signalement automatique à Telegram.\n\n"
        "Commandes :\n"
        "/nouveau - créer un nouveau dossier de preuves\n"
        "/mes_dossiers - voir combien de dossiers tu as créés aujourd'hui\n"
        "/aide - afficher l'aide",
        parse_mode="Markdown"
    )


async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Aide*\n\n"
        "/nouveau - créer un dossier de preuves pour un compte qui te harcèle\n"
        "/annuler - annuler la création en cours\n"
        f"Limite : {DAILY_LIMIT} dossiers par jour par utilisateur.\n\n"
        "Une fois le dossier généré, envoie-le via l'app Telegram "
        "(Réglages > Signaler un problème, ou @notoscam) accompagné de "
        "captures d'écran réelles des messages en question.",
        parse_mode="Markdown"
    )


async def nouveau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.register_user(user.id, user.username or "")

    if db.is_banned(user.id):
        await update.message.reply_text("🚫 Tu n'es plus autorisé à utiliser ce bot.")
        return ConversationHandler.END

    if user.id != ADMIN_ID:
        used = db.get_today_count(user.id)
        if used >= DAILY_LIMIT:
            await update.message.reply_text(
                f"⏳ Limite quotidienne atteinte ({DAILY_LIMIT}/jour). "
                "Réessaie demain."
            )
            return ConversationHandler.END

    await update.message.reply_text(
        "📝 Envoie le *uid* ou le *@username* du compte concerné.\n"
        "Tape /annuler pour arrêter.",
        parse_mode="Markdown"
    )
    return ASK_TARGET


async def ask_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["target"] = update.message.text.strip()
    await update.message.reply_text(
        "✍️ Décris maintenant les faits le plus précisément possible "
        "(dates, contenu des messages, contexte). "
        "N'oublie pas de garder des captures d'écran de ton côté."
    )
    return ASK_DESCRIPTION


async def ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    description = update.message.text.strip()
    target = context.user_data.get("target", "inconnu")

    filepath = evidence.build_dossier(
        reporter_username=user.username,
        reporter_id=user.id,
        target=target,
        description=description
    )

    db.increment_usage(user.id)
    db.log_dossier(user.id, target, description)

    with open(filepath, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename=os.path.basename(filepath),
            caption=(
                "✅ Dossier généré.\n\n"
                "Envoie ce fichier, accompagné de tes captures d'écran, à :\n"
                "• Telegram : @notoscam ou Réglages > Signaler\n"
                "• Les autorités si nécessaire.\n\n"
                "Ce bot n'a rien envoyé à ta place."
            )
        )

    context.user_data.clear()
    return ConversationHandler.END


async def annuler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Création annulée.")
    return ConversationHandler.END


async def mes_dossiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    used = db.get_today_count(user.id)
    limite = "illimitée" if user.id == ADMIN_ID else str(DAILY_LIMIT)
    await update.message.reply_text(
        f"📊 Dossiers créés aujourd'hui : {used}\n"
        f"Limite quotidienne : {limite}"
    )


def get_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("nouveau", nouveau)],
        states={
            ASK_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_target)],
            ASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_description)],
        },
        fallbacks=[CommandHandler("annuler", annuler)],
    )
