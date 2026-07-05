"""
handlers/admin_handlers.py
Commandes réservées à l'administrateur (ADMIN_ID).

Privilèges admin :
- /stats        : nombre total d'utilisateurs et de dossiers créés
- /leaderboard  : classement des utilisateurs les plus actifs
- /utilisateurs : liste des utilisateurs enregistrés
- /ban <id>     : bannir un utilisateur du bot
- /unban <id>   : débannir un utilisateur
- illimité sur /nouveau (déjà géré dans user_handlers.py)
"""

import os
from telegram import Update
from telegram.ext import ContextTypes

import database as db

ADMIN_ID = int(os.environ.get("ADMIN_ID", "8294554523"))


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("🚫 Commande réservée à l'administrateur.")
            return
        return await func(update, context)
    return wrapper


@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = db.count_users()
    total_dossiers = db.count_dossiers()
    await update.message.reply_text(
        "📈 *Statistiques du bot*\n\n"
        f"👥 Utilisateurs enregistrés : {total_users}\n"
        f"📁 Dossiers générés au total : {total_dossiers}",
        parse_mode="Markdown"
    )


@admin_only
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.get_leaderboard(10)
    if not rows:
        await update.message.reply_text("Aucun dossier créé pour l'instant.")
        return

    lines = ["🏆 *Leaderboard - utilisateurs les plus actifs*\n"]
    for i, row in enumerate(rows, start=1):
        uname = f"@{row['username']}" if row["username"] else f"id:{row['user_id']}"
        lines.append(f"{i}. {uname} — {row['total']} dossier(s)")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


@admin_only
async def utilisateurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.get_all_users()
    if not rows:
        await update.message.reply_text("Aucun utilisateur enregistré.")
        return

    lines = ["👥 *Utilisateurs enregistrés*\n"]
    for row in rows[:50]:  # on limite l'affichage à 50 pour éviter un message trop long
        uname = f"@{row['username']}" if row["username"] else "inconnu"
        statut = "🚫 banni" if row["is_banned"] else "✅ actif"
        lines.append(f"{row['user_id']} - {uname} - {statut}")

    if len(rows) > 50:
        lines.append(f"\n... et {len(rows) - 50} autre(s).")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


@admin_only
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage : /ban <user_id>")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("L'ID doit être un nombre.")
        return

    db.set_banned(target_id, True)
    await update.message.reply_text(f"🚫 Utilisateur {target_id} banni du bot.")


@admin_only
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage : /unban <user_id>")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("L'ID doit être un nombre.")
        return

    db.set_banned(target_id, False)
    await update.message.reply_text(f"✅ Utilisateur {target_id} débanni.")


@admin_only
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ *Commandes admin*\n\n"
        "/stats - statistiques globales\n"
        "/leaderboard - classement des utilisateurs actifs\n"
        "/utilisateurs - liste des utilisateurs\n"
        "/ban <id> - bannir un utilisateur\n"
        "/unban <id> - débannir un utilisateur\n"
        "/adminhelp - cette aide",
        parse_mode="Markdown"
    )
