# Network WebUI: Backend API Specification

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Server: Flask/FastAPI](https://img.shields.io/badge/Server-Python_Backend-green.svg)]()

**Architect: Deeven Seru**

---

## 📑 Table of Contents

1.  [Service Overview](#service-overview)
2.  [REST API Endpoints](#rest-api-endpoints)
3.  [WebSocket Event Catalog](#websocket-event-catalog)
4.  [Running the Server](#running-the-server)

---

## 1. Service Overview

The `network/webui` backend serves two purposes:
1.  **Static File Server**: Hosts the compiled React frontend.
2.  **API Gateway**: Proxies requests from the UI to the core Janus Server (if running separately) or acts as the Janus Server itself.

It is built using **FastAPI** for high-performance async handling.

---

## 2. REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Returns distinct health metrics of the server. |
| `GET` | `/api/agents` | Lists all currently connected worker nodes. |
| `POST` | `/api/task` | Submits a new natural language task to the queue. |
| `DELETE` | `/api/task/{id}` | Cancels a running task. |

---

## 3. WebSocket Event Catalog

Real-time communication uses the `/ws` endpoint.

**Server -> Client Events:**

| Event Type | Payload | Description |
| :--- | :--- | :--- |
| `dag_update` | `{nodes: [], edges: []}` | The task graph structure has changed. |
| `agent_heartbeat` | `{id: "agent_1", status: "idle"}` | Specific agent status update. |
| `stream_frame` | `{data: base64_jpg}` | Video frame from the active agent. |

**Client -> Server Events:**

| Event Type | Payload | Description |
| :--- | :--- | :--- |
| `subscribe` | `{topic: "task_123"}` | Listen for updates on a specific task. |
| `intervention` | `{text: "Click the red button"}` | Human guidance injection. |

---

## 4. Running the Server

```bash
# Production Mode (Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker network.webui.app:app

# Development Mode
python -m network.webui.main --debug
```

---
*© 2026 Deeven Seru. All Rights Reserved.*
