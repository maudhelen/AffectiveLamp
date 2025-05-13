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
  const [statusMessage, setStatusMessage] = useState('');
  const [lastProcessedData, setLastProcessedData] = useState(null);
  const [isProcessingPrediction, setIsProcessingPrediction] = useState(false);

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

  // Function to check for Garmin data and make predictions
  const checkForGarminData = async () => {
    // Don't check for new data if we're currently processing a prediction
    if (isProcessingPrediction) {
      return;
    }

    try {
      const response = await fetch('/api/predict-emotion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        // Silently handle failed response
        return;
      }
      const data = await response.json();
      
      if (data && data.timestamp) {
        // Check if this is new data (different from last processed data)
        if (lastProcessedData && 
            lastProcessedData.timestamp === data.timestamp && 
            lastProcessedData.valence === data.valence && 
            lastProcessedData.arousal === data.arousal) {
          setStatusMessage('Checking for Garmin data...');
          return;
        }

        setStatusMessage('New Garmin data found! Making prediction...');
        setIsProcessingPrediction(true);
        
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
          timestamp: data.timestamp,
          valence: data.valence,
          arousal: data.arousal,
          closestEmotion,
          color,
          isPrediction: true
        });
        setPreviewColor(color);
        setShowConfirmation(true);
      } else {
        setStatusMessage('Checking for Garmin data...');
      }
    } catch (error) {
      // Silently handle any errors and continue checking
      console.error('Error checking for Garmin data:', error);
      setStatusMessage('Checking for Garmin data...');
    }
  };

  // Set up interval to check for Garmin data every 5 seconds
  useEffect(() => {
    const interval = setInterval(checkForGarminData, 5000);
    return () => clearInterval(interval);
  }, [lastProcessedData, isProcessingPrediction]); // Add isProcessingPrediction as dependency

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

  const handleConfirm = async () => {
    if (!pendingData) return;

    try {
      // First save the data
      if (pendingData.isPrediction) {
        await fetch('/api/save-prediction', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ data: pendingData }),
        });
        // Store the processed data
        setLastProcessedData({
          timestamp: pendingData.timestamp,
          valence: pendingData.valence,
          arousal: pendingData.arousal
        });
      } else {
        await fetch('/api/save-emotion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ data: pendingData }),
        });
      }

      // Add the point to the graph data
      setClickData(pendingData);
      
      // Reset states immediately after saving
      setPendingData(null);
      setShowConfirmation(false);
      setPreviewColor(null);
      setIsProcessingPrediction(false);
      setStatusMessage('Checking for Garmin data...');

      // Try to update the lamp color after everything else is done
      try {
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
      } catch (lampError) {
        console.warn('Could not connect to lamp:', lampError);
        // Show a temporary message about lamp connection
        const message = document.createElement('div');
        message.textContent = 'Could not connect to lamp, but saved to CSV!';
        message.style.position = 'fixed';
        message.style.top = '20px';
        message.style.left = '50%';
        message.style.transform = 'translateX(-50%)';
        message.style.backgroundColor = '#4CAF50';
        message.style.color = 'white';
        message.style.padding = '10px 20px';
        message.style.borderRadius = '5px';
        message.style.zIndex = '1000';
        document.body.appendChild(message);
        
        // Remove the message after 3 seconds
        setTimeout(() => {
          document.body.removeChild(message);
        }, 3000);
      }
    } catch (error) {
      console.error('Error saving data:', error);
      // Even if there's an error, try to close the popup
      setPendingData(null);
      setShowConfirmation(false);
      setPreviewColor(null);
      setIsProcessingPrediction(false);
      setStatusMessage('Checking for Garmin data...');
    }
  };

  const handleCancel = () => {
    // If this was a prediction, still mark it as processed to avoid showing it again
    if (pendingData?.isPrediction) {
      setLastProcessedData({
        timestamp: pendingData.timestamp,
        valence: pendingData.valence,
        arousal: pendingData.arousal
      });
    }
    setShowConfirmation(false);
    setPendingData(null);
    setPreviewColor(null);
    setIsProcessingPrediction(false);
    setStatusMessage('Checking for Garmin data...');
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
            <div className="text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
              {statusMessage || 'Checking for Garmin data...'}
            </div>
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
