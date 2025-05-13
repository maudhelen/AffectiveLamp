import React, { useRef, useEffect, useState } from 'react';
import { emotions } from '../utils/emotions';
import * as d3 from 'd3';
import { getColorFromPosition } from '../utils/colorUtils';

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

const ValenceArousalGraph = ({ onDataClick, clickData }) => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 600, height: 600 });
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
    // Create date object from timestamp
    const date = new Date(timestamp);
    
    // Round to nearest 2 minutes
    const currentMinutes = date.getMinutes();
    const roundedMinutes = Math.floor(currentMinutes / 2) * 2;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    
    // Convert to Madrid timezone
    const options = {
      timeZone: 'Europe/Madrid',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    };
    
    // Format the date in Madrid timezone
    const madridTime = date.toLocaleString('en-US', options);
    
    // Create a new date object from the Madrid time string
    const [datePart, timePart] = madridTime.split(', ');
    const [month, day, year] = datePart.split('/');
    const [hours, minutes, seconds] = timePart.split(':');
    
    // Create Madrid date
    const madridDate = new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds));
    
    return madridDate.toISOString();
  };

  useEffect(() => {
    drawGraph();
  }, [dimensions, confirmedMarkers, clickData]);

  const drawGraph = () => {
    if (!canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');
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
    ctx.fillText('Active', centerX, centerY - radius - 20);
    ctx.fillText('Calm', centerX, centerY + radius + 20);
    
    // Valence labels
    ctx.textAlign = 'left';
    ctx.fillText('Negative', centerX - radius - 50, centerY);
    ctx.textAlign = 'right';
    ctx.fillText('Positive', centerX + radius + 50, centerY);

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

    // Draw click data marker if exists
    if (clickData) {
      const angle = Math.atan2(clickData.arousal, clickData.valence);
      const distance = Math.sqrt(clickData.valence * clickData.valence + clickData.arousal * clickData.arousal);
      const scaledDistance = distance * displayRadius;
      const x = centerX + (scaledDistance * Math.cos(angle));
      const y = centerY - (scaledDistance * Math.sin(angle));

      // Draw marker
      ctx.beginPath();
      ctx.arc(x, y, 10, 0, 2 * Math.PI);
      ctx.fillStyle = clickData.color.rgb;
      ctx.fill();
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Add label
      ctx.fillStyle = '#000';
      ctx.font = '14px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(clickData.closestEmotion.name, x, y - 15);
    }
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

    // Calculate distance from center
    const distanceFromCenter = Math.sqrt(
      Math.pow(x - centerX, 2) + 
      Math.pow(y - centerY, 2)
    );

    // Only process click if it's within the circle's radius
    if (distanceFromCenter > radius) {
      return; // Ignore clicks outside the circle
    }

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
    
    // Get current timestamp in Madrid timezone and round to nearest even minute
    const now = new Date();
    const madridTime = new Date(now.toLocaleString('en-US', { timeZone: 'Europe/Madrid' }));
    const timestamp = roundToNearestTwoMinutes(madridTime.toISOString());
    
    // Call the parent's click handler with the data
    onDataClick({
      timestamp,
      valence,
      arousal,
      closestEmotion,
      color,
      x,
      y
    });
  };

  return (
    <div className="relative flex flex-col items-center">
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        onClick={handleClick}
        className="border border-gray-200 rounded-lg shadow-sm"
      />
    </div>
  );
};

export default ValenceArousalGraph; 