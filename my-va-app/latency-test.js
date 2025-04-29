const fetch = require('node-fetch');

async function testLatency() {
    console.log('Starting latency test...');
    
    // Test data - using a happy emotion (positive valence, high arousal)
    const testData = {
        valence: 0.95,
        arousal: 0.5
    };

    // Start timing
    const startTime = Date.now();
    console.log(`Sending emotion data at ${new Date().toISOString()}`);

    try {
        const response = await fetch('http://localhost:3000/api/control-lamp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testData),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        const endTime = Date.now();
        const latency = endTime - startTime;

        console.log('\nTest Results:');
        console.log('-------------');
        console.log(`Emotion sent: Happy (valence: ${testData.valence}, arousal: ${testData.arousal})`);
        console.log(`Start time: ${new Date(startTime).toISOString()}`);
        console.log(`End time: ${new Date(endTime).toISOString()}`);
        console.log(`Total latency: ${latency}ms`);
        console.log('Server response:', result);

    } catch (error) {
        console.error('Error during test:', error);
    }
}

// Run the test
testLatency(); 