# NEXT_PUBLIC_* values are public and embedded by Next.js at build time.
FROM node:22-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ARG NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/v1/demo
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run typecheck && npm run build

FROM node:22-alpine
ENV NODE_ENV=production
WORKDIR /app
COPY --from=builder /app ./
USER node
EXPOSE 3000
CMD ["npm", "run", "start"]
