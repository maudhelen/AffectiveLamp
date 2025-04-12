import React, { useRef, useEffect, useState } from 'react';
import { emotions } from '../utils/emotions';

const getEmotionColor = (emotionName) => {
  const colorMap = {
    // Yellow emotions
    'Calm': '#FFD700',
    'Peaceful': '#FFD700',
    // Green emotions
    'Happy': '#4CAF50',
    'Content': '#4CAF50',
    'Excited': '#4CAF50',
    // Red emotions
    'Angry': '#FF4444',
    'Anxious': '#FF4444',
    'Frustrated': '#FF4444',
    // Blue emotions
    'Sad': '#2196F3',
    'Bored': '#2196F3'
  };
  return colorMap[emotionName] || '#4a90e2';
};

const ValenceArousalGraph = ({ onDataClick }) => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 600, height: 600 });
  const [previewColor, setPreviewColor] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingData, setPendingData] = useState(null);
  const [confirmedMarkers, setConfirmedMarkers] = useState([]);

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

  // Function to round time to nearest 2-minute interval
  const roundToNearestTwoMinutes = (timestamp) => {
    const date = new Date(timestamp);
    // Add two hours (7200000 milliseconds)
    date.setTime(date.getTime() + 7200000);
    const minutes = date.getMinutes();
    const roundedMinutes = Math.floor(minutes / 2) * 2;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    
    // Convert to Marrakech timezone (subtract 1 hour as Morocco doesn't observe DST)
    const marrakechDate = new Date(date.toLocaleString('en-US', { timeZone: 'Africa/Casablanca' }));
    marrakechDate.setHours(marrakechDate.getHours() - 1);
    return marrakechDate.toISOString();

    // For Madrid timezone (when needed):
    // const madridDate = new Date(date.toLocaleString('en-US', { timeZone: 'Europe/Madrid' }));
    // return madridDate.toISOString();
  };

  // Function to save data to file
  const saveDataToFile = async (data) => {
    const roundedTimestamp = roundToNearestTwoMinutes(data.timestamp);
    const formattedDate = new Date(roundedTimestamp).toISOString();
    
    const csvData = `${formattedDate},${data.valence},${data.arousal},${data.closestEmotion.name},${data.color.hue.hue},${data.color.hue.saturation},${data.color.hue.brightness}\n`;
    
    console.log('Sending data to server:', csvData);
    
    try {
      const response = await fetch('/api/save-emotion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: csvData })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        console.log('Data saved successfully to:', result.filePath);
      } else {
        console.error('Server error:', result.error);
        alert('Failed to save emotion data. Please try again.');
      }
    } catch (error) {
      console.error('Error saving data:', error);
      alert('Failed to save emotion data. Please try again.');
    }
  };

  const handleConfirm = async () => {
    if (pendingData) {
      // Set the new marker (replacing any previous markers)
      setConfirmedMarkers([{
        x: pendingData.x,
        y: pendingData.y,
        color: pendingData.color.rgb
      }]);

      // Save data to file
      await saveDataToFile(pendingData);

      // Call the original callback
      onDataClick(pendingData);
    }
    setShowConfirmation(false);
    setPendingData(null);
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setPendingData(null);
    setPreviewColor(null);
  };

  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = dimensions;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 50;
    const displayRadius = radius * 0.7;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw circle outline
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw quadrants
    const colors = {
      upperRight: 'rgba(0, 255, 0, 0.75)',    // GREEN (positive valence, high arousal)
      upperLeft: 'rgba(255, 0, 0, 0.75)',     // RED (negative valence, high arousal)
      lowerLeft: 'rgba(32, 151, 255, 0.75)',  // BLUE (negative valence, low arousal)
      lowerRight: 'rgba(255, 255, 0, 0.75)',  // YELLOW (positive valence, low arousal)
    };

    // Upper right quadrant (GREEN - positive valence, high arousal)
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, -Math.PI/2, 0);
    ctx.lineTo(centerX, centerY);
    ctx.fillStyle = colors.upperRight;
    ctx.fill();

    // Lower right quadrant (YELLOW - positive valence, low arousal)
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, 0, Math.PI/2);
    ctx.lineTo(centerX, centerY);
    ctx.fillStyle = colors.lowerRight;
    ctx.fill();

    // Lower left quadrant (BLUE - negative valence, low arousal)
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, Math.PI/2, Math.PI);
    ctx.lineTo(centerX, centerY);
    ctx.fillStyle = colors.lowerLeft;
    ctx.fill();

    // Upper left quadrant (RED - negative valence, high arousal)
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, Math.PI, 3*Math.PI/2);
    ctx.lineTo(centerX, centerY);
    ctx.fillStyle = colors.upperLeft;
    ctx.fill();

    // Create a radial gradient for the white center fade
    const centerGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
    centerGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');      // Fully white at center
    centerGradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.9)');  // Very white
    centerGradient.addColorStop(0.4, 'rgba(255, 255, 255, 0.7)');  // Semi-white
    centerGradient.addColorStop(0.6, 'rgba(255, 255, 255, 0.4)');  // Light white
    centerGradient.addColorStop(0.8, 'rgba(255, 255, 255, 0.1)');  // Very light white
    centerGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');      // Fully transparent at edges

    // Add the center white gradient overlay
    ctx.fillStyle = centerGradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fill();

    // Draw axes
    ctx.beginPath();
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 2;

    // Vertical axis (Arousal)
    ctx.moveTo(centerX, centerY - radius);
    ctx.lineTo(centerX, centerY + radius);
    ctx.stroke();

    // Horizontal axis (Valence)
    ctx.moveTo(centerX - radius, centerY);
    ctx.lineTo(centerX + radius, centerY);
    ctx.stroke();

    // Add axis labels
    ctx.font = '14px Arial';
    ctx.fillStyle = '#374151';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Arousal labels
    ctx.fillText('High Arousal', centerX, centerY - radius - 20);
    ctx.fillText('Low Arousal', centerX, centerY + radius + 20);
    
    // Valence labels
    ctx.textAlign = 'left';
    ctx.fillText('Negative Valence', centerX - radius - 100, centerY);
    ctx.textAlign = 'right';
    ctx.fillText('Positive Valence', centerX + radius + 100, centerY);

    // Draw emotion labels
    emotions.forEach(emotion => {
      const angle = Math.atan2(emotion.arousal, emotion.valence);
      const distance = Math.sqrt(emotion.valence * emotion.valence + emotion.arousal * emotion.arousal);
      const scaledDistance = distance * displayRadius;
      const x = centerX + (scaledDistance * Math.cos(angle));
      const y = centerY - (scaledDistance * Math.sin(angle));

      // Draw emotion label
      ctx.fillStyle = '#374151';
      ctx.font = '14px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const labelOffset = 15;
      const labelX = x + (Math.cos(angle) * labelOffset);
      const labelY = y - (Math.sin(angle) * labelOffset);
      ctx.fillText(emotion.name, labelX, labelY);
    });

    // Draw confirmed markers
    confirmedMarkers.forEach(marker => {
      ctx.beginPath();
      ctx.arc(marker.x, marker.y, 8, 0, 2 * Math.PI);
      ctx.fillStyle = marker.color;
      ctx.fill();
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  };

  const getColorFromPosition = (valence, arousal) => {
    // Calculate distance from center (0 to 1)
    const distance = Math.sqrt(valence * valence + arousal * arousal);
    
    // If very close to center, return white
    if (distance < 0.2) { // Increased white center threshold
      const whiteIntensity = 1 - (distance / 0.2); // Linear fade from white
      return {
        rgb: `rgba(255, 255, 255, ${whiteIntensity})`,
        hue: { 
          hue: 0, 
          saturation: 0, 
          brightness: Math.round(254 * whiteIntensity)
        }
      };
    }

    // Determine quadrant and set colors
    let r, g, b;
    
    if (valence >= 0 && arousal >= 0) { // Upper right - GREEN
      r = 0;
      g = 255;
      b = 0;
    } else if (valence >= 0 && arousal < 0) { // Lower right - YELLOW
      r = 255;
      g = 255;
      b = 0;
    } else if (valence < 0 && arousal < 0) { // Lower left - BLUE
      r = 32;
      g = 151;
      b = 255;
    } else { // Upper left - RED
      r = 255;
      g = 0;
      b = 0;
    }

    // Calculate opacity based on distance from center
    const opacity = 0.5; // Match the opacity used in the graph

    // Convert to RGB format with opacity
    const rgb = `rgba(${r}, ${g}, ${b}, ${opacity})`;
    
    // Convert to Hue format (using full intensity values for Hue calculation)
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, v = max;

    const d = max - min;
    s = max === 0 ? 0 : d / max;

    if (max === min) {
      h = 0;
    } else {
      switch (max) {
        case r:
          h = (g - b) / d + (g < b ? 6 : 0);
          break;
        case g:
          h = (b - r) / d + 2;
          break;
        case b:
          h = (r - g) / d + 4;
          break;
      }
      h /= 6;
    }

    return {
      rgb,
      hue: {
        hue: Math.round(h * 65535),
        saturation: Math.round(s * 254),
        brightness: Math.round(v / 255 * 254)
      }
    };
  };

  const handleClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const { width, height } = dimensions;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 50;
    const displayRadius = radius * 0.7;

    // Convert click coordinates to relative position from center
    const relativeX = (x - centerX) / displayRadius;
    const relativeY = -(y - centerY) / displayRadius; // Invert Y for correct arousal

    // Calculate distance from center
    const distance = Math.sqrt(relativeX * relativeX + relativeY * relativeY);

    // If click is outside the circle, clamp to circle boundary
    let valence, arousal;
    if (distance > 1) {
      const angle = Math.atan2(relativeY, relativeX);
      valence = Math.cos(angle);
      arousal = Math.sin(angle);
    } else {
      valence = relativeX;
      arousal = relativeY;
    }

    const closestEmotion = findClosestEmotion(valence, arousal);
    const color = getColorFromPosition(valence, arousal);
    
    setPreviewColor(color);
    setPendingData({
      timestamp: Date.now(),
      valence,
      arousal,
      closestEmotion,
      color,
      x,
      y
    });
    setShowConfirmation(true);
  };

  useEffect(() => {
    drawGraph();
  }, [dimensions, confirmedMarkers]);

  return (
    <div className="relative flex flex-col items-center">
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        onClick={handleClick}
        className="border border-gray-200 rounded-lg shadow-sm"
      />
      
      {/* Confirmation Popup */}
      {showConfirmation && pendingData && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Confirm Emotion</h3>
            <div className="flex items-center space-x-4">
              <div 
                className="w-8 h-8 rounded-full border border-gray-200"
                style={{ backgroundColor: previewColor.rgb }}
              />
              <div className="space-y-1">
                <p className="text-sm text-gray-600">
                  Emotion: {pendingData.closestEmotion.name}
                </p>
                <p className="text-sm text-gray-600">
                  Valence: {pendingData.valence.toFixed(2)}, Arousal: {pendingData.arousal.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600">
                  Hue: {previewColor.hue.hue}, Sat: {previewColor.hue.saturation}, Bri: {previewColor.hue.brightness}
                </p>
              </div>
            </div>
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              className="px-4 py-2 text-sm text-white bg-blue-500 hover:bg-blue-600 rounded"
            >
              Confirm
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValenceArousalGraph; 