# Private Chat

## Overview

This project implements a simple **Private Chat** system using WebSockets, consisting of two components:

- Server: Handles WebSocket connections and message broadcasting.
- Client: Connects to the server via WebSocket to send and receive messages in real-time.

---

## Features

- WebSocket-based real-time communication.
- Automatic public URL creation using ngrok (optional).
- Dockerized server for isolated, secure deployment.
- Client supports username identification and message broadcasting.

---

## Prerequisites

- Docker installed on your system.
- (Optional) An ngrok account with an authentication token if you want to expose the server publicly.

---

## Setup & Usage

### Server

1. Configure environment

   Create a `.env` file in the `server` directory (if not already present):

   ```
   NGROK_TOKEN=your_ngrok_auth_token_here
   ```

    If `NGROK_TOKEN` is omitted, the server will run locally on `localhost:8000`.

2. Build and run the server

    ```
    cd server
    docker build -t <container-name> .
    docker run <container-name>
    ```

3. Server output

- If `NGROK_TOKEN` is set, the server will print a public WebSocket URL (e.g., `wss://xxxx.ngrok.io/ws`) on startup.
- Otherwise, it will print that it's running locally at `ws://localhost:8000/ws`.

---

### Client

1. Run the client script

The client will prompt for the WebSocket server URL:

- Use the public `wss://...` URL if ngrok is active.
- Use `ws://localhost:8000/ws` if connecting locally.

2. Chatting

- On connection, enter your username.
- Start sending messages; your messages will be broadcasted to other connected clients.
- Incoming messages from other users will be displayed live.

---

## Notes

- WebSocket connections use secure `wss://` when ngrok exposes an HTTPS tunnel.
- Local connections use `ws://` without encryption.
- The server is designed to broadcast messages to all other clients, excluding the sender.
- The project uses FastAPI for the server and Python asyncio-based client for simplicity and efficiency.