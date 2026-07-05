"""
evidence.py
Génère un fichier texte structuré et horodaté, prêt à être envoyé
manuellement par l'utilisateur à Telegram (@notoscam) ou aux autorités
compétentes.

Ce module NE communique jamais avec l'API Telegram pour signaler un compte.
Il produit uniquement un document à usage humain.
"""

from datetime import datetime
import os

OUTPUT_DIR = "dossiers_generes"


def build_dossier(reporter_username: str, reporter_id: int, target: str,
                   description: str, extra_notes: str = "") -> str:
    """
    Construit le contenu texte du dossier et l'écrit sur disque.
    Retourne le chemin du fichier généré.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/dossier_{timestamp}_{reporter_id}.txt"

    content = f"""
==================================================
DOSSIER DE SIGNALEMENT - PREUVES DE HARCÈLEMENT
==================================================

Ce document a été généré automatiquement pour aider à documenter
un cas de harcèlement présumé sur Telegram. Il est destiné à être
transmis MANUELLEMENT par la personne concernée à :
  - Telegram : @notoscam ou via Réglages > Signaler dans l'application
  - Les autorités compétentes si nécessaire

Ce document ne constitue pas un signalement automatique et n'a été
envoyé à aucun tiers par le bot.

--------------------------------------------------
INFORMATIONS SUR LE DOSSIER
--------------------------------------------------
Date de génération (UTC)  : {datetime.utcnow().isoformat()}
Compte visé (uid/username): {target}

--------------------------------------------------
DÉCLARANT
--------------------------------------------------
Nom d'utilisateur Telegram : @{reporter_username or 'inconnu'}
ID Telegram                : {reporter_id}

--------------------------------------------------
DESCRIPTION DES FAITS
--------------------------------------------------
{description.strip()}

--------------------------------------------------
NOTES / PIÈCES JOINTES MENTIONNÉES
--------------------------------------------------
{extra_notes.strip() if extra_notes.strip() else "Aucune note supplémentaire."}

--------------------------------------------------
RAPPEL IMPORTANT
--------------------------------------------------
- Ce dossier doit être complété par des captures d'écran réelles
  des messages problématiques avant envoi.
- Un signalement précis et documenté a plus de chances d'être
  traité efficacement par les équipes de modération.
- En cas de danger immédiat, contactez les autorités locales.

==================================================
Fin du dossier
==================================================
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return filename
