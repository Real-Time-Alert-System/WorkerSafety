// script.js - Enhanced to handle video uploads and processing
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.querySelector('.file-input');
    const dropArea = document.querySelector('.file-drop-area');
    const fileMsg = document.querySelector('.file-msg');
    const resultItems = document.getElementById('result-items');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');
    const mediaContainer = document.getElementById('media-preview');
    
    // Hide results initially
    resultsContainer.classList.add('hidden');
    
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle file drop
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateFileMessage(files);
    }
    
    // Handle file selection via input
    fileInput.addEventListener('change', function() {
        updateFileMessage(this.files);
    });
    
    function updateFileMessage(files) {
        if (files.length > 0) {
            const fileName = files[0].name;
            fileMsg.textContent = fileName;
            
            // Show preview for the selected file
            showMediaPreview(files[0]);
        } else {
            fileMsg.textContent = 'or drag and drop files here';
            mediaContainer.innerHTML = '';
        }
    }
    
    function showMediaPreview(file) {
        mediaContainer.innerHTML = '';
        
        if (file.type.startsWith('image/')) {
            // For image files
            const img = document.createElement('img');
            img.classList.add('preview-image');
            img.file = file;
            mediaContainer.appendChild(img);
            
            const reader = new FileReader();
            reader.onload = (e) => { img.src = e.target.result; };
            reader.readAsDataURL(file);
        } else if (file.type.startsWith('video/')) {
            // For video files
            const video = document.createElement('video');
            video.classList.add('preview-video');
            video.controls = true;
            video.preload = 'metadata';
            mediaContainer.appendChild(video);
            
            const reader = new FileReader();
            reader.onload = (e) => { video.src = e.target.result; };
            reader.readAsDataURL(file);
        }
    }
    
    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please select a file first');
            return;
        }
        
        // Get location and area type values
        const location = document.getElementById('location').value || 'Unknown';
        const areaType = document.getElementById('area-type').value || 'default';
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        resultItems.innerHTML = '';
        resultsContainer.classList.remove('hidden');
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('location', location);
        formData.append('area_type', areaType);
        
        // Send request to server
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
            
            // Display results
            if (data.violations && data.violations.length > 0) {
                displayViolations(data.violations);
            } else {
                resultItems.innerHTML = '<div class="success-message">No PPE violations detected!</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingIndicator.classList.add('hidden');
            resultItems.innerHTML = '<div class="error-message">Error processing file. Please try again.</div>';
        });
    });
    
    function displayViolations(violations) {
        resultItems.innerHTML = '';
        
        // Header for violations
        const header = document.createElement('h4');
        header.textContent = `${violations.length} PPE Violations Detected`;
        header.className = 'violation-header';
        resultItems.appendChild(header);
        
        // List of violations
        const list = document.createElement('ul');
        list.className = 'violation-list';
        
        violations.forEach(violation => {
            const item = document.createElement('li');
            item.className = 'violation-item';
            item.innerHTML = `
                <span class="violation-type"><i class="fas fa-exclamation-triangle"></i> Missing: ${formatEquipmentType(violation.type)}</span>
                <span class="violation-severity ${getSeverityClass(violation.type)}">
                    ${getSeverityLabel(violation.type)}
                </span>
            `;
            list.appendChild(item);
        });
        
        resultItems.appendChild(list);
        
        // Add notification info
        const notificationInfo = document.createElement('div');
        notificationInfo.className = 'notification-info';
        notificationInfo.innerHTML = '<i class="fas fa-bell"></i> Notifications sent to safety personnel';
        resultItems.appendChild(notificationInfo);
    }
    
    function formatEquipmentType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    function getSeverityClass(equipmentType) {
        const severityMap = {
            'helmet': 'high-severity',
            'safety_goggles': 'high-severity',
            'vest': 'medium-severity',
            'safety_vest': 'medium-severity',
            'gloves': 'medium-severity',
            'mask': 'medium-severity'
        };
        return severityMap[equipmentType] || 'low-severity';
    }
    
    function getSeverityLabel(equipmentType) {
        const severityMap = {
            'helmet': 'High Risk',
            'safety_goggles': 'High Risk',
            'vest': 'Medium Risk',
            'safety_vest': 'Medium Risk',
            'gloves': 'Medium Risk',
            'mask': 'Medium Risk'
        };
        return severityMap[equipmentType] || 'Low Risk';
    }
});
