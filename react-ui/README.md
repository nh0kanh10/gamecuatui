# React UI - Game Frontend

## 🚀 Quick Start

### Option 1: Auto Start (Recommended)
```bash
# From project root
START_REACT_UI.bat
```

### Option 2: Manual Start
```bash
# 1. Install dependencies (first time only)
cd react-ui
npm install

# 2. Start dev server
npm run dev
```

## ✅ Features

- **Modern React UI** với Vite
- **TailwindCSS** styling
- **TypeScript** type safety
- **Dark Fantasy Theme**
- **Real-time Game State**
- **Memory System Integration**

## 📦 Dependencies

- `react` + `react-dom` - Core framework
- `axios` - API client
- `tailwindcss` - Styling
- `typescript` - Type safety
- `vite` - Build tool

## 🎯 Architecture

```
react-ui/
├── src/
│   ├── App.tsx          # Main game UI component
│   ├── api.ts           # API client (axios)
│   ├── main.tsx         # Entry point
│   └── index.css        # TailwindCSS styles
├── package.json
└── vite.config.ts       # Vite config with proxy
```

## 🔧 Development

```bash
# Dev mode (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🌐 API Integration

UI connects to FastAPI server at `http://localhost:8000`:
- `/` - Health check
- `/game/new` - Start new game
- `/game/load` - Load saved game
- `/game/saves` - List saves
- `/game/action` - Send player action
- `/memory/count` - Get memory count

---

**Status**: ✅ Ready to Use
