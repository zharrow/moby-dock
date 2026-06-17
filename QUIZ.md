# 🧪 QUIZ DE RÉVISION — Docker, Compose & CI/CD

> Auto-test pour le devoir écrit. Essaie de répondre **avant** de déplier la réponse.
> Sur GitHub, clique sur « ▸ Réponse » pour la révéler.

---

## A. Concepts de base

**A1.** Quelle est la différence entre une **image** et un **conteneur** ?
<details><summary>▸ Réponse</summary>

Une **image** est un gabarit figé et inerte (la recette + l'appli + ses dépendances).
Un **conteneur** est une **instance de cette image en cours d'exécution**. Une image = la
recette, un conteneur = le plat servi. On peut lancer plusieurs conteneurs d'une même image.
</details>

**A2.** À quoi sert un **Dockerfile** ?
<details><summary>▸ Réponse</summary>

C'est le **fichier de recette** qui décrit comment construire une image, via une suite
d'instructions (`FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, `CMD`…).
</details>

**A3.** Qu'est-ce qu'un **registry** ? Donne un exemple.
<details><summary>▸ Réponse</summary>

Un entrepôt d'images Docker en ligne, où on **push** (envoie) et **pull** (récupère) des
images. Exemple : **Docker Hub** (aussi GitHub Container Registry, AWS ECR…).
</details>

**A4.** Que signifie le **tag** d'une image (ex. `studioflow/moby-dock-backend:latest`) ?
<details><summary>▸ Réponse</summary>

Le tag (`:latest`, `:v1.0`, `:sha-18486b4`) est une **étiquette de version** sur l'image.
Format complet : `registry/utilisateur/nom-image:tag`. Sans tag précisé, Docker utilise
`latest` par défaut.
</details>

**A5.** Qu'est-ce qu'un **monorepo** et quel intérêt ici ?
<details><summary>▸ Réponse</summary>

Un **seul dépôt Git** contenant plusieurs projets (ici `backend/` + `frontend/`). Intérêt :
versionner back et front ensemble, une seule pipeline, cohérence des changements.
</details>

---

## B. Multi-stage (très souvent demandé)

**B1.** Qu'est-ce qu'un build **multi-stage** ?
<details><summary>▸ Réponse</summary>

Un Dockerfile avec **plusieurs étapes `FROM`**. On construit/compile dans une 1ʳᵉ étape
(« builder », avec les outils lourds), puis on **copie seulement le résultat** dans une
2ᵉ étape minimale qui devient l'image finale.
</details>

**B2.** Pourquoi utiliser le multi-stage ? (2 raisons)
<details><summary>▸ Réponse</summary>

1. **Image finale plus légère** (on n'embarque pas les outils de build, Node, compilateurs…).
2. **Plus sûre** : moins de logiciels = moins de failles potentielles ; pas de code source
   ni de secrets de build dans l'image livrée.
</details>

**B3.** Dans notre frontend, que contient l'image **finale** et qu'est-ce qui a disparu ?
<details><summary>▸ Réponse</summary>

L'image finale contient **Nginx + les fichiers statiques compilés** (`/app/dist`). **Node et
les `node_modules` ont disparu** : ils n'existaient que dans l'étape `builder`. Résultat ~21 Mo.
</details>

**B4.** À quoi sert l'instruction `COPY --from=builder ...` ?
<details><summary>▸ Réponse</summary>

À copier des fichiers **depuis une étape précédente** (nommée `AS builder`) vers l'étape
courante. C'est le mécanisme qui permet de récupérer uniquement le résultat du build.
</details>

---

## C. Docker Compose

**C1.** À quoi sert Docker Compose ?
<details><summary>▸ Réponse</summary>

À définir et lancer **plusieurs conteneurs ensemble** avec un seul fichier
`docker-compose.yml` et une seule commande (`docker compose up`). Idéal pour une stack
multi-services (db + backend + frontend).
</details>

**C2.** Dans notre projet, quels sont les **3 services** et comment communiquent-ils ?
<details><summary>▸ Réponse</summary>

`db` (PostgreSQL), `backend` (FastAPI), `frontend` (Nginx). Ils sont sur un **réseau Docker
commun** créé par Compose : ils se joignent par leur **nom de service** (ex. le backend
parle à `db:5432`, Nginx proxifie vers `backend:8000`).
</details>

**C3.** À quoi sert `depends_on` avec `condition: service_healthy` ?
<details><summary>▸ Réponse</summary>

À **ordonner le démarrage** : le backend n'attend pas seulement que la base soit *lancée*,
mais qu'elle soit **réellement prête** (healthcheck `pg_isready` OK), pour éviter de se
connecter trop tôt.
</details>

**C4.** À quoi sert un **volume** (`pgdata`) dans le compose ?
<details><summary>▸ Réponse</summary>

À **conserver les données** de la base en dehors du conteneur. Sans volume, supprimer le
conteneur effacerait la base. Avec, les données survivent à un `docker compose down`.
</details>

**C5.** Différence entre `docker compose down` et `docker compose down -v` ?
<details><summary>▸ Réponse</summary>

`down` arrête et supprime les conteneurs/réseaux mais **garde les volumes** (données
conservées). `down -v` supprime **aussi les volumes** → la base est effacée.
</details>

**C6.** Que veut dire `ports: "8080:80"` ?
<details><summary>▸ Réponse</summary>

`port_machine:port_conteneur`. Le port **80 dans le conteneur** est exposé sur le port
**8080 de ta machine**. On y accède via http://localhost:8080.
</details>

---

## D. CI/CD & GitHub Actions

**D1.** Que veulent dire **CI** et **CD** ?
<details><summary>▸ Réponse</summary>

**CI** = *Continuous Integration* (intégration continue) : build + tests automatiques à
chaque commit. **CD** = *Continuous Delivery/Deployment* : publication/déploiement
automatique des artefacts (ici, push des images sur Docker Hub).
</details>

**D2.** Cite la hiérarchie d'un workflow GitHub Actions.
<details><summary>▸ Réponse</summary>

**Workflow** → déclenché par un événement (`on:`) → contient un ou plusieurs **jobs** →
chaque job contient des **steps** (étapes). Un job tourne sur une machine (`runs-on`).
</details>

**D3.** Quels événements déclenchent notre pipeline ?
<details><summary>▸ Réponse</summary>

`push` sur la branche `main`, `push` d'un **tag** `v*`, et les **pull requests** vers `main`
(sur PR, on build mais on **ne push pas**).
</details>

**D4.** Pourquoi ne **pousse-t-on pas** les images sur une pull request ?
<details><summary>▸ Réponse</summary>

Une PR sert à **valider** du code pas encore intégré. On vérifie juste que les images
**se construisent**, sans polluer Docker Hub avec des versions non validées.
</details>

**D5.** Qu'est-ce qu'un **secret** GitHub et pourquoi l'utiliser ?
<details><summary>▸ Réponse</summary>

Une valeur sensible (identifiant, token) **stockée chiffrée** dans GitHub et injectée dans
la pipeline via `${{ secrets.NOM }}`. Ça évite d'**écrire les identifiants en clair** dans
le code. Ici : `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN`.
</details>

**D6.** À quoi sert la **matrice** (`strategy: matrix`) dans notre pipeline ?
<details><summary>▸ Réponse</summary>

À exécuter le **même job plusieurs fois avec des paramètres différents**. Ici : une fois
pour le `backend`, une fois pour le `frontend`, sans dupliquer le code du workflow.
</details>

**D7.** Quels tags notre pipeline génère-t-elle, et à quoi sert `sha-xxxxxxx` ?
<details><summary>▸ Réponse</summary>

`latest` (sur `main`), `sha-<commit>` (à chaque push), et `vX.Y.Z` / `X.Y` (sur tag git).
Le tag `sha-xxxxxxx` permet de **tracer exactement quel commit** a produit une image donnée
(reproductibilité / debug).
</details>

---

## E. Lecture de commandes (« quelle commande pour… »)

**E1.** Construire l'image du dossier courant et la nommer `api` ?
<details><summary>▸ Réponse</summary>

`docker build -t api .`
</details>

**E2.** Lancer toute la stack en arrière-plan en reconstruisant les images ?
<details><summary>▸ Réponse</summary>

`docker compose up -d --build`
</details>

**E3.** Voir les logs en direct du service `backend` ?
<details><summary>▸ Réponse</summary>

`docker compose logs -f backend`
</details>

**E4.** Se connecter à Docker Hub puis envoyer une image ?
<details><summary>▸ Réponse</summary>

`docker login -u studioflow` puis `docker push studioflow/moby-dock-backend:latest`
</details>

**E5.** Relier un dépôt local à GitHub et tout envoyer sur `main` ?
<details><summary>▸ Réponse</summary>

`git remote add origin <url>` puis `git push -u origin main`
</details>

**E6.** Ouvrir un terminal interactif dans un conteneur qui tourne ?
<details><summary>▸ Réponse</summary>

`docker exec -it <conteneur> sh` (ou `bash` si dispo dans l'image)
</details>

---

## F. Débogage (les erreurs qu'on a vécues)

**F1.** La pipeline affiche `Username and password required`. Cause et solution ?
<details><summary>▸ Réponse</summary>

Les **secrets Docker Hub manquent**. Solution : ajouter `DOCKERHUB_USERNAME` et
`DOCKERHUB_TOKEN` dans Settings → Secrets and variables → Actions.
</details>

**F2.** La pipeline échoue avec `401 Unauthorized: access token has insufficient scopes`. Cause ?
<details><summary>▸ Réponse</summary>

Le **token Docker Hub est en lecture seule**. Le `push` exige un token avec les droits
**Read & Write**. Solution : régénérer un token avec ces droits et mettre à jour le secret.
</details>

**F3.** `npm ci` échoue dans le Dockerfile. Pourquoi ?
<details><summary>▸ Réponse</summary>

`npm ci` exige un fichier **`package-lock.json`** présent. Solution : générer le lock avec
`npm install` (et le versionner).
</details>

**F4.** Après un `docker compose down -v`, les données ont disparu. Normal ?
<details><summary>▸ Réponse</summary>

Oui : `-v` supprime les **volumes**, donc la base. Pour conserver les données, faire
`docker compose down` **sans** `-v`.
</details>

---

## G. Spécifique à notre projet « Moby Dock »

**G1.** Quelles sont les 2 tables et leur relation ?
<details><summary>▸ Réponse</summary>

`whales` (les baleines) et `containers` (les conteneurs). Relation **un-à-plusieurs** : une
baleine possède plusieurs conteneurs (`containers.whale_id` → `whales.id`).
</details>

**G2.** Que veut dire CRUD et à quelles méthodes HTTP ça correspond ?
<details><summary>▸ Réponse</summary>

**C**reate = `POST`, **R**ead = `GET`, **U**pdate = `PUT` (ou `PATCH`), **D**elete =
`DELETE`.
</details>

**G3.** Comment le frontend (Nginx) atteint-il l'API sans problème de CORS ?
<details><summary>▸ Réponse</summary>

Nginx **proxifie** les requêtes commençant par `/api` vers le service `backend:8000`
(directive `location /api/ { proxy_pass ... }`). Le navigateur ne parle qu'à une seule
origine → pas de CORS.
</details>

**G4.** Où voit-on la documentation interactive de l'API ?
<details><summary>▸ Réponse</summary>

Sur http://localhost:8000/docs — Swagger UI **généré automatiquement par FastAPI**.
</details>

**G5.** Quel est le livrable final du TP ?
<details><summary>▸ Réponse</summary>

Le **lien Docker Hub** (https://hub.docker.com/u/studioflow) où la pipeline a publié les
images `moby-dock-backend` et `moby-dock-frontend`, plus le dépôt GitHub du code.
</details>

---

### 🎯 Si tu ne dois retenir que 5 phrases

1. Image = recette figée ; conteneur = image qui tourne.
2. Multi-stage = build dans une étape, image finale minimale (plus léger, plus sûr).
3. Compose = lancer plusieurs services ensemble, qui se parlent par leur nom.
4. CI/CD = build + publication automatiques à chaque push, déclenchés par un événement.
5. Les secrets restent chiffrés dans GitHub, jamais en clair dans le code.
