# Base image
FROM node:latest

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json /app/package.json
RUN npm install

# Copy the rest of the app
COPY . /app

## Run tests
RUN npm test -- --watchAll=false

# Build the app
RUN npm run build

# Serve the app
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
