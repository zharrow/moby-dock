# 🐳 TP CI/CD — Moby Dock

Monorepo **backend + frontend** conteneurisé, orchestré avec **Docker Compose** et
livré par une **pipeline GitHub Actions** qui build, tague et pousse les images sur
**Docker Hub**.

La mini-app « Moby Dock » est un petit port de conteneurs : des **baleines** 🐳
transportent des **conteneurs**. CRUD complet côté API.

## Stack

| Couche    | Techno                                   |
|-----------|------------------------------------------|
| Frontend  | React + Vite, servi par **Nginx**        |
| Backend   | **FastAPI** (Python 3.12) + SQLAlchemy   |
| Base      | **PostgreSQL 16**                        |
| Orchestr. | **Docker Compose**                       |
| CI/CD     | **GitHub Actions** → Docker Hub          |

## Arborescence

```
.
├── backend/                # API FastAPI + CRUD
│   ├── app/
│   │   ├── main.py         # routes (CRUD whales + containers)
│   │   ├── models.py       # 2 tables : whales, containers
│   │   ├── schemas.py      # validation Pydantic
│   │   └── database.py     # connexion Postgres
│   └── Dockerfile          # multi-stage (wheels → runtime slim)
├── frontend/               # UI React (Vite)
│   ├── src/
│   ├── nginx.conf          # SPA + proxy /api → backend
│   └── Dockerfile          # multi-stage (build Vite → Nginx)
├── docker-compose.yml      # db + backend + frontend
└── .github/workflows/ci.yml# pipeline build + tag + push
```

## Lancer en local

```bash
docker compose up --build
```

- Frontend : <http://localhost:8080>
- API : <http://localhost:8000/api/health> — docs Swagger : <http://localhost:8000/docs>

La base est initialisée automatiquement (tables + données de démo) au démarrage du backend.

## Le modèle de données (2 tables)

- **whales** — `id`, `name`, `emoji`
- **containers** — `id`, `name`, `image`, `status` (`running`/`stopped`/`exited`), `whale_id` → `whales.id`

## API (CRUD)

| Méthode  | Route                              | Rôle                                   |
|----------|------------------------------------|----------------------------------------|
| `GET`    | `/api/health`                      | Santé du service                       |
| `GET`    | `/api/whales`                      | Liste des baleines                     |
| `POST`   | `/api/whales`                      | Créer une baleine                      |
| `DELETE` | `/api/whales/{id}`                 | Supprimer une baleine (+ ses conteneurs)|
| `GET`    | `/api/containers`                  | Liste des conteneurs                   |
| `GET`    | `/api/containers/{id}`             | Détail d'un conteneur                  |
| `POST`   | `/api/containers`                  | Créer un conteneur                     |
| `PUT`    | `/api/containers/{id}`             | Modifier un conteneur                  |
| `POST`   | `/api/containers/{id}/restart`     | Relancer (status → running)            |
| `DELETE` | `/api/containers/{id}`             | Supprimer un conteneur                 |

## Pipeline CI/CD

À chaque `push` sur `main`, GitHub Actions construit les **deux images** (matrice
backend + frontend), les **tague** et les **pousse** sur Docker Hub.

Tags générés :
- `latest` (sur la branche par défaut)
- `sha-<commit>` (traçabilité)
- `vX.Y.Z` / `X.Y` (quand on pousse un tag git `v*`)

### Secrets à configurer (Settings → Secrets and variables → Actions)

| Secret               | Valeur                                              |
|----------------------|-----------------------------------------------------|
| `DOCKERHUB_USERNAME` | ton identifiant Docker Hub                          |
| `DOCKERHUB_TOKEN`    | un *Access Token* Docker Hub (Account → Security)   |

Images publiées : `DOCKERHUB_USERNAME/moby-dock-backend` et `DOCKERHUB_USERNAME/moby-dock-frontend`.

## Multi-stage : pourquoi

- **Backend** : étape *builder* compile les dépendances en `wheels`, l'image finale
  (`runtime`) n'embarque que le strict nécessaire (pas de toolchain) → image légère,
  utilisateur non-root.
- **Frontend** : étape *builder* (Node) compile l'app Vite, l'image finale (`nginx`)
  ne contient que les fichiers statiques → pas de Node en production.
