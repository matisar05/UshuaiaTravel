# Etapa 1: Build de la aplicación con Vite
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar dependencias e instalarlas
COPY package.json package-lock.json* ./
RUN npm install

# Copiar el resto del código y compilar para producción
COPY . .
RUN npm run build

# Etapa 2: Servidor web ultrarrápido (Nginx) para producción
FROM nginx:alpine

# Copiar los estáticos compilados desde la etapa 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuración por defecto opcional para SPAs (React Router)
# RUN echo "server { listen 80; location / { root /usr/share/nginx/html; index index.html index.htm; try_files \$uri \$uri/ /index.html; } }" > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
