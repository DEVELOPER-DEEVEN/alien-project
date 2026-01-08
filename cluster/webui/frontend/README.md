# cluster WebUI Frontend

React-based frontend for cluster Framework with real-time WebSocket updates.

## Development Mode

### Prerequisites
- Node.js 16+ and npm
- cluster backend running

### Quick Start

1. **Start the cluster backend** (in a separate terminal):
   ```bash
   cd Alien
   python -m cluster --webui
   ```
   
   The backend will:
   - Find an available port (8000-8009)
   - Auto-generate `.env.development.local` with the backend URL
   - Display the backend URL (e.g., `http://localhost:8001`)

2. **Start the frontend development server**:
   ```bash
   cd cluster/webui/frontend
   npm install  # First time only
   npm run dev
   ```
   
   The frontend will:
   - Read the backend URL from `.env.development.local`
   - Start on port 3000 (or 3001 if 3000 is busy)
   - Connect to the backend automatically

3. **Open your browser**: 
   - Frontend: `http://localhost:3000` (or 3001)
   - The frontend will connect to backend automatically

### Manual Port Configuration

If you need to manually specify the backend port:

1. Copy `.env.example` to `.env.development.local`:
   ```bash
   cp .env.example .env.development.local
   ```

2. Edit `.env.development.local`:
   ```
   VITE_BACKEND_URL=http://localhost:8001
   ```

3. Restart the frontend dev server

## Production Mode

In production, the backend serves the built frontend automatically:

```bash
# Build the frontend
cd cluster/webui/frontend
npm run build

# Start cluster with WebUI
cd ../../..
python -m cluster --webui
```

Then open `http://localhost:8000` (or whatever port the backend chooses).

## Architecture

- **Development**: Frontend (Vite) runs separately, connects to backend via direct HTTP/WebSocket
- **Production**: Backend (FastAPI) serves built frontend static files

## Troubleshooting

### Error: "Unexpected token '<', "<!DOCTYPE"..."

This error means the frontend is trying to connect to the wrong backend port.

**Solutions**:
1. Make sure the cluster backend is running first
2. Check that `.env.development.local` exists with the correct backend URL
3. Restart the frontend dev server after starting the backend
4. Check the backend terminal for the actual port it's using

### Backend Port Already in Use

If port 8000 is occupied:
- The backend will automatically find another port (8001-8009)
- It will update `.env.development.local` automatically
- Just restart your frontend dev server to pick up the new port

### WebSocket Connection Failed

- Ensure backend is running and accessible
- Check browser console for WebSocket errors
- Verify the backend URL in `.env.development.local`
