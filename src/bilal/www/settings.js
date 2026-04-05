
document.addEventListener('DOMContentLoaded', function() {
  // Load settings
  loadSettings();
  
  // Set up event listeners for buttons
  document.getElementById('play-azan').addEventListener('click', playAzan);
  document.getElementById('stop-azan').addEventListener('click', stopAzan);
  document.getElementById('save-settings').addEventListener('click', saveSettings);
  document.getElementById('back-to-main').addEventListener('click', function() {
    window.location.href = '/';
  });
});

function loadSettings() {
  // Fetch metadata and config
  Promise.all([
    fetch('/metadata').then(response => response.json()),
    fetch('/config').then(response => response.json())
  ])
  .then(([metadata, config]) => {
    // Populate azan files dropdown
    const azanSelect = document.getElementById('azan-file-select');
    metadata.available_azans.forEach(azan => {
      const option = document.createElement('option');
      option.value = azan;
      option.textContent = azan.replace('.mp3', '').replace(/_/g, ' ');
      azanSelect.appendChild(option);
    });
    
    // Set the current azan file if available in config
    if (config.azan_file) {
      azanSelect.value = config.azan_file;
    }
    
    // Set quiet hours
    document.getElementById('quiet-start').value = config.quiet_times_start || '';
    document.getElementById('quiet-end').value = config.quiet_times_end || '';
    document.getElementById('quiet-hours-enabled').checked = config.quiet_times_enabled || false;
    
    // Populate calculation methods dropdown
    const methodSelect = document.getElementById('calculation-method');
    for (const [key, value] of Object.entries(metadata.azan_methods)) {
      const option = document.createElement('option');
      option.value = key;
      option.textContent = value.name;
      methodSelect.appendChild(option);
    }
    
    // Set current calculation settings
    document.getElementById('latitude').value = config.latitude || '';
    document.getElementById('longitude').value = config.longitude || '';
    
    if (config.calculation_method) {
      methodSelect.value = config.calculation_method;
    }
  })
  .catch(error => {
    console.error('Error loading settings:', error);
  });
}

function playAzan() {
  const azanFile = document.getElementById('azan-file-select').value;
  fetch(`/command/play_azan?file=${azanFile}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to play azan');
      }
    })
    .catch(error => {
      console.error('Error playing azan:', error);
    });
}

function stopAzan() {
  fetch('/command/stop_azan')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to stop azan');
      }
    })
    .catch(error => {
      console.error('Error stopping azan:', error);
    });
}

function saveSettings() {
  // Gather settings from form
  const config = {
    azan_file: document.getElementById('azan-file-select').value,
    quiet_times_start: document.getElementById('quiet-start').value,
    quiet_times_end: document.getElementById('quiet-end').value,
    quiet_times_enabled: document.getElementById('quiet-hours-enabled').checked,
    latitude: parseFloat(document.getElementById('latitude').value),
    longitude: parseFloat(document.getElementById('longitude').value),
    calculation_method: document.getElementById('calculation-method').value
  };
  
  // Send settings to server
  fetch('/config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(config)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to save settings');
    }
    return response.json();
  })
  .then(data => {
    alert('Settings saved successfully!');
    // Reload settings to ensure we display the correct values
    loadSettings();
  })
  .catch(error => {
    console.error('Error saving settings:', error);
    alert('Error saving settings. Please try again.');
  });
}
