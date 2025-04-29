import React, { useState, useEffect } from 'react'
import ValenceArousalGraph from './components/ValenceArousalGraph'
import { emotions } from './utils/emotions'
import { getColorFromPosition } from './utils/colorUtils'

function App() {
  const [clickData, setClickData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingData, setPendingData] = useState(null);
  const [previewColor, setPreviewColor] = useState(null);

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
          timestamp: timestamp,
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
    // Round timestamp to nearest even minute for new entries
    const now = new Date();
    const minutes = now.getMinutes();
    const roundedMinutes = Math.round(minutes / 2) * 2;
    now.setMinutes(roundedMinutes);
    now.setSeconds(0);
    now.setMilliseconds(0);

    setPendingData({
      ...data,
      timestamp: now.toISOString(),
      color: getColorFromPosition(data.valence, data.arousal)
    });
    setPreviewColor(getColorFromPosition(data.valence, data.arousal));
    setShowConfirmation(true);
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
        throw new Error('Failed to fetch prediction');
      }
      const data = await response.json();
      
      // Find the closest emotion using the same logic as the graph
      const findClosestEmotion = (valence, arousal) => {
        return emotions.reduce((closest, current) => {
          const currentDistance = Math.sqrt(
            Math.pow(current.valence - valence, 2) + 
            Math.pow(current.arousal - arousal, 2)
          );
          const closestDistance = Math.sqrt(
            Math.pow(closest.valence - valence, 2) + 
            Math.pow(closest.arousal - arousal, 2)
          );
          return currentDistance < closestDistance ? current : closest;
        });
      };

      const closestEmotion = findClosestEmotion(data.valence, data.arousal);
      const color = getColorFromPosition(data.valence, data.arousal);

      // Set pending data to trigger the confirmation popup
      setPendingData({
        timestamp: data.timestamp, // Use exact timestamp from prediction
        valence: data.valence,
        arousal: data.arousal,
        closestEmotion,
        color,
        isPrediction: true // Add flag to indicate this is a prediction
      });
      setPreviewColor(color);
      setShowConfirmation(true);
    } catch (error) {
      console.error('Error loading prediction:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!pendingData) return;

    try {
      // Only save to the appropriate endpoint based on whether it's a prediction
      if (pendingData.isPrediction) {
        // For predictions, only save to predictions.csv
        await fetch('/api/save-prediction', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ data: pendingData }),
        });
      } else {
        // For manual entries, only save to emotion_data.csv
        await fetch('/api/save-emotion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ data: pendingData }),
        });
      }

      // Update the lamp color
      await fetch('/api/control-lamp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          valence: pendingData.valence,
          arousal: pendingData.arousal,
        }),
      });

      // Add the point to the graph data
      setClickData(pendingData);
      
      // Reset states
      setPendingData(null);
      setShowConfirmation(false);
      setPreviewColor(null);
    } catch (error) {
      console.error('Error saving data:', error);
    }
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setPendingData(null);
    setPreviewColor(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-12">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">Affective Lamp</h1>
          <p className="text-lg text-gray-600 font-medium">Track and visualize your emotions in real-time</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-100">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-1">Emotion Graph</h2>
              <p className="text-gray-500">Click anywhere on the graph to record your emotion</p>
            </div>
            <button
              onClick={handleLoadPrediction}
              disabled={isLoading}
              className={`px-6 py-3 rounded-lg font-medium text-white transition-all duration-200
                ${isLoading 
                  ? 'bg-blue-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'}`}
            >
              {isLoading ? 'Loading...' : 'Load Prediction'}
            </button>
          </div>

          <div className="relative">
            <ValenceArousalGraph 
              onDataClick={handleDataClick}
              clickData={clickData}
            />
            
            {/* Confirmation Popup */}
            {showConfirmation && pendingData && pendingData.closestEmotion && (
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                bg-white p-6 rounded-xl shadow-xl border border-gray-200 w-96">
                <div className="mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Confirm Emotion</h3>
                  <div className="flex items-center space-x-6">
                    <div 
                      className="w-12 h-12 rounded-full border-2 border-gray-200 shadow-sm"
                      style={{ backgroundColor: previewColor?.rgb || '#FFFFFF' }}
                    />
                    <div className="space-y-2">
                      <p className="text-base text-gray-700">
                        <span className="font-medium">Emotion:</span> {pendingData.closestEmotion.name}
                      </p>
                      <p className="text-base text-gray-700">
                        <span className="font-medium">Valence:</span> {pendingData.valence.toFixed(2)}
                        <span className="mx-2">•</span>
                        <span className="font-medium">Arousal:</span> {pendingData.arousal.toFixed(2)}
                      </p>
                      <p className="text-sm text-gray-500">
                        <span className="font-medium">Hue:</span> {previewColor?.hue?.hue || 0}
                        <span className="mx-2">•</span>
                        <span className="font-medium">Sat:</span> {previewColor?.hue?.saturation || 0}
                        <span className="mx-2">•</span>
                        <span className="font-medium">Bri:</span> {previewColor?.hue?.brightness || 0}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={handleCancel}
                    className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleConfirm}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                  >
                    Yes
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {clickData && (
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Latest Emotion</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Emotion</h3>
                <p className="text-lg text-gray-900">{clickData.closestEmotion.name}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Timestamp</h3>
                <p className="text-lg text-gray-900">
                  {new Date(clickData.timestamp).toLocaleString('en-US', { timeZone: 'Europe/Madrid' })}
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Valence</h3>
                <p className="text-lg text-gray-900">{clickData.valence.toFixed(2)}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Arousal</h3>
                <p className="text-lg text-gray-900">{clickData.arousal.toFixed(2)}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
