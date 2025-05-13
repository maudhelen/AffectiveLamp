const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { exec } = require('child_process');

const app = express();

app.use(express.json());

// Serve the React app
app.use(express.static(path.join(__dirname, 'dist')));

// Function to get current time in Madrid timezone and round down to nearest even minute
function getCurrentMadridTime() {
    // Get current time in Madrid timezone
    const now = new Date();
    const madridTime = new Date(now.toLocaleString('en-US', { timeZone: 'Europe/Madrid' }));
    
    // Round down to nearest even minute
    const minutes = madridTime.getMinutes();
    const roundedMinutes = Math.floor(minutes / 2) * 2;
    madridTime.setMinutes(roundedMinutes);
    madridTime.setSeconds(0);
    madridTime.setMilliseconds(0);
    
    // Format as ISO string with Z suffix
    return madridTime.toISOString().replace('.000Z', 'Z');
}

// Function to convert Madrid time to UTC for Garmin data
function convertToUTC(madridTime) {
    const date = new Date(madridTime);
    // Add 2 hours to convert from Madrid time to UTC
    date.setHours(date.getHours() + 2);
    return date.toISOString().replace('Z', '');
}

// Function to round timestamp down to nearest even minute
function roundTimestamp(timestamp) {
    const date = new Date(timestamp);
    const minutes = date.getMinutes();
    const roundedMinutes = Math.floor(minutes / 2) * 2;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    return date.toISOString().replace('Z', ''); // Remove Z suffix
}

