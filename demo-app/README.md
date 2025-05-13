# Affective Lamp VA App

A web application for collecting and managing emotion data, designed to interface with an affective lamp system.

## Technology Stack

- **Frontend**: React.js (v18.2.0) with Vite
- **Backend**: Node.js with Express.js (v4.18.3)
- **Styling**: Tailwind CSS
- **Development Tools**: 
  - ESLint for code quality
  - PostCSS for CSS processing
  - TypeScript support

## Architecture

The application follows a client-server architecture:
- React frontend for user interface
- Express backend for data management
- RESTful API design
- Static file serving for the frontend application

## Data Management

The system uses CSV-based data storage with the following structure:
- Timestamp
- Valence
- Arousal
- Emotion
- Color parameters (hue, saturation, brightness)

Features:
- Automatic file creation and header management
- Data persistence through file system operations
- Real-time emotion data collection
- Data retrieval capabilities

## Development

### Prerequisites
- Node.js
- npm

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Application
Start the development server:
```bash
npm run dev
```
This will concurrently run:
- Vite development server (frontend)
- Express server (backend)

### Building for Production
```bash
npm run build
```

## API Endpoints

- `POST /api/save-emotion`: Save emotion data
- `GET /api/emotion-data`: Retrieve emotion data

## Error Handling
The application includes comprehensive error handling and logging for:
- File system operations
- Data validation
- Server operations
