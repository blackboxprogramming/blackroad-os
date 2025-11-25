# BlackRoad OS

A microservice infrastructure management platform for the BlackRoad ecosystem.

## Service Purpose

BlackRoad OS provides:
- Health monitoring endpoints
- Version tracking and build information
- Express and Fastify-based API routing
- Job scheduling with BullMQ
- React component library for UI dashboards

## Local Development

### Prerequisites
- Node.js 18+
- npm

### Installation

```bash
npm install
```

### Running the Development Server

```bash
npm run dev
```

The server will start at `http://localhost:8080`.

### Running Tests

```bash
npm test
```

## Build & Deploy

### Building for Production

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

### Running in Production

```bash
npm start
```

### Railway Deployment

This project is configured for automatic deployment on Railway. The `railway.toml` file defines:

- **Builder**: Nixpacks
- **Start Command**: `npm run start`
- **Healthcheck**: `/health` endpoint
- **Default Port**: 8080

## Healthcheck

The `/health` endpoint returns:

```json
{
  "status": "ok",
  "service": "blackroad-os"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8080` |
| `SERVICE_NAME` | Service identifier | `blackroad-os` |
| `ENVIRONMENT` | Runtime environment | `production` |
| `APP_VERSION` | Application version | `1.0.0` |
| `APP_COMMIT` | Git commit hash | Auto-detected |