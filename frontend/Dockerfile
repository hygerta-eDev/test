# build stage
FROM node:lts-gallium as build-stage
WORKDIR /app
COPY . .
RUN apt install autoconf automake gcc make g++ make libpng-dev
RUN npm install
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

ADD ./nginx/default.conf /etc/nginx/sites-available/default.conf

# ADD and set Group
RUN addgroup -g 1000 webuser && adduser -G webuser -g webuser -s /bin/sh -D webuser

# Set Group to Workspace
RUN chown webuser:webuser /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]