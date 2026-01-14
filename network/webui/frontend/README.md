# Network Dashboard (Frontend)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Created by Deeven Seru**

## Table of Contents

1.  [About the Dashboard](#about-the-dashboard)
2.  [Running in Development](#running-in-development)
3.  [Building for Production](#building-for-production)

## About the Dashboard

The **Network Dashboard** is the visual control center for your multi-agent system. It allows you to:
*   Watch tasks execute in real-time.
*   See the connections between devices.
*   Monitor performance status.

It's built with **React** and **Vite** for a fast, responsive experience.

## Running in Development

If you are a developer and want to modify the UI, follow these steps:

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Start the Dev Server**:
    ```bash
    npm run dev
    ```

The dashboard will open at `http://localhost:3000` and automatically connect to your Python backend.

## Building for Production

To create a finalized version of the dashboard for deployment:

```bash
npm run build
```

This compiles all the code into a small, efficient package in the `dist/` folder, ready to be served by the backend.

---
*© 2026 Deeven Seru. All Rights Reserved.*
