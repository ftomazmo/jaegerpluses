FROM node:14

COPY . .
RUN npm ci

CMD ["--require", "./instrumentation.js", "app.js"]