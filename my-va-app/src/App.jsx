import React, { useState, useEffect } from 'react'
import ValenceArousalGraph from './components/ValenceArousalGraph'

function App() {
  const [clickData, setClickData] = useState(null);
  const [predictionData, setPredictionData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Function to fetch the latest data from the server
  const fetchLatestData = async () => {
    try {
      const response = await fetch('/api/emotion-data');
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      const csvText = await response.text();
      const rows = csvText.split('\n').filter(row => row.trim() !== '');
      
      // Skip header row and check if there's any data
      if (rows.length > 1) {
        const lastRow = rows[rows.length - 1];
        const [timestamp, valence, arousal, emotion, hue, saturation, brightness] = lastRow.split(',');
        
        // Find the closest emotion from the emotions array
        const closestEmotion = {
          name: emotion,
          valence: parseFloat(valence),
          arousal: parseFloat(arousal)
        };

        setClickData({
          timestamp: timestamp, // Keep the original timestamp string
          valence: parseFloat(valence),
          arousal: parseFloat(arousal),
          closestEmotion,
          color: {
            hue: {
              hue: parseInt(hue),
              saturation: parseFloat(saturation),
              brightness: parseFloat(brightness)
            }
          }
        });
      }
    } catch (error) {
      console.error('Error fetching latest data:', error);
    }
  };

  // Fetch latest data when component mounts
  useEffect(() => {
    fetchLatestData();
  }, []);

  const handleDataClick = async (data) => {
    // Format the timestamp to match CSV format (YYYY-MM-DDTHH:MM:00)
    const date = new Date(data.timestamp);
    const formattedTimestamp = date.toISOString().replace(/:\d{2}\.\d{3}Z$/, ':00');
    
    setClickData({
      ...data,
      timestamp: formattedTimestamp
    });
    
    console.log('New emotion recorded:', {
      emotion: data.closestEmotion.name,
      valence: data.valence.toFixed(2),
      arousal: data.arousal.toFixed(2)
    });

    // Send VA coordinates to lamp
    try {
      const response = await fetch('/api/control-lamp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          valence: data.valence,
          arousal: data.arousal
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to control lamp');
      }

      const result = await response.json();
      console.log('Lamp control response:', result);
    } catch (error) {
      console.error('Error controlling lamp:', error);
    }
  };

  const handleLoadPrediction = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/predict-emotion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get prediction');
      }

      const result = await response.json();
      setPredictionData(result);
      
      // Show prediction on VA space
      handleDataClick({
        timestamp: result.timestamp,
        valence: result.predicted_valence,
        arousal: result.predicted_arousal,
        closestEmotion: {
          name: result.predicted_emotion,
          valence: result.predicted_valence,
          arousal: result.predicted_arousal
        }
      });
    } catch (error) {
      console.error('Error getting prediction:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-white flex items-center justify-center">
      <div className="max-w-4xl w-full px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">Affective Lamp - Emotion Tracker</h1>
        
        <div className="bg-white rounded-xl shadow-lg p-8 relative">
          {/* Load Prediction Button */}
          <button
            onClick={handleLoadPrediction}
            disabled={isLoading}
            className="absolute top-4 right-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Loading...' : 'Load Prediction'}
          </button>

          <ValenceArousalGraph onDataClick={handleDataClick} />
          
          {clickData && (
            <div className="mt-8 p-6 bg-gray-50 rounded-lg">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">
                {predictionData ? 'Predicted Emotion' : 'Last Recorded Emotion'}
              </h2>
              <div className="flex items-center justify-between space-x-8">
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Time</p>
                  <p className="font-medium text-gray-800">{clickData.timestamp}</p>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Emotion</p>
                  <p className="font-medium text-gray-800">{clickData.closestEmotion.name}</p>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Valence</p>
                  <p className="font-medium text-gray-800">{clickData.valence.toFixed(2)}</p>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-500">Arousal</p>
                  <p className="font-medium text-gray-800">{clickData.arousal.toFixed(2)}</p>
                </div>
              </div>
              
              {predictionData && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Is this prediction correct? Click on the VA space to confirm or adjust.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
