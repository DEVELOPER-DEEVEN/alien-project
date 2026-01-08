# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster Web UI Server.

FastAPI-based server that provides WebSocket communication for the cluster Web UI.
Integrates with the cluster event system to provide real-time updates.

This is the refactored version with improved architecture:
- Pydantic models and enums in separate modules
- Business logic separated into services
- Routers for endpoint organization
- Dependency injection for state management
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from cluster.core.events import get_event_bus
from cluster.webui.dependencies import get_app_state
from cluster.webui.routers import health_router, devices_router, websocket_router
from cluster.webui.websocket_observer import WebSocketObserver

if TYPE_CHECKING:
    from cluster.cluster_client import clusterClient
    from cluster.session.cluster_session import clusterSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown logic including:
    - Creating and registering the WebSocket observer on startup
    - Unsubscribing the observer on shutdown

    :param app: The FastAPI application instance
    """
    # Startup phase
    logger: logging.Logger = logging.getLogger(__name__)
    logger.info("🚀 Starting cluster Web UI Server")
    print("🚀 Starting cluster Web UI Server")

    # Get application state
    app_state = get_app_state()

    # Create and register WebSocket observer with event bus
    websocket_observer = WebSocketObserver()
    app_state.websocket_observer = websocket_observer

    event_bus = get_event_bus()
    event_bus.subscribe(websocket_observer)

    logger.info(
        f"✅ WebSocket observer registered with event bus (observer: {websocket_observer})"
    )
    print(f"✅ WebSocket observer registered with event bus")
    print(f"📊 Event bus has {len(event_bus._observers)} observers")

    yield

    # Shutdown phase
    logger.info("👋 Shutting down cluster Web UI Server")
    print("👋 Shutting down cluster Web UI Server")
    event_bus.unsubscribe(websocket_observer)


# Create FastAPI app with lifespan management
app = FastAPI(
    title="cluster Web UI",
    description="Modern web interface for cluster Framework",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different endpoint groups
app.include_router(health_router)
app.include_router(devices_router)
app.include_router(websocket_router)

# Mount frontend static files if built
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    logger = logging.getLogger(__name__)
    logger.info(f"Serving frontend from {frontend_dist}")


@app.get("/logo3.png")
async def logo() -> FileResponse:
    """
    Serve the logo file.

    :return: FileResponse containing the logo image, or 404 if not found
    """
    logo_path: Path = Path(__file__).parent / "frontend" / "dist" / "logo3.png"
    if logo_path.exists():
        return FileResponse(logo_path, media_type="image/png")
    return HTMLResponse(content="Logo not found", status_code=404)


@app.get("/")
async def root() -> HTMLResponse:
    """
    Root endpoint that serves the web UI.

    Attempts to serve the built React application if available,
    otherwise returns a placeholder HTML page from templates.

    :return: HTMLResponse containing the web UI or placeholder
    """
    # Try to serve built React app first
    frontend_index: Path = Path(__file__).parent / "frontend" / "dist" / "index.html"
    if frontend_index.exists():
        with open(frontend_index, "r", encoding="utf-8") as f:
            return HTMLResponse(
                content=f.read(),
                status_code=200,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )

    # Fallback to placeholder HTML from templates
    template_path: Path = Path(__file__).parent / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)

    # Ultimate fallback if template file doesn't exist
    return HTMLResponse(
        content="<h1>cluster Web UI</h1><p>Server is running</p>", status_code=200
    )


def set_cluster_session(session: "clusterSession") -> None:
    """
    Set the cluster session for the web UI.

    :param session: The clusterSession instance
    """
    app_state = get_app_state()
    app_state.cluster_session = session


def set_cluster_client(client: "clusterClient") -> None:
    """
    Set the cluster client for the web UI.

    :param client: The clusterClient instance
    """
    app_state = get_app_state()
    app_state.cluster_client = client


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Start the cluster Web UI server.

    :param host: Host address to bind to (default: "0.0.0.0")
    :param port: Port number to listen on (default: 8000)
    """
    import uvicorn

    logger: logging.Logger = logging.getLogger(__name__)
    logger.info(f"Starting cluster Web UI server on {host}:{port}")

    uvicorn.run(app, host=host, port=port, log_level="info")
