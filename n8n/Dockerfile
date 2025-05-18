FROM node:18-alpine

# n8n version
ARG N8N_VERSION=latest

# Install packages
RUN apk add --update graphicsmagick tzdata git tini su-exec

# Set up timezone
ENV TZ=Asia/Seoul

# Create n8n directory
RUN mkdir /home/node/.n8n

# Install n8n
RUN npm install -g n8n@${N8N_VERSION}

# n8n user
USER root

# Set workdir
WORKDIR /home/node/.n8n

# Volumes
VOLUME /home/node/.n8n

# Expose port
EXPOSE 5678

# Start n8n
ENTRYPOINT ["tini", "--"]
CMD ["n8n", "start"] 