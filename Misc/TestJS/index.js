const { spawn, exec } = require('child_process');

// Path to your compiled C executable
const cExecutablePath = '/home/nin/Downloads/TestC/main';

// Function to execute the C code and capture output
function executeCCode() {
    // Spawn the child process to execute the C code
    const childProcess = spawn(cExecutablePath);

    // Listen for data events on stdout to capture the output
    let output = '';
    childProcess.stdout.on('data', (data) => {
        output += data.toString();
    });

    // Listen for the close event to know when the process has finished
    childProcess.on('close', (code) => {
        if (code === 0) {
            try {
              	let thisOutput = output.toString();
              	console.log(JSON.parse(thisOutput));
                // Parse the JSON-like output into a JavaScript object
                //const sensorData = JSON.parse(output);
                // Use the sensor data as needed
                //console.log(sensorData);
            } catch (error) {
              	console.log(output)
                console.error('Error parsing output:', error);
            }
        } else {
            console.error('Child process exited with code', code);
        }

        // Execute the C code again after a delay
        setTimeout(executeCCode, 1000); // Adjust delay as needed
    });

    // Handle errors in the child process
    childProcess.on('error', (error) => {
        console.error('Child process error:', error);
        // Retry execution after a delay
        setTimeout(executeCCode, 1000); // Adjust delay as needed
    });
}

// Start executing the C code
executeCCode();