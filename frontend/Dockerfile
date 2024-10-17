# Use the official Nginx image as the base
FROM nginx:alpine

# Install necessary tools
RUN apk add --no-cache nodejs npm

# Set the working directory
WORKDIR /usr/share/nginx/html

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire frontend directory contents into the container
COPY . .

# Copy a custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx and run the watch script
CMD ["sh", "-c", "nginx -g 'daemon off;' & npm run watch"]