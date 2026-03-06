// AutoML Platform Dashboard JavaScript

class AutoMLDashboard {
    constructor() {
        this.baseURL = '';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadAllData();
        this.updateLastUpdatedTime();
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadAllData();
            this.updateLastUpdatedTime();
        }, 30000);
    }

    setupEventListeners() {
        // Prediction form submission
        document.getElementById('prediction-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.makePrediction();
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadAllData();
            this.updateLastUpdatedTime();
        });
    }

    async loadAllData() {
        try {
            await Promise.all([
                this.loadPlatformSummary(),
                this.loadModelPerformance(),
                this.loadDatasetSummary(),
                this.loadPredictionStats(),
                this.loadFeatureImportance()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async apiCall(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API call failed for ${endpoint}:`, error);
            throw error;
        }
    }

    async loadPlatformSummary() {
        try {
            const data = await this.apiCall('/platform-summary');
            
            document.getElementById('production-model').textContent = data.production_model || 'None';
            document.getElementById('total-models').textContent = data.total_models || '0';
            document.getElementById('datasets-available').textContent = data.datasets_available || '0';
            document.getElementById('predictions-logged').textContent = data.predictions_logged || '0';
            
        } catch (error) {
            this.showError('platform-overview', 'Failed to load platform summary');
        }
    }

    async loadModelPerformance() {
        try {
            const data = await this.apiCall('/model-performance');
            
            if (data.message) {
                document.getElementById('model-list').innerHTML = `
                    <div class="error-state">${data.message}</div>
                `;
                return;
            }

            document.getElementById('best-model').textContent = data.best_model || 'None';
            document.getElementById('improvement').textContent = data.improvement_over_v1 || 'N/A';
            
            const modelList = document.getElementById('model-list');
            if (data.models && data.models.length > 0) {
                modelList.innerHTML = data.models.map(model => `
                    <div class="model-item">
                        <div class="model-name">${model.version} - ${model.model_name}</div>
                        <div class="model-details">
                            <div>Task: ${model.task_type}</div>
                            <div>Score: ${model.score.toFixed(4)}</div>
                            <div>Date: ${new Date(model.timestamp).toLocaleDateString()}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                modelList.innerHTML = '<div class="error-state">No models found</div>';
            }
            
        } catch (error) {
            this.showError('model-performance', 'Failed to load model performance');
        }
    }

    async loadDatasetSummary() {
        try {
            const data = await this.apiCall('/dataset-summary');
            
            document.getElementById('dataset-rows').textContent = data.rows || '0';
            document.getElementById('dataset-columns').textContent = data.columns || '0';
            
            // Calculate total missing values
            const totalMissing = data.missing_values ? 
                Object.values(data.missing_values).reduce((sum, val) => sum + val, 0) : 0;
            document.getElementById('missing-values').textContent = totalMissing;
            
            // Display column names
            const columnNamesDiv = document.getElementById('column-names');
            if (data.column_names && data.column_names.length > 0) {
                columnNamesDiv.innerHTML = data.column_names.map(name => 
                    `<span class="column-tag">${name}</span>`
                ).join('');
            } else {
                columnNamesDiv.innerHTML = '<span class="error-state">No columns found</span>';
            }
            
        } catch (error) {
            this.showError('dataset-insights', 'Failed to load dataset summary');
        }
    }

    async loadPredictionStats() {
        try {
            const data = await this.apiCall('/prediction-stats');
            
            if (data.message) {
                document.getElementById('prediction-analytics').innerHTML = `
                    <div class="error-state">${data.message}</div>
                `;
                return;
            }
            
            document.getElementById('analytics-total').textContent = data.total_predictions || '0';
            document.getElementById('analytics-last').textContent = 
                data.last_prediction ? new Date(data.last_prediction).toLocaleString() : 'None';
                
            // Display class distribution
            const distributionDiv = document.getElementById('class-distribution');
            if (data.class_distribution && Object.keys(data.class_distribution).length > 0) {
                const total = Object.values(data.class_distribution).reduce((sum, val) => sum + val, 0);
                
                distributionDiv.innerHTML = Object.entries(data.class_distribution).map(([className, count]) => {
                    const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
                    return `
                        <div class="class-bar">
                            <div class="class-label">Class ${className}</div>
                            <div class="class-count">${count} (${percentage}%)</div>
                        </div>
                    `;
                }).join('');
            } else {
                distributionDiv.innerHTML = '<div class="error-state">No predictions logged yet</div>';
            }
            
        } catch (error) {
            this.showError('prediction-analytics', 'Failed to load prediction analytics');
        }
    }

    async loadFeatureImportance() {
        try {
            const data = await this.apiCall('/feature-importance');
            
            const featureChart = document.getElementById('feature-chart');
            
            if (data.feature_importance) {
                const features = Object.entries(data.feature_importance);
                const maxImportance = Math.max(...Object.values(data.feature_importance));
                
                featureChart.innerHTML = features.map(([feature, importance]) => {
                    const percentage = maxImportance > 0 ? (importance / maxImportance) * 100 : 0;
                    return `
                        <div class="feature-bar">
                            <div class="feature-name">${feature}</div>
                            <div class="feature-bar-container">
                                <div class="feature-bar-fill" style="width: ${percentage}%"></div>
                            </div>
                            <div class="feature-value">${importance.toFixed(3)}</div>
                        </div>
                    `;
                }).join('');
            } else {
                featureChart.innerHTML = '<div class="error-state">Feature importance not available</div>';
            }
            
        } catch (error) {
            this.showError('feature-importance', 'Failed to load feature importance');
        }
    }

    async makePrediction() {
        const form = document.getElementById('prediction-form');
        const resultDiv = document.getElementById('prediction-result');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Disable form and show loading
        submitBtn.disabled = true;
        submitBtn.textContent = '🤔 Predicting...';
        resultDiv.innerHTML = '<div class="loading">Making prediction...</div>';
        resultDiv.className = 'result-display';
        
        try {
            const features = [
                parseFloat(document.getElementById('sepal-length').value),
                parseFloat(document.getElementById('sepal-width').value),
                parseFloat(document.getElementById('petal-length').value),
                parseFloat(document.getElementById('petal-width').value)
            ];
            
            // Validate inputs
            if (features.some(val => isNaN(val))) {
                throw new Error('Please enter valid numbers for all features');
            }
            
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ features: features })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Map prediction to class name
            const classNames = {
                0: 'Setosa',
                1: 'Versicolor', 
                2: 'Virginica'
            };
            
            const className = classNames[result.prediction] || `Class ${result.prediction}`;
            
            resultDiv.innerHTML = `
                <div>🎯 Prediction: <strong>${className}</strong> (${result.prediction})</div>
            `;
            resultDiv.className = 'result-display prediction-success';
            
            // Refresh prediction stats to show new prediction
            setTimeout(() => this.loadPredictionStats(), 1000);
            
        } catch (error) {
            resultDiv.innerHTML = `<div>❌ Error: ${error.message}</div>`;
            resultDiv.className = 'result-display prediction-error';
        } finally {
            // Re-enable form
            submitBtn.disabled = false;
            submitBtn.textContent = '🔮 Make Prediction';
        }
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="error-state">${message}</div>`;
        }
    }

    updateLastUpdatedTime() {
        const now = new Date();
        document.getElementById('last-updated').textContent = now.toLocaleString();
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new AutoMLDashboard();
});

// Add some sample data for demonstration if APIs fail
window.addEventListener('load', () => {
    // Add some visual enhancements
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.style.animation = 'fadeInUp 0.5s ease forwards';
    });
});

// CSS animation for cards
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .card {
        opacity: 0;
    }
`;
document.head.appendChild(style);