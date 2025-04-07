const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();

app.use(express.json());

// Serve the React app
app.use(express.static(path.join(__dirname, 'dist')));

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