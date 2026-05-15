FROM node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293 AS builder

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    NODE_ENV=production

WORKDIR /app

# Pin pnpm to a Node 20-compatible release. pnpm 11+ requires Node 22's
# built-in node:sqlite module and will crash on Node 20.
ENV PNPM_VERSION=10.18.0
RUN corepack enable && corepack prepare "pnpm@${PNPM_VERSION}" --activate

COPY ./app/package.json ./app/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY ./app .
RUN pnpm build

FROM nginx:alpine@sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de AS runtime

LABEL org.opencontainers.image.source="https://github.com/straightchlorine/wikipedia-knowledge-explorer"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="wke-frontend"
LABEL org.opencontainers.image.description="Wikipedia Knowledge Explorer — React SPA served by nginx"

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html

USER nginx

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
