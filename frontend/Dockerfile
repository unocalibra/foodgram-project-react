# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
ENV PYTHONUNBUFFERED 1
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
CMD cp -r build result_build
