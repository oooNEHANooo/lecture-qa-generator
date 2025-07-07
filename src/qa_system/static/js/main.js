// Main JavaScript for QA System

// Global utilities and common functions
const QASystem = {
    // API endpoints
    api: {
        lectures: '/api/lectures',
        questions: '/api/questions',
        analytics: '/api/analytics'
    },

    // Common HTTP methods
    async fetch(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Show notification
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto dismiss
        setTimeout(() => {
            if (notification.parentNode) {
                bootstrap.Alert.getOrCreateInstance(notification).close();
            }
        }, duration);
    },

    // Show loading overlay
    showLoading() {
        const overlay = document.createElement('div');
        overlay.className = 'spinner-overlay';
        overlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
                <div class="mt-2">読み込み中...</div>
            </div>
        `;
        overlay.id = 'loading-overlay';
        document.body.appendChild(overlay);
    },

    // Hide loading overlay
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    },

    // Format date for display
    formatDate(dateString, includeTime = false) {
        if (!dateString) return '不明';
        
        const date = new Date(dateString);
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        };
        
        if (includeTime) {
            options.hour = '2-digit';
            options.minute = '2-digit';
        }
        
        return date.toLocaleDateString('ja-JP', options);
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Debounce function for search inputs
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Validate form data
    validateForm(formElement) {
        const formData = new FormData(formElement);
        const errors = [];

        // Check required fields
        const requiredFields = formElement.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                errors.push(`${field.dataset.label || field.name}は必須項目です`);
            }
        });

        // Check file size for file inputs
        const fileInputs = formElement.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            if (input.files.length > 0) {
                const file = input.files[0];
                const maxSize = parseInt(input.dataset.maxSize) || 50 * 1024 * 1024; // 50MB default
                
                if (file.size > maxSize) {
                    errors.push(`ファイルサイズが上限（${this.formatFileSize(maxSize)}）を超えています`);
                }
            }
        });

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },

    // Copy text to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('クリップボードにコピーしました', 'success', 2000);
        } catch (error) {
            console.error('Clipboard copy failed:', error);
            this.showNotification('コピーに失敗しました', 'danger', 2000);
        }
    },

    // Initialize tooltips
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Initialize popovers
    initializePopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },

    // Chart utilities
    chart: {
        // Default color scheme
        colors: {
            primary: '#0d6efd',
            secondary: '#6c757d',
            success: '#198754',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#0dcaf0'
        },

        // Create pie chart
        createPieChart(elementId, data, title = '') {
            const layout = {
                title: title,
                font: { family: 'Segoe UI, sans-serif' },
                showlegend: true,
                margin: { t: 40, b: 40, l: 40, r: 40 }
            };

            const config = {
                responsive: true,
                displayModeBar: false
            };

            Plotly.newPlot(elementId, data, layout, config);
        },

        // Create bar chart
        createBarChart(elementId, data, title = '') {
            const layout = {
                title: title,
                font: { family: 'Segoe UI, sans-serif' },
                xaxis: { title: '' },
                yaxis: { title: '件数' },
                margin: { t: 40, b: 80, l: 60, r: 40 }
            };

            const config = {
                responsive: true,
                displayModeBar: false
            };

            Plotly.newPlot(elementId, data, layout, config);
        },

        // Create line chart
        createLineChart(elementId, data, title = '') {
            const layout = {
                title: title,
                font: { family: 'Segoe UI, sans-serif' },
                xaxis: { title: '時間' },
                yaxis: { title: '正答率 (%)' },
                margin: { t: 40, b: 80, l: 60, r: 40 }
            };

            const config = {
                responsive: true,
                displayModeBar: false
            };

            Plotly.newPlot(elementId, data, layout, config);
        }
    }
};

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    QASystem.initializeTooltips();
    QASystem.initializePopovers();

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Auto-refresh functionality for real-time data
    if (window.location.pathname.includes('analytics')) {
        setInterval(() => {
            if (typeof refreshAnalytics === 'function') {
                refreshAnalytics();
            }
        }, 30000); // Refresh every 30 seconds
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+R or F5 - Refresh current view
        if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
            e.preventDefault();
            if (typeof refreshCurrentView === 'function') {
                refreshCurrentView();
            } else {
                location.reload();
            }
        }

        // Escape - Close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                bootstrap.Modal.getInstance(modal)?.hide();
            });
        }
    });

    // Handle network errors globally
    window.addEventListener('online', function() {
        QASystem.showNotification('ネットワーク接続が復旧しました', 'success');
    });

    window.addEventListener('offline', function() {
        QASystem.showNotification('ネットワーク接続が切断されました', 'warning');
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const validation = QASystem.validateForm(this);
            if (!validation.isValid) {
                e.preventDefault();
                const errorMessage = validation.errors.join('<br>');
                QASystem.showNotification(errorMessage, 'danger');
            }
        });
    });

    // Auto-save form data to localStorage
    const formInputs = document.querySelectorAll('input[data-autosave], textarea[data-autosave]');
    formInputs.forEach(input => {
        // Load saved value
        const savedValue = localStorage.getItem(`autosave_${input.name}`);
        if (savedValue && !input.value) {
            input.value = savedValue;
        }

        // Save on input
        input.addEventListener('input', QASystem.debounce(function() {
            localStorage.setItem(`autosave_${input.name}`, input.value);
        }, 1000));
    });
});

// Export QASystem to global scope
window.QASystem = QASystem;