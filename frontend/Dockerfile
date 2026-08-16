FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# We'll run the dev server in the container for simplicity in this demo,
# so the code syncs and is immediately visible.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
