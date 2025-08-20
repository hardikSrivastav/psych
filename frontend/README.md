# AI Psychologist Frontend

Next.js frontend for the AI Psychologist RAG system with TypeScript and Tailwind CSS.

## Features

- 🧠 Therapeutic chat interface
- 📱 Responsive design
- ⚡ Real-time messaging
- 🎨 Modern UI with glassmorphism effects
- 📊 Response metadata display
- 🔒 Session management

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Docker

The frontend is containerized and integrated with the full stack via docker-compose:

```bash
# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Docker** - Containerization