// Endpoint for emotion prediction
app.post('/api/predict-emotion', async (req, res) => {
    try {
        // Get current Madrid time rounded to nearest even minute
        const madridTime = getCurrentMadridTime();
        console.log('\n=== Prediction Request Debug ===');
        console.log('1. Current Madrid Time (rounded to even minute):', madridTime);
        console.log('2. Current Madrid Time (local format):', new Date(madridTime).toLocaleString('en-US', { timeZone: 'Europe/Madrid' }));

        // Run the Python script to predict emotion
        const pythonScript = path.join(__dirname, '..', 'models', 'predict_emotion.py');
        console.log('\n3. Running Python script:', pythonScript);
        
        const pythonProcess = spawn('python3', [pythonScript, madridTime], {
            cwd: path.join(__dirname, '..')
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString();
            console.log('\n4. Python script output:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString();
            console.log('\n5. Python script error:', data.toString());
        });

        const exitCode = await new Promise((resolve, reject) => {
            pythonProcess.on('close', (code) => {
                console.log('\n6. Python script exit code:', code);
                resolve(code);
            });
            pythonProcess.on('error', (err) => {
                console.log('\n7. Python script error:', err);
                reject(err);
            });
        });

        if (exitCode !== 0) {
            return res.status(500).json({ error: 'Error running prediction script', details: stderr });
        }

        // Parse the prediction results - only use the last line
        try {
            const lines = stdout.trim().split('\n');
            const lastLine = lines[lines.length - 1];
            console.log('\n8. Last line of output:', lastLine);
            
            const prediction = JSON.parse(lastLine);
            console.log('\n9. Parsed prediction:', prediction);
            
            if (prediction.error) {
                return res.status(500).json({ error: prediction.error });
            }

            // Get color from position
            const color = getColorFromPosition(prediction.valence, prediction.arousal);
            console.log('\n10. Calculated color:', color);

            // Return the prediction results with the Madrid timestamp and color
            const response = {
                valence: prediction.valence,
                arousal: prediction.arousal,
                emotion: prediction.emotion,
                timestamp: madridTime,
                color: color
            };
            
            console.log('\n11. Final response:', response);
            console.log('=== End of Prediction Request ===\n');
            
            res.json(response);
        } catch (parseError) {
            console.error('\nError parsing prediction results:', parseError);
            console.error('Full stdout:', stdout);
            return res.status(500).json({ error: 'Error parsing prediction results', details: parseError.message });
        }

    } catch (error) {
        console.error('\nError:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Add this helper function at the top of the file
function getColorFromPosition(valence, arousal) {
    // Calculate hue based on quadrant
    let hue;
    if (valence >= 0 && arousal >= 0) {
        hue = 120; // Green for positive valence and arousal
    } else if (valence >= 0 && arousal < 0) {
        hue = 60; // Yellow for positive valence, negative arousal
    } else if (valence < 0 && arousal < 0) {
        hue = 240; // Blue for negative valence and arousal
    } else {
        hue = 0; // Red for negative valence, positive arousal
    }

    // Calculate saturation based on distance from center
    const distance = Math.sqrt(valence * valence + arousal * arousal);
    const saturation = Math.min(1, distance * 2);

    // Calculate brightness based on arousal
    const brightness = 0.5 + (arousal * 0.5);

    return {
        rgb: hsvToRgb(hue, saturation, brightness),
        hue: {
            hue: hue,
            saturation: saturation,
            brightness: brightness
        }
    };
}

// Helper function to convert HSV to RGB
function hsvToRgb(h, s, v) {
    h = h / 360;
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

    return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;
}

// Endpoint to control the lamp
app.post('/api/control-lamp', async (req, res) => {
    try {
        const { valence, arousal } = req.body;
        
        // Validate input
        if (typeof valence !== 'number' || typeof arousal !== 'number') {
            return res.status(400).json({ error: 'Valence and arousal must be numbers' });
        }

        // Path to the change_color.py script
        const scriptPath = path.join(__dirname, '..', 'light', 'change_color.py');
        
        // Run the Python script using spawn
        const pythonProcess = spawn('python3', [scriptPath, valence.toString(), arousal.toString()], {
            cwd: path.join(__dirname, '..')
        });

        let stdout = '';
        let stderr = '';

        // Collect stdout
        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        // Collect stderr
        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        // Wait for the process to complete
        const exitCode = await new Promise((resolve, reject) => {
            pythonProcess.on('close', (code) => {
                resolve(code);
            });
            pythonProcess.on('error', (err) => {
                reject(err);
            });
        });

        if (exitCode !== 0) {
            return res.status(500).json({ 
                error: 'Failed to control light', 
                details: stderr || 'Python script failed'
            });
        }

        res.json({ success: true, message: 'Lamp color updated successfully' });

    } catch (error) {
        console.error('Error controlling lamp:', error);
        res.status(500).json({ error: 'Failed to control lamp', details: error.message });
    }
});

// Endpoint to save emotion data
app.post('/api/save-emotion', (req, res) => {
  const { data } = req.body;
  const { timestamp, valence, arousal, closestEmotion, color } = data;

  // Convert timestamp to Madrid timezone, add 2 hours, and round to nearest even minute
  const date = new Date(timestamp);
  // Add 2 hours to get correct Madrid time
  date.setHours(date.getHours() + 2);
  const minutes = date.getMinutes();
  const roundedMinutes = Math.round(minutes / 2) * 2;
  date.setMinutes(roundedMinutes);
  date.setSeconds(0);
  date.setMilliseconds(0);

  // Format timestamp to match required format (YYYY-MM-DDTHH:MM:00Z)
  const formattedTimestamp = date.toISOString().replace('.000Z', 'Z');
  const csvLine = `${formattedTimestamp},${valence},${arousal},${closestEmotion.name},${color.hue.hue},${color.hue.saturation},${color.hue.brightness}\n`;

  // Ensure data directory exists
  const dataDir = path.join(__dirname, 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir);
  }

  fs.appendFile(path.join(dataDir, 'emotion_data.csv'), csvLine, (err) => {
    if (err) {
      console.error('Error saving emotion data:', err);
      return res.status(500).json({ error: 'Failed to save emotion data' });
    }
    res.json({ success: true });
  });
});

// Endpoint to save prediction data
app.post('/api/save-prediction', (req, res) => {
  const { data } = req.body;
  const { timestamp, valence, arousal, closestEmotion } = data;

  // Use the exact timestamp from the prediction without any modification
  const formattedTimestamp = timestamp;
  const csvLine = `${formattedTimestamp},${valence},${arousal},${closestEmotion.name}\n`;

  // Ensure data directory exists
  const dataDir = path.join(__dirname, 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir);
  }

  fs.appendFile(path.join(dataDir, 'predictions.csv'), csvLine, (err) => {
    if (err) {
      console.error('Error saving prediction:', err);
      return res.status(500).json({ error: 'Failed to save prediction' });
    }
    res.json({ success: true });
  });
});

// Add a GET endpoint to retrieve the data file
app.get('/api/emotion-data', (req, res) => {
  const filePath = path.join(__dirname, 'data', 'emotion_data.csv');
  console.log('Attempting to read file:', filePath);
  if (fs.existsSync(filePath)) {
    try {
      const data = fs.readFileSync(filePath, 'utf8');
      console.log('File contents:', data);
      res.sendFile(filePath);
    } catch (err) {
      console.error('Error reading file:', err);
      res.status(500).json({ error: 'Failed to read file', details: err.message });
    }
  } else {
    console.log('File not found');
    res.status(404).json({ error: 'No emotion data found' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Current directory: ${__dirname}`);
  console.log(`Data will be saved to: ${path.join(__dirname, 'data', 'emotion_data.csv')}`);
}); 