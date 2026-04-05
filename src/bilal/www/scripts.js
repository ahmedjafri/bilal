
// Current date offset (0 = today, -1 = yesterday, 1 = tomorrow)
let dateOffset = 0;

document.addEventListener('DOMContentLoaded', function() {
  fetchMetadata();
  
  // Refresh data every minute
  setInterval(() => {
    if (dateOffset === 0) {
      fetchMetadata(); // Only auto-refresh for today
    }
  }, 60000);
  
  // Set up day navigation buttons
  document.getElementById('prev-day').addEventListener('click', () => {
    dateOffset--;
    fetchMetadata(dateOffset);
  });
  
  document.getElementById('next-day').addEventListener('click', () => {
    dateOffset++;
    fetchMetadata(dateOffset);
  });
});

function fetchMetadata(offset = 0) {
  const date = new Date();
  if (offset !== 0) {
    date.setDate(date.getDate() + offset);
  }
  
  const dateString = date.toISOString().split('T')[0]; // Format: YYYY-MM-DD
  
  fetch(`/metadata?date=${dateString}`)
    .then(response => response.json())
    .then(data => {
      updateNextAzan(data.upcoming_azan);
      generateDailyAzans(data.azans_for_day, data.upcoming_azan);
      updateCurrentDate(date);
    })
    .catch(error => {
      console.error('Error fetching metadata:', error);
    });
}

function updateCurrentDate(date) {
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const formattedDate = date.toLocaleDateString(undefined, options);
  document.getElementById('current-date').textContent = formattedDate;
}

function updateNextAzan(upcomingAzan) {
  const nextAzanName = document.getElementById('next-azan-name');
  const nextAzanTime = document.getElementById('next-azan-time');
  const countdown = document.getElementById('countdown');
  
  nextAzanName.textContent = formatSalatName(upcomingAzan.salat);
  nextAzanTime.textContent = upcomingAzan.time;
  
  // Calculate countdown
  updateCountdown(upcomingAzan.azan_time);
  // Update countdown every second
  setInterval(() => updateCountdown(upcomingAzan.azan_time), 1000);
}

function updateCountdown(timeString) {
  const targetTime = new Date(timeString);
  const now = new Date();
  const diffMs = targetTime - now;
  
  if (diffMs <= 0) {
    document.getElementById('countdown').textContent = "Now";
    return;
  }
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
  
  let countdownText = "";
  if (hours > 0) {
    countdownText += `${hours}h `;
  }
  countdownText += `${minutes}m ${seconds}s`;
  
  document.getElementById('countdown').textContent = countdownText;
}

function generateDailyAzans(azansForDay, upcomingAzan) {
  const dailyAzans = document.getElementById('daily-azans');
  dailyAzans.innerHTML = "";

  // Create elements for each prayer time
  azansForDay.forEach(azan => {
    const azanItem = document.createElement('div');
    azanItem.className = 'azan-time-item';
    
    // Highlight the next upcoming prayer
    if (azan.salat == upcomingAzan.salat && 
      azan.azan_time == upcomingAzan.azan_time) {
      azanItem.className += ' active';
    }

    const azanTime = new Date(azan.azan_time);
    // Format the date to "hh:mm AM/PM"
    const formattedTime = azanTime.toLocaleString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });

    azanItem.innerHTML = `
      <span class="azan-name">${formatSalatName(azan.salat)}</span>
      <span class="azan-time">${formattedTime}</span>
    `;
    
    dailyAzans.appendChild(azanItem);
  });
}

function getTimeFromUpcoming(upcomingAzan, salatName) {
  // This is a placeholder function since we don't have all times from the API
  // In a real implementation, the backend would provide all times
  if (salatName === upcomingAzan.salat) {
    return upcomingAzan.time.split(', ')[1];
  }
  
  // Return placeholder times for demonstration
  const placeholderTimes = {
    'FAJR': '05:29 AM',
    'ZUHR': '01:15 PM',
    'ASR': '04:45 PM',
    'MAGHRIB': '07:30 PM',
    'ISHA': '09:00 PM'
  };
  
  return placeholderTimes[salatName];
}

function formatSalatName(name) {
  // Convert FAJR to Fajr, etc.
  return name.charAt(0) + name.slice(1).toLowerCase();
}
