# QuackChat — Backend (FastAPI)

## Démarrer en local

```bash
# 1) Créer et activer l'env (une fois)
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt

# 2) (optionnel) VSCode: sélectionner l'interpréteur .venv

# 3) Lancer en dev (rechargement + env)
uvicorn app.main:app --reload --port 8000 --env-file ./env/dev.env