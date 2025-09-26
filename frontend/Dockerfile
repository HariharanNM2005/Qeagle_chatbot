# syntax=docker/dockerfile:1

# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend /app
RUN npm run build

# Serve stage
FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=build /app/dist /app/dist
RUN npm i -g serve
EXPOSE 3001
CMD ["serve", "-s", "dist", "-l", "3001"]


