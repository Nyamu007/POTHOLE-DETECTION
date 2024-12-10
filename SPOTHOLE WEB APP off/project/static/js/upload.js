document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file-upload');
    const dropZone = document.querySelector('.border-dashed');
    const selectFileBtn = document.getElementById('selectFile');
    const startUploadBtn = document.getElementById('startUpload');
    const previewSection = document.getElementById('previewSection');
    const previewImage = document.getElementById('previewImage');
    const previewVideo = document.getElementById('previewVideo');
    const resultsSection = document.getElementById('resultsSection');
    const results = document.getElementById('results');
    const uploadStatus = document.getElementById('uploadStatus');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    selectFileBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFileSelect);

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('border-red-600', 'bg-gray-700');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('border-red-600', 'bg-gray-700');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        handleFileSelect({ target: { files: dt.files } });
    });

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            startUploadBtn.disabled = false;
            startUploadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            uploadStatus.textContent = 'Ready to upload';

            // Show preview
            previewSection.classList.remove('hidden');
            const isVideo = file.type.startsWith('video/');
            
            if (isVideo) {
                previewVideo.classList.remove('hidden');
                previewImage.classList.add('hidden');
                previewVideo.src = URL.createObjectURL(file);
            } else {
                previewImage.classList.remove('hidden');
                previewVideo.classList.add('hidden');
                previewImage.src = URL.createObjectURL(file);
            }
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    startUploadBtn.addEventListener('click', async () => {
        const formData = new FormData(form);
        uploadStatus.textContent = 'Processing...';
        startUploadBtn.disabled = true;
        startUploadBtn.classList.add('opacity-50', 'cursor-not-allowed');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/upload_file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Upload failed');
            }

            const data = await response.json();
            uploadStatus.textContent = 'Complete';
            resultsSection.classList.remove('hidden');
            
            // Update detection stats
            document.getElementById('detectionCount').textContent = data.detections.length;
            if (data.detections.length > 0) {
                const avgConf = data.detections.reduce((acc, det) => acc + det.confidence, 0) / data.detections.length;
                document.getElementById('avgConfidence').textContent = `${(avgConf * 100).toFixed(1)}%`;
            }

            // Display results
            results.innerHTML = data.detections.map((det, i) => `
                <div class="bg-gray-800 p-4 rounded-lg border border-red-800 mb-4">
                    <p class="text-red-400 font-medium">Detection ${i + 1}</p>
                    <p class="text-red-500">Confidence: ${(det.confidence * 100).toFixed(1)}%</p>
                    ${det.bbox ? `
                        <p class="text-red-500">Location: (${det.bbox[0]}, ${det.bbox[1]})</p>
                        <p class="text-red-500">Size: ${det.bbox[2]-det.bbox[0]}x${det.bbox[3]-det.bbox[1]}px</p>
                    ` : ''}
                    <p class="text-red-500">Time: ${new Date(det.timestamp).toLocaleTimeString()}</p>
                </div>
            `).join('');

            // Show processed output if available
            if (data.output_path) {
                const outputImage = document.createElement('img');
                outputImage.src = data.output_path;
                outputImage.className = 'w-full h-auto rounded-lg border border-red-800 mt-4';
                results.appendChild(outputImage);
            }

        } catch (error) {
            console.error('Error:', error);
            uploadStatus.textContent = 'Failed: ' + error.message;
            startUploadBtn.disabled = false;
            startUploadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });
});