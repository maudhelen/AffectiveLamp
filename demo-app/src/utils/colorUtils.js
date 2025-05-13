/**
 * Converts valence and arousal coordinates to RGB color values
 * 
 * The color mapping follows this logic:
 * - Positive valence + Positive arousal = Green (excited/happy)
 * - Positive valence + Negative arousal = Yellow (calm/peaceful)
 * - Negative valence + Positive arousal = Red (frustrated/angry)
 * - Negative valence + Negative arousal = Blue (sad/depressed)
 * - Neutral (when both valence and arousal are below 0.3) = White
 */

function hsvToRgb(h, s, v) {
  // Convert HSV to RGB
  let r, g, b;
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);

  switch (i % 6) {
    case 0: r = v; g = t; b = p; break;
    case 1: r = q; g = v; b = p; break;
    case 2: r = p; g = v; b = t; break;
    case 3: r = p; g = q; b = v; break;
    case 4: r = t; g = p; b = v; break;
    case 5: r = v; g = p; b = q; break;
  }

  return {
    r: Math.round(r * 255),
    g: Math.round(g * 255),
    b: Math.round(b * 255)
  };
}

export function getColorFromPosition(valence, arousal) {
  // Check if the point is within the neutral zone (both valence and arousal below 0.3)
  if (Math.abs(valence) < 0.3 && Math.abs(arousal) < 0.3) {
    return {
      rgb: '#FFFFFF',
      hue: {
        hue: 0,
        saturation: 0,
        brightness: 100
      }
    };
  }

  // Calculate hue based on quadrant
  let hue;
  if (valence >= 0 && arousal >= 0) {
    // Green quadrant (excited/happy)
    hue = 120 / 360; // Green
  } else if (valence >= 0 && arousal < 0) {
    // Yellow quadrant (calm/peaceful)
    hue = 60 / 360; // Yellow
  } else if (valence < 0 && arousal >= 0) {
    // Red quadrant (frustrated/angry)
    hue = 0 / 360; // Red
  } else {
    // Blue quadrant (sad/depressed)
    hue = 240 / 360; // Blue
  }

  // Calculate saturation based on distance from center
  const distanceFromOrigin = Math.sqrt(valence * valence + arousal * arousal);
  const saturation = Math.min(1, distanceFromOrigin * 2);

  // Calculate brightness based on arousal
  const brightness = 0.5 + (arousal * 0.5);

  // Convert to RGB
  const rgb = hsvToRgb(hue, saturation, brightness);
  const rgbString = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;

  return {
    rgb: rgbString,
    hue: {
      hue: Math.round(hue * 360),
      saturation: Math.round(saturation * 100),
      brightness: Math.round(brightness * 100)
    }
  };
} 