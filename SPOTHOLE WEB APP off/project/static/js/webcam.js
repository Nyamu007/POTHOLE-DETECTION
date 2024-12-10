// Webcam handling
const videoFeed = document.getElementById('video-feed');
const modalVideoFeed = document.getElementById('modal-video-feed');
const toggleWebcamBtn = document.getElementById('toggleWebcam');
const toggleModalWebcamBtn = document.getElementById('toggleModalWebcam');
const modal = document.getElementById('webcamModal');
const closeModalBtn = document.getElementById('closeModal');

async function startWebcam() {
    try {
        // Start backend webcam processing
        const response = await fetch('/start_webcam');
        if (!response.ok) {
            throw new Error('Failed to start webcam processing');
        }

        // Show video feeds
        const feedUrl = '/video_feed';
        if (videoFeed) {
            videoFeed.src = feedUrl;
            videoFeed.style.display = 'block';
        }
        if (modalVideoFeed) {
            modalVideoFeed.src = feedUrl;
            modalVideoFeed.style.display = 'block';
        }

        // Update UI
        toggleModalWebcamBtn.classList.remove('hidden');
        toggleWebcamBtn.textContent = 'Stop Webcam';
        
    } catch (error) {
        console.error('Error starting webcam:', error);
        alert('Failed to start webcam. Please ensure camera permissions are granted.');
    }
}

async function stopWebcam() {
    try {
        // Stop backend processing
        await fetch('/stop_webcam');

        // Update UI
        if (videoFeed) {
            videoFeed.style.display = 'none';
            videoFeed.src = '';
        }
        if (modalVideoFeed) {
            modalVideoFeed.style.display = 'none';
            modalVideoFeed.src = '';
        }
        modal.style.display = 'none';
        toggleWebcamBtn.textContent = 'Start Webcam';
        toggleModalWebcamBtn.classList.add('hidden');

    } catch (error) {
        console.error('Error stopping webcam:', error);
    }
}

// Event Listeners
toggleWebcamBtn.addEventListener('click', async () => {
    if (toggleWebcamBtn.textContent === 'Start Webcam') {
        await startWebcam();
    } else {
        await stopWebcam();
    }
});

toggleModalWebcamBtn.addEventListener('click', () => {
    modal.style.display = 'block';
    if (modalVideoFeed && !modalVideoFeed.src) {
        modalVideoFeed.src = '/video_feed';
        modalVideoFeed.style.display = 'block';
    }
});

closeModalBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Handle coordinates display
const showCoordinatesBtn = document.getElementById('showCoordinates');
const coordinatesPanel = document.getElementById('coordinatesPanel');
const coordinatesDiv = document.getElementById('coordinates');

showCoordinatesBtn.addEventListener('click', async () => {
    coordinatesPanel.classList.toggle('hidden');
    if (!coordinatesPanel.classList.contains('hidden')) {
        await updateCoordinates();
    }
});

async function updateCoordinates() {
    try {
        const response = await fetch('/api/coordinates');
        if (!response.ok) throw new Error('Failed to fetch coordinates');
        
        const data = await response.json();
        
        coordinatesDiv.innerHTML = data.map(coord => `
            <div class="bg-gray-700 p-4 rounded-lg border border-gray-600 mb-4">
                <p class="text-gray-300">Time: ${new Date(coord.timestamp).toLocaleString()}</p>
                <p class="text-white font-medium">Position: (${coord.center_x}, ${coord.center_y})</p>
                <p class="text-white font-medium">Confidence: ${(coord.confidence * 100).toFixed(1)}%</p>
                ${coord.bbox ? `<p class="text-gray-300">Size: ${coord.bbox[2]-coord.bbox[0]}x${coord.bbox[3]-coord.bbox[1]}px</p>` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error fetching coordinates:', error);
        coordinatesDiv.innerHTML = '<p class="text-red-500">Failed to load coordinates</p>';
    }
}

// Update coordinates periodically when panel is visible
setInterval(() => {
    if (!coordinatesPanel.classList.contains('hidden')) {
        updateCoordinates();
    }
}, 1000);