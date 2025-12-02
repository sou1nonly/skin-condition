/**
 * SkinAI - Skin Condition Analyzer
 * Frontend JavaScript Application
 */

class SkinAnalyzer {
    constructor() {
        this.imageFile = null;
        this.imageData = null;
        this.stream = null;
        this.analysisResults = null;
        
        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        // Sections
        this.uploadSection = document.getElementById('uploadSection');
        this.previewSection = document.getElementById('previewSection');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');

        // Upload elements
        this.dropZone = document.getElementById('dropZone');
        this.imageInput = document.getElementById('imageInput');
        this.selectBtn = document.getElementById('selectBtn');
        this.cameraBtn = document.getElementById('cameraBtn');

        // Preview elements
        this.previewImage = document.getElementById('previewImage');
        this.changeImageBtn = document.getElementById('changeImageBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');

        // Results elements
        this.conditionName = document.getElementById('conditionName');
        this.confidenceValue = document.getElementById('confidenceValue');
        this.conditionsList = document.getElementById('conditionsList');
        this.recommendationDescription = document.getElementById('recommendationDescription');
        this.tipsList = document.getElementById('tipsList');
        this.goodIngredients = document.getElementById('goodIngredients');
        this.badIngredients = document.getElementById('badIngredients');
        this.newAnalysisBtn = document.getElementById('newAnalysisBtn');
        this.downloadBtn = document.getElementById('downloadBtn');

        // Error elements
        this.errorMessage = document.getElementById('errorMessage');
        this.tryAgainBtn = document.getElementById('tryAgainBtn');

        // Camera modal elements
        this.cameraModal = document.getElementById('cameraModal');
        this.cameraVideo = document.getElementById('cameraVideo');
        this.cameraCanvas = document.getElementById('cameraCanvas');
        this.captureBtn = document.getElementById('captureBtn');
        this.closeCameraBtn = document.getElementById('closeCameraBtn');
    }

