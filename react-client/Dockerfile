FROM node:latest

WORKDIR /home

RUN git clone https://github.com/lucien-stavenhagen/MERN-Stack-Example.git ./client

WORKDIR /home/client/express-posts/react-client

RUN npm install

CMD ["npm","run","start"]
