
// Function to open the modal window
function openModal() {
    document.getElementById('modal').style.display = 'block';
}

// Function to close the modal window
function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

// Function to add a new threshold rule
function addThreshold() {
    const value = document.getElementById('threshold-value').value;
    const operator = document.getElementById('operator').value;
    const action = document.getElementById('action').value;
    const datatype = document.getElementById('datatype').value; // Get the selected datatype

    if (value === '') {
        alert('Please fill in threshold value');
        return;
    }

    if(isNaN(parseFloat(value)) || !isFinite(value)){
        alert('Please enter a valid number');
        return;
    }

    // Create a new row for the table
    const table = document.getElementById('threshold-table');
    const newRow = table.insertRow(-1);
    const cell1 = newRow.insertCell(0);
    const cell2 = newRow.insertCell(1);
    const cell3 = newRow.insertCell(2);
    const cell4 = newRow.insertCell(3);
    const cell5 = newRow.insertCell(4); // Add a new cell for the datatype

    // Add data to the row
    cell1.innerHTML = datatype;
    cell2.innerHTML = operator;
    cell3.innerHTML = value;
    cell4.innerHTML = action; // Display the datatype in the table
    cell5.innerHTML = `<button onclick="editThreshold(this)">Edit</button> | <button onclick="deleteThreshold(this)">Delete</button>`;

    // Close the modal window
    closeModal();
}

// Function to edit a threshold rule
function editThreshold(button) {
    const row = button.parentNode.parentNode;
    const datatype = row.cells[0].innerHTML;
    const operator = row.cells[1].innerHTML;
    const value = row.cells[2].innerHTML;
    const action = row.cells[3].innerHTML; // Get the datatype from the table

    if (value === '') {
        alert('Please fill in threshold value');
        return;
    }

    if(isNaN(parseFloat(value)) || !isFinite(value)){
        alert('Please enter a valid number');
        return;
    }

    // Fill the modal window with existing data
    document.getElementById('threshold-value').value = value;
    document.getElementById('operator').value = operator;
    document.getElementById('action').value = action;
    document.getElementById('datatype').value = datatype; // Set the datatype in the modal window

    // Delete the row from the table
    row.parentNode.removeChild(row);

    // Open the modal window for editing
    openModal();
}

// Function to delete a threshold rule
function deleteThreshold(button) {
    const row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

// Function to save the table data
function saveRules() {
    const table = document.getElementById('threshold-table');
    const rows = table.rows;
    const thresholdData = [];

    // Iterate through rows to extract data
    for (let i = 1; i < rows.length; i++) {
        const datatype = rows[i].cells[0].innerHTML;
        const operator = rows[i].cells[1].innerHTML;
        const value = rows[i].cells[2].innerHTML;
        const action = rows[i].cells[3].innerHTML; // Get the datatype from the table
        thresholdData.push({ value, operator, action, datatype }); // Include the datatype in the threshold data
    }

    // Log the threshold data
    console.log(thresholdData);

    // Send thresholdData to the webserver
    fetch('/save_threshold_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(thresholdData),
    })
    .then(response => {
        if (response.ok) {
            console.log('Threshold data saved successfully.');
        } else {
            console.error('Failed to save threshold data.');
        }
    })
    .catch(error => console.error('Error saving threshold data:', error));
}

// Function to load the table data
function refreshRules() {
    fetch('/load_rules')
    .then(response => response.json())
    .then(data => {
        // Clear existing rows in the table
        const table = document.getElementById('threshold-table');
        table.innerHTML = `
            <th>Datatype</th>
            <th>Operator</th>
            <th>Threshold Value</th>
            <th>Action</th>
            <th>Options</th>
        `;

        // Iterate through the received data to populate the table
        data.forEach(rule => {
            const newRow = table.insertRow(-1);
            const cell1 = newRow.insertCell(0);
            const cell2 = newRow.insertCell(1);
            const cell3 = newRow.insertCell(2);
            const cell4 = newRow.insertCell(3);
            const cell5 = newRow.insertCell(4); // Add a new cell for the datatype
         
            cell1.innerHTML = rule.datatype;
            cell2.innerHTML = rule.operator;
            cell3.innerHTML = rule.value;
            cell4.innerHTML = rule.action; // Display the datatype in the table
            cell5.innerHTML = `<button onclick="editThreshold(this)">Edit</button> | <button onclick="deleteThreshold(this)">Delete</button>`;
        
        });
    })
    .catch(error => console.error('Error loading rules:', error));
}

// Update data 
function updateData() {
    console.log('Updating data...');

    // Read sensor data from the JSON
    fetch('/get_sensor_data')
    .then(response => response.json())
    .then(data => {
        // Separate data for each parameter
        const labels = data.map(item => item.timestamp);
        const temperatureData = data.map(item => item.temperature);
        const humidityData = data.map(item => item.humidity);
        const pressureData = data.map(item => item.pressure);
        const luxData = data.map(item => item.lux);
        const uvsData = data.map(item => item.uvs);

        // Create graphs for each parameter
        createOrUpdateGraph('temperature-graph', 'Temperature (°C)', labels, temperatureData, '#ff6384');
        createOrUpdateGraph('humidity-graph', 'Humidity (%)', labels, humidityData, '#36a2eb');
        createOrUpdateGraph('pressure-graph', 'Pressure', labels, pressureData, '#ffce56');
        createOrUpdateGraph('lux-graph', 'Lux', labels, luxData, '#4bc0c0');
        createOrUpdateGraph('uvs-graph', 'UVS', labels, uvsData, '#ff9f40');

        const latest = data[data.length - 1];

        document.getElementById('temperature').textContent = `Temperature: ${latest.temperature}°C`;
        document.getElementById('humidity').textContent = `Humidity: ${latest.humidity}%`;
        document.getElementById('pressure').textContent = `Pressure: ${latest.pressure} hPa`;
        document.getElementById('lux').textContent = `Lux: ${latest.lux}`;
        document.getElementById('uvs').textContent = `UVS: ${latest.uvs}`;
                    
    })
    .catch(error => console.error('Error fetching data:', error));

    // Read action data from the JSON
    // Code Here
}

// Function to create or update a graph
function createOrUpdateGraph(canvasId, label, labels, data, borderColor) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    let chart = Chart.getChart(canvasId);

    if (chart) {
        // Update the existing chart
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
    } else {
        // Create a new chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    borderColor: borderColor,
                    backgroundColor: 'transparent'
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            unit: 'hour',
                            displayFormats: {
                                hour: 'HH:mm'
                            }
                        }
                    }]
                }
            }
        });
    }
}

function modeSwitcher(){
    var mode = document.getElementById('mode-switch').checked;
    if(mode){
        sendServerMessage('function_mode:auto');
        document.getElementById('window-div').hidden = true;
        document.getElementById('light-div').hidden = true;
    } else {
        sendServerMessage('function_mode:manual');
        document.getElementById('window-div').hidden = false;
        document.getElementById('light-div').hidden = false;
    }
}

function toggleWindow(){
    var window = document.getElementById('window-switch').checked;
    if(window){
        sendServerMessage('action_control:window_on');
    } else {
        sendServerMessage('action_control:window_off');
    }
}

function toggleLight(){
    var light = document.getElementById('light-switch').checked;
    if(light){
        sendServerMessage('action_control:light_on');
    } else {
        sendServerMessage('action_control:light_off');
    }

}

function sendServerMessage(message) {
    fetch('/send_server_message', {
        method: 'POST', // or 'GET'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Initial call to update sensor data
updateData();
modeSwitcher();
refreshRules();
// Set interval to update sensor data every 3 seconds
setInterval(updateData, 3000);

document.getElementById('mode-switch').addEventListener('change', function() {
    modeSwitcher();
});

document.getElementById('window-switch').addEventListener('click', function() {
    toggleWindow();
});

document.getElementById('light-switch').addEventListener('click', function() {
    toggleLight();
});
