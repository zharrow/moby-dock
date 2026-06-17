# ----------------------------------------------------------------------------
# Étape 1 : build — compilation de l'app React avec Vite
# ----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# On copie d'abord les manifests pour profiter du cache Docker
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ----------------------------------------------------------------------------
# Étape 2 : runtime — Nginx sert les fichiers statiques générés
# ----------------------------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

# Config Nginx (SPA + proxy /api → backend)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Fichiers compilés depuis l'étape de build (image finale sans Node)
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