    initEventListeners() {
        // File selection
        this.selectBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.imageInput.click();
        });
        
        this.dropZone.addEventListener('click', () => this.imageInput.click());
        this.imageInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        this.dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e));

        // Camera
        this.cameraBtn.addEventListener('click', () => this.openCamera());
        this.captureBtn.addEventListener('click', () => this.capturePhoto());
        this.closeCameraBtn.addEventListener('click', () => this.closeCamera());

        // Preview actions
        this.changeImageBtn.addEventListener('click', () => this.resetToUpload());
        this.analyzeBtn.addEventListener('click', () => this.analyzeImage());

        // Result actions
        this.newAnalysisBtn.addEventListener('click', () => this.resetToUpload());
        this.downloadBtn.addEventListener('click', () => this.downloadReport());

        // Error actions
        this.tryAgainBtn.addEventListener('click', () => this.resetToUpload());

        // Close modal on backdrop click
        this.cameraModal.addEventListener('click', (e) => {
            if (e.target === this.cameraModal) {
                this.closeCamera();
            }
        });
    }

    // ===== File Handling =====
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        this.dropZone.classList.add('drag-over');
    }

    handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        this.dropZone.classList.remove('drag-over');
    }

    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        this.dropZone.classList.remove('drag-over');

        const file = event.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showError('Please select a valid image file.');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('Image file is too large. Maximum size is 10MB.');
            return;
        }

        this.imageFile = file;

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.imageData = e.target.result;
            this.previewImage.src = this.imageData;
            this.showSection('preview');
        };
        reader.readAsDataURL(file);
    }

    // ===== Camera Handling =====
    async openCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: 1280, height: 720 }
            });
            this.cameraVideo.srcObject = this.stream;
            this.cameraModal.classList.remove('hidden');
        } catch (error) {
            console.error('Camera error:', error);
            this.showError('Unable to access camera. Please check permissions.');
        }
    }

    capturePhoto() {
        const canvas = this.cameraCanvas;
        const video = this.cameraVideo;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        this.imageData = canvas.toDataURL('image/jpeg', 0.9);
        this.previewImage.src = this.imageData;

        // Convert to file
        canvas.toBlob((blob) => {
            this.imageFile = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
        }, 'image/jpeg', 0.9);

        this.closeCamera();
        this.showSection('preview');
    }

    closeCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.cameraModal.classList.add('hidden');
    }

    // ===== Analysis =====
    async analyzeImage() {
        if (!this.imageFile) {
            this.showError('No image selected.');
            return;
        }

        this.showSection('loading');

        try {
            const formData = new FormData();
            formData.append('image', this.imageFile);

            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            this.analysisResults = data;
            this.displayResults(data);
            this.showSection('results');

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(error.message || 'An error occurred during analysis.');
        }
    }

    displayResults(data) {
        // Main result
        this.conditionName.textContent = data.top_condition;
        this.confidenceValue.textContent = `${data.confidence}%`;

        // Update confidence badge color based on value
        const badge = document.getElementById('confidenceBadge');
        if (data.confidence >= 70) {
            badge.style.background = 'rgba(16, 185, 129, 0.2)';
            badge.style.color = '#10b981';
        } else if (data.confidence >= 40) {
            badge.style.background = 'rgba(245, 158, 11, 0.2)';
            badge.style.color = '#f59e0b';
        } else {
            badge.style.background = 'rgba(99, 102, 241, 0.2)';
            badge.style.color = '#818cf8';
        }

        // All conditions
        this.conditionsList.innerHTML = '';
        const sortedConditions = Object.entries(data.all_conditions)
            .sort((a, b) => b[1] - a[1]);

        sortedConditions.forEach(([name, percentage]) => {
            const item = document.createElement('div');
            item.className = 'condition-item';
            item.innerHTML = `
                <span class="name">${name}</span>
                <div class="bar-container">
                    <div class="bar" style="width: ${percentage}%"></div>
                </div>
                <span class="percentage">${percentage.toFixed(1)}%</span>
            `;
            this.conditionsList.appendChild(item);
        });

        // Recommendations
        const rec = data.recommendations;
        this.recommendationDescription.textContent = rec.description;

        // Tips
        this.tipsList.innerHTML = '';
        rec.tips.forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            this.tipsList.appendChild(li);
        });

        // Good ingredients
        this.goodIngredients.innerHTML = '';
        rec.ingredients_to_look_for.forEach(ingredient => {
            const tag = document.createElement('span');
            tag.className = 'ingredient-tag';
            tag.textContent = ingredient;
            this.goodIngredients.appendChild(tag);
        });

        // Bad ingredients
        this.badIngredients.innerHTML = '';
        rec.ingredients_to_avoid.forEach(ingredient => {
            const tag = document.createElement('span');
            tag.className = 'ingredient-tag';
            tag.textContent = ingredient;
            this.badIngredients.appendChild(tag);
        });
    }

    // ===== Report Download =====
    downloadReport() {
        if (!this.analysisResults) return;

        const data = this.analysisResults;
        const rec = data.recommendations;
        const date = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        let report = `
SKIN CONDITION ANALYSIS REPORT
==============================
Generated: ${date}

PRIMARY CONDITION DETECTED
--------------------------
Condition: ${data.top_condition}
Confidence: ${data.confidence}%

ALL DETECTED CONDITIONS
-----------------------
${Object.entries(data.all_conditions)
    .sort((a, b) => b[1] - a[1])
    .map(([name, val]) => `${name}: ${val.toFixed(1)}%`)
    .join('\n')}

ABOUT THIS CONDITION
--------------------
${rec.description}

RECOMMENDED TIPS
----------------
${rec.tips.map((tip, i) => `${i + 1}. ${tip}`).join('\n')}

INGREDIENTS TO LOOK FOR
-----------------------
${rec.ingredients_to_look_for.join(', ')}

INGREDIENTS TO AVOID
--------------------
${rec.ingredients_to_avoid.join(', ')}

==============================
DISCLAIMER: This analysis is for educational purposes only.
Always consult a dermatologist for professional medical advice.
        `.trim();

        const blob = new Blob([report], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `skin-analysis-report-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // ===== UI Helpers =====
    showSection(section) {
        // Hide all sections
        this.uploadSection.classList.add('hidden');
        this.previewSection.classList.add('hidden');
        this.loadingSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.errorSection.classList.add('hidden');

        // Show requested section
        switch (section) {
            case 'upload':
                this.uploadSection.classList.remove('hidden');
                break;
            case 'preview':
                this.previewSection.classList.remove('hidden');
                break;
            case 'loading':
                this.loadingSection.classList.remove('hidden');
                break;
            case 'results':
                this.resultsSection.classList.remove('hidden');
                break;
            case 'error':
                this.errorSection.classList.remove('hidden');
                break;
        }
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.showSection('error');
    }

    resetToUpload() {
        this.imageFile = null;
        this.imageData = null;
        this.analysisResults = null;
        this.imageInput.value = '';
        this.showSection('upload');
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.skinAnalyzer = new SkinAnalyzer();
});
