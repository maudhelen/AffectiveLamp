import React, { useState, useEffect } from 'react'
import ValenceArousalGraph from './components/ValenceArousalGraph'

function App() {
  const [clickData, setClickData] = useState(null);

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

  const handleDataClick = (data) => {
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
  };

  return (
    <div className="h-screen w-screen bg-white flex items-center justify-center">
      <div className="max-w-4xl w-full px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">Affective Lamp - Emotion Tracker</h1>
        
        <div className="bg-white rounded-xl shadow-lg p-8">
          <ValenceArousalGraph onDataClick={handleDataClick} />
          
          {clickData && (
            <div className="mt-8 p-6 bg-gray-50 rounded-lg">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Last Recorded Emotion</h2>
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
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
