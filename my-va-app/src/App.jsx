import React, { useState } from 'react'
import ValenceArousalGraph from './components/ValenceArousalGraph'

function App() {
  const [clickData, setClickData] = useState(null);

  const handleDataClick = (data) => {
    setClickData(data);
    console.log('Click Data:', {
      timestamp: new Date(data.timestamp).toLocaleString(),
      valence: data.valence.toFixed(2),
      arousal: data.arousal.toFixed(2),
      closestEmotion: data.closestEmotion.name
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
                  <p className="font-medium text-gray-800">{new Date(clickData.timestamp).toLocaleString()}</p>
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
