# Course Chatbot Frontend

A modern React frontend for the Course Chatbot application, built with TypeScript, Vite, and Tailwind CSS.

## Features

- 🤖 **AI Chat Interface**: Clean, modern chat UI powered by Llama 3.3 70B
- 💬 **Real-time Messaging**: Instant responses from the AI assistant
- 🎨 **Modern Design**: Built with Tailwind CSS for a beautiful, responsive interface
- ⚡ **Fast Development**: Vite for lightning-fast development and builds
- 🔧 **TypeScript**: Full type safety and better developer experience
- 📱 **Responsive**: Works perfectly on desktop and mobile devices

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to http://localhost:3000

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The frontend connects to the backend API with the following endpoints:

- `POST /api/v1/chat` - Send chat messages
- `POST /api/v1/answer` - Advanced chat with vector search
- `GET /api/v1/models` - Get model information
- `GET /api/v1/status` - Check service status
- `GET /api/v1/search` - Search content
- `POST /api/v1/content` - Add course content

## Project Structure

```
frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components
│   │   ├── ChatInterface.tsx
│   │   └── Header.tsx
│   ├── lib/
│   │   ├── api.ts        # API client
│   │   └── utils.ts      # Utility functions
│   ├── types/
│   │   └── chat.ts       # TypeScript types
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Features Overview

### Chat Interface
- Clean, modern chat UI with message bubbles
- Real-time typing indicators
- Message timestamps
- Error handling and loading states
- Responsive design for all screen sizes

### AI Integration
- Powered by Llama 3.3 70B via OpenRouter
- Free AI completions
- Context-aware responses
- Citation support (when available)

### User Experience
- Intuitive interface
- Keyboard shortcuts (Enter to send)
- Clear chat functionality
- Loading states and error messages
- Mobile-friendly design

## Development

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **API Calls**: Extend `src/lib/api.ts`
3. **Types**: Add to `src/types/`
4. **Styling**: Use Tailwind CSS classes

### Styling

The project uses Tailwind CSS with a custom configuration:
- Primary colors: Blue theme
- Responsive design utilities
- Custom component classes
- Dark mode support (ready for future implementation)

## Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Environment Variables

Create a `.env` file for environment-specific configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on http://localhost:8000
   - Check CORS configuration in backend

2. **Build Errors**
   - Run `npm install` to ensure all dependencies are installed
   - Check TypeScript errors with `npm run lint`

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check if all required CSS classes are imported

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Course Chatbot application.
