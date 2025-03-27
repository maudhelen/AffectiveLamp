export const emotions = [
  // Positive valence, high arousal (upper right - GREEN)
  { name: 'Happy', valence: 0.95, arousal: 0.5 },
  { name: 'Excited', valence: 0.75, arousal: 0.85 },
  { name: 'Confident', valence: 0.8, arousal: 0.2 },
  { name: 'Aroused', valence: 0.2, arousal: 1.1 },

  // Positive valence, low arousal (lower right - YELLOW)
  { name: 'Pleased', valence: 1.1, arousal: -0.15 },
  { name: 'Content', valence: 0.75, arousal: -0.45 },
  { name: 'Relaxed', valence: 0.7, arousal: -0.8 },
  { name: 'Calm', valence: 0.2, arousal: -1.1 },

  // Negative valence, high arousal (upper left - RED)
  { name: 'Tense', valence: -0.2, arousal: 1.1 },
  { name: 'Anxious', valence: -0.7, arousal: 1.0 },
  { name: 'Angry', valence: -0.9, arousal: 0.69 },
  { name: 'Annoyed', valence: -0.95, arousal: 0.45 },
  { name: 'Frustrated', valence: -1.0, arousal: 0.2 },

  // Negative valence, low arousal (lower left - BLUE)
  { name: 'Depressed', valence: -1.1, arousal: -0.2 },
  { name: 'Sad', valence: -1.0, arousal: -0.55 },
  { name: 'Bored', valence: -0.5, arousal: -0.7 },
  { name: 'Tired', valence: -0.2, arousal: -1.1 },

  { name: 'Neutral', valence: 0.0, arousal: 0.0 }
]; 