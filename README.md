# Private Chat

## Overview

This project implements a simple **Private Chat** system using WebSockets, consisting of two components:

- **Server**: Handles WebSocket connections and message broadcasting.
- **CLI Client**: Connects to the server via WebSocket to send and receive messages in real-time.
- **GUI Client:** A web-based graphical interface for chatting, built with React.

---

## Features

- WebSocket-based real-time communication.
- Automatic public URL creation using ngrok (optional).
- Dockerized server for isolated, secure deployment.
- Client supports username identification and message broadcasting.
- **Web GUI client for a user-friendly chat experience.**

---

## Prerequisites

- Docker installed on your system.
- (Optional) An ngrok account with an authentication token if you want to expose the server publicly.
- Node.js (if running the GUI client locally).

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

### Client (CLI)

1. Run the client script

The client will prompt for the WebSocket server URL:

- Use the public `wss://...` URL if ngrok is active.
- Use `ws://localhost:8000/ws` if connecting locally.

2. Chatting

- On connection, enter your username.
- Start sending messages; your messages will be broadcasted to other connected clients.
- Incoming messages from other users will be displayed live.

---

### GUI Client (Web)

A graphical web client is available for a more user-friendly chat experience.

#### Recommended: Run Locally

Running the GUI client locally is **recommended** for development and general use, as it ensures proper handling and closure of TCP ports when you close the browser or stop the development server.

1. Install dependencies and start the client:

    ```
    cd chat-front
    npm install
    npm run dev
    ```

2. Open your browser and navigate to [http://localhost:5173](http://localhost:5173).

3. Enter the WebSocket server URL when prompted (see above for options) and your Username.

#### Alternative: Run with Docker

You can also run the GUI client in a Docker container:

1. Build and run the Docker container:

    ```
    cd chat-front
    docker build -t chat-front .
    docker run --name front -p 5173:5173 chat-front
    ```

2. Open your browser and navigate to [http://localhost:5173](http://localhost:5173).

**Important:**  
When running the GUI client in Docker, there is a known issue where the TCP port used by the development server (Vite) may not close immediately when stopping the container.  
- You may need to ensure the container is fully stopped (`docker stop front` or `docker kill front`) to release the port.
- This is a limitation of how some development servers handle process signals inside containers.

**For best results and to avoid lingering TCP connections, prefer running the GUI client locally during development.**

---

## Notes

- WebSocket connections use secure `wss://` when ngrok exposes an HTTPS tunnel.
- Local connections use `ws://` without encryption.
- The server is designed to broadcast messages to all other clients, excluding the sender.
- The project uses FastAPI for the server and Python asyncio-based client for simplicity and efficiency.
- The GUI client is built with React and Vite for a modern web experience.