const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const app = express();

app.use(express.json());

// Serve the React app
app.use(express.static(path.join(__dirname, 'dist')));

// Hardcoded timestamp for testing
const HARDCODED_TIMESTAMP = '2025-04-27T16:46:00Z';

// Function to round timestamp down to nearest even minute
function roundTimestamp(timestamp) {
    const date = new Date(timestamp);
    const minutes = date.getMinutes();
    const roundedMinutes = Math.floor(minutes / 2) * 2;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    return date.toISOString();
}

// Endpoint for emotion prediction
app.post('/api/predict-emotion', async (req, res) => {
    try {
        // Get timestamp from request or use hardcoded one
        const timestamp = req.body.timestamp ? roundTimestamp(req.body.timestamp) : HARDCODED_TIMESTAMP;
        console.log(`Using timestamp: ${timestamp}`);

        // Run the Python script to predict emotion
        const pythonScript = path.join(__dirname, '..', 'models', 'predict_emotion.py');
        const pythonProcess = spawn('python3', [pythonScript, timestamp], {
            cwd: path.join(__dirname, '..')
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        const exitCode = await new Promise((resolve, reject) => {
            pythonProcess.on('close', (code) => {
                resolve(code);
            });
            pythonProcess.on('error', (err) => {
                reject(err);
            });
        });

        if (exitCode !== 0) {
            return res.status(500).json({ error: 'Error running prediction script', details: stderr });
        }

        // Parse the prediction results
        const prediction = JSON.parse(stdout);
        console.log('Prediction results:', prediction);

        // Change the light color based on VA values
        const lightScript = path.join(__dirname, '..', 'light', 'change_color.py');
        const lightProcess = spawn('python3', [lightScript, prediction.valence.toString(), prediction.arousal.toString()], {
            cwd: path.join(__dirname, '..')
        });

        let lightStdout = '';
        let lightStderr = '';

        lightProcess.stdout.on('data', (data) => {
            lightStdout += data.toString();
        });

        lightProcess.stderr.on('data', (data) => {
            lightStderr += data.toString();
        });

        const lightExitCode = await new Promise((resolve, reject) => {
            lightProcess.on('close', (code) => {
                resolve(code);
            });
            lightProcess.on('error', (err) => {
                reject(err);
            });
        });

        if (lightExitCode !== 0) {
            return res.status(500).json({ error: 'Error controlling light', details: lightStderr });
        }

        // Return both the prediction and the emotion label
        res.json({
            valence: prediction.valence,
            arousal: prediction.arousal,
            emotion: prediction.emotion
        });

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

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
  console.log('Received emotion data:', req.body);
  const { data } = req.body;
  
  // Create absolute path for data directory and file
  const dataDir = path.join(__dirname, 'data');
  const filePath = path.join(dataDir, 'emotion_data.csv');
  
  console.log('Current directory:', __dirname);
  console.log('Data directory:', dataDir);
  console.log('File path:', filePath);
  
  // Create directory if it doesn't exist
  if (!fs.existsSync(dataDir)) {
    console.log('Creating data directory:', dataDir);
    try {
      fs.mkdirSync(dataDir, { recursive: true });
      console.log('Data directory created successfully');
    } catch (err) {
      console.error('Error creating directory:', err);
      res.status(500).json({ error: 'Failed to create directory', details: err.message });
      return;
    }
  }
  
  // Create headers if file doesn't exist
  if (!fs.existsSync(filePath)) {
    console.log('Creating new CSV file with headers');
    try {
      const headers = 'timestamp,valence,arousal,emotion,hue,saturation,brightness\n';
      fs.writeFileSync(filePath, headers, 'utf8');
      console.log('Headers written successfully');
    } catch (err) {
      console.error('Error writing headers:', err);
      res.status(500).json({ error: 'Failed to create file', details: err.message });
      return;
    }
  }

  // Append data to file
  try {
    // Format timestamp to match the desired format (YYYY-MM-DDTHH:MM:00Z)
    const formattedData = data.replace(/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}):\d{2}(\.\d{3}Z)/, '$1:00Z');
    
    fs.appendFileSync(filePath, formattedData, 'utf8');
    console.log('Successfully wrote data:', formattedData);
    console.log('To file:', filePath);
    res.json({ success: true, filePath });
  } 
  catch (err) {
        console.error('Error writing to file:', err);
        res.status(500).json({ error: 'Failed to save data', details: err.message });
  }
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