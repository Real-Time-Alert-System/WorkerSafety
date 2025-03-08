// script.js
document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.querySelector('.file-drop-area');
    const fileInput = document.querySelector('.file-input');
    const fileMsg = document.querySelector('.file-msg');
    const form = document.getElementById('upload-form');
    const results = document.getElementById('results');
    const uploadedImage = document.getElementById('uploaded-image');
    const resultItems = document.getElementById('result-items');
    const loading = document.getElementById('loading');
    
    // Navigation smooth scroll
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            window.scrollTo({
                top: targetSection.offsetTop - 80,
                behavior: 'smooth'
            });
            
            // Update active state
            document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // File upload handling
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
        dropArea.classList.add('is-active');
    }
    
    function unhighlight() {
        dropArea.classList.remove('is-active');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateFileMessage();
    }
    
    fileInput.addEventListener('change', updateFileMessage);
    
    function updateFileMessage() {
        let filename = '';
        if (fileInput.files && fileInput.files.length) {
            filename = fileInput.files[0].name;
            fileMsg.textContent = filename;
        }
    }
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!fileInput.files || !fileInput.files[0]) {
            alert('Please select an image to upload');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        // Show loading
        loading.classList.remove('hidden');
        results.classList.add('active');
        resultItems.innerHTML = '';
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayResults(data);
            } else {
                alert(data.error || 'An error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during upload');
        })
        .finally(() => {
            loading.classList.add('hidden');
        });
    });
    
    function displayResults(data) {
        // Set the image
        uploadedImage.src = data.filepath;
        
        // Clear previous results
        resultItems.innerHTML = '';
        
        // Display overall safety status
        const overallStatus = document.createElement('div');
        overallStatus.className = `ppe-item ${data.results.safe ? 'detected' : 'missing'}`;
        overallStatus.innerHTML = `
            <i class="fas ${data.results.safe ? 'fa-check-circle' : 'fa-exclamation-triangle'}"></i>
            <div>
                <h4>Overall Safety Status</h4>
                <p>${data.results.safe ? 'Worker is properly equipped with PPE' : 'Safety violation detected'}</p>
            </div>
        `;
        resultItems.appendChild(overallStatus);
        
        // Display individual PPE items
        const ppeItems = {
            helmet: { icon: 'fa-hard-hat', name: 'Safety Helmet' },
            vest: { icon: 'fa-vest', name: 'Safety Vest' },
            gloves: { icon: 'fa-mitten', name: 'Safety Gloves' },
            goggles: { icon: 'fa-glasses', name: 'Safety Goggles' }
        };
        
        for (const [item, detected] of Object.entries(data.results.detections)) {
            const ppeItem = document.createElement('div');
            ppeItem.className = `ppe-item ${detected ? 'detected' : 'missing'}`;
            ppeItem.innerHTML = `
                <i class="fas ${detected ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                <div>
                    <h4>${ppeItems[item].name}</h4>
                    <p>${detected ? 'Properly worn' : 'Not detected or improperly worn'}</p>
                </div>
            `;
            resultItems.appendChild(ppeItem);
        }
    }
    
    // Scroll event to change header background
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        header.classList.toggle('scrolled', window.scrollY > 50);
    });
});
