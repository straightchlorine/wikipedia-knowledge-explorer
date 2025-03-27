# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set environment variable here
ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}
RUN echo "Use env variable for API base URL: {$REACT_APP_API_BASE_URL}"

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY ./app .
RUN npm install

# Build the React app
RUN npm run build

# Use Nginx to serve the built files
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
