# Stage 1: Serve with Nginx
FROM nginx:alpine

# Copy built assets from local dist folder
# Note: Requires 'npm run build' to be run locally first (handled by setup.sh)
COPY dist /usr/share/nginx/html

# Copy custom Nginx configuration
# We'll create a simple inline config or copy a file if we had one.
# For now, let's use a simple command to overwrite default config to handle SPA routing
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
    try_files $uri $uri/ /index.html; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
