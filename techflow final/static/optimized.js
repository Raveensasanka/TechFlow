// Enhanced JavaScript functionality for TechFlow Issue Tracking System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFileUploads();
    initializeFormValidation();
    initializeDashboardFeatures();
    initializeImageModals();
    initializeNotifications();
});

// File Upload Management
function initializeFileUploads() {
    const fileInput = document.getElementById('image_upload');
    if (!fileInput) return;

    let uploadedFiles = [];

    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        
        // Validate file count
        if (files.length > 10) {
            showNotification('❌ Too Many Files', 'Please select maximum 10 images', 'error');
            return;
        }
        
        // Validate file sizes
        const oversizedFiles = files.filter(file => file.size > 5 * 1024 * 1024);
        if (oversizedFiles.length > 0) {
            showNotification('❌ File Too Large', 'Please select images smaller than 5MB each', 'error');
            return;
        }
        
        // Replace uploaded files (don't accumulate)
        uploadedFiles = files.slice(0, 10);
        updateFileDisplay();
    });

    function updateFileDisplay() {
        const uploadedFilesDiv = document.getElementById('uploadedFiles');
        const filesList = document.getElementById('filesList');
        const filesCount = document.querySelector('.files-count');
        
        if (uploadedFiles.length > 0) {
            uploadedFilesDiv.style.display = 'block';
            filesCount.textContent = `${uploadedFiles.length}/10 images uploaded`;
            
            filesList.innerHTML = '';
            uploadedFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="file-info">
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                    <button type="button" class="remove-file-btn" onclick="removeFile(${index})">×</button>
                `;
                filesList.appendChild(fileItem);
            });
        } else {
            uploadedFilesDiv.style.display = 'none';
        }
    }

    window.removeFile = function(index) {
        uploadedFiles.splice(index, 1);
        updateFileDisplay();
    };

    window.clearAllFiles = function() {
        uploadedFiles = [];
        document.getElementById('image_upload').value = '';
        updateFileDisplay();
    };
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailField = form.querySelector('input[type="email"]');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            showFieldError(emailField, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Phone validation
    const phoneField = form.querySelector('input[type="tel"]');
    if (phoneField && phoneField.value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(phoneField.value.replace(/[\s\-\(\)]/g, ''))) {
            showFieldError(phoneField, 'Please enter a valid phone number');
            isValid = false;
        }
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.style.borderColor = '#dc3545';
    field.style.boxShadow = '0 0 0 4px rgba(220, 53, 69, 0.1)';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.style.borderColor = '';
    field.style.boxShadow = '';
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Dashboard Features
function initializeDashboardFeatures() {
    // Filter functionality
    const statusFilter = document.getElementById('statusFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const techLevelFilter = document.getElementById('techLevelFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    if (priorityFilter) priorityFilter.addEventListener('change', applyFilters);
    if (techLevelFilter) techLevelFilter.addEventListener('change', applyFilters);
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    
    // Clear filters
    const clearFiltersBtn = document.getElementById('clearFilters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearAllFilters);
    }
    
    // Action buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-action]')) {
            handleActionClick(e);
        }
    });
    
    // Export functionality
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportToExcel);
    }
    
    // Print functionality
    const printBtn = document.getElementById('printBtn');
    if (printBtn) {
        printBtn.addEventListener('click', printData);
    }
    
    // Refresh functionality
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            location.reload();
        });
    }
    
    // Reset functionality
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetAllData);
    }
}

let allIssues = [];
let filteredIssues = [];

function loadIssues() {
    const issueCards = document.querySelectorAll('.issue-card');
    allIssues = Array.from(issueCards);
    filteredIssues = [...allIssues];
    updateDashboardStats();
    showIssues(filteredIssues);
}

function updateDashboardStats() {
    const totalIssues = allIssues.length;
    const pendingIssues = allIssues.filter(issue => 
        issue.dataset.status === 'Pending'
    ).length;
    const inProgressIssues = allIssues.filter(issue => 
        issue.dataset.status === 'In Progress'
    ).length;
    const completedIssues = allIssues.filter(issue => 
        issue.dataset.status === 'Completed'
    ).length;
    
    const totalElement = document.getElementById('totalIssues');
    const pendingElement = document.getElementById('pendingIssues');
    const inProgressElement = document.getElementById('inProgressIssues');
    const completedElement = document.getElementById('completedIssues');
    
    if (totalElement) totalElement.textContent = totalIssues;
    if (pendingElement) pendingElement.textContent = pendingIssues;
    if (inProgressElement) inProgressElement.textContent = inProgressIssues;
    if (completedElement) completedElement.textContent = completedIssues;
}

function applyFilters() {
    const statusFilter = document.getElementById('statusFilter')?.value;
    const priorityFilter = document.getElementById('priorityFilter')?.value;
    const techLevelFilter = document.getElementById('techLevelFilter')?.value;
    const searchInput = document.getElementById('searchInput')?.value.toLowerCase();
    
    filteredIssues = allIssues.filter(issueCard => {
        const statusMatch = !statusFilter || issueCard.dataset.status === statusFilter;
        const priorityMatch = !priorityFilter || issueCard.dataset.priority === priorityFilter;
        const techLevelMatch = !techLevelFilter || issueCard.dataset.techLevel === techLevelFilter;
        
        let searchMatch = true;
        if (searchInput) {
            const issueText = issueCard.textContent.toLowerCase();
            searchMatch = issueText.includes(searchInput);
        }
        
        return statusMatch && priorityMatch && techLevelMatch && searchMatch;
    });
    
    showIssues(filteredIssues);
}

function clearAllFilters() {
    const statusFilter = document.getElementById('statusFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const techLevelFilter = document.getElementById('techLevelFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (statusFilter) statusFilter.value = '';
    if (priorityFilter) priorityFilter.value = '';
    if (techLevelFilter) techLevelFilter.value = '';
    if (searchInput) searchInput.value = '';
    
    applyFilters();
}

function showIssues(issues) {
    // Hide all issues first
    allIssues.forEach(issue => {
        issue.style.display = 'none';
    });
    
    // Show filtered issues
    issues.forEach(issue => {
        issue.style.display = 'block';
    });
    
    // Update the issues container to show count
    const container = document.querySelector('.issues-container');
    const countInfo = document.getElementById('filter-count') || document.createElement('div');
    countInfo.id = 'filter-count';
    countInfo.innerHTML = `<p class="filter-info">Showing ${issues.length} of ${allIssues.length} issues</p>`;
    
    if (!document.getElementById('filter-count')) {
        container.insertBefore(countInfo, container.firstChild);
    } else {
        document.getElementById('filter-count').innerHTML = `<p class="filter-info">Showing ${issues.length} of ${allIssues.length} issues</p>`;
    }
}

function handleActionClick(e) {
    const action = e.target.getAttribute('data-action');
    const issueId = parseInt(e.target.getAttribute('data-issue-id'));
    
    switch(action) {
        case 'setPriority':
            setPriority(issueId);
            break;
        case 'setTechLevel':
            setTechLevel(issueId);
            break;
        case 'startIssue':
            startIssue(issueId);
            break;
        case 'completeIssue':
            completeIssue(issueId);
            break;
        case 'viewHistory':
            viewHistory(issueId);
            break;
    }
}

// Action Functions
function setPriority(issueId) {
    Swal.fire({
        title: 'Set Priority',
        input: 'select',
        inputOptions: {
            'High': 'High',
            'Medium': 'Medium',
            'Low': 'Low'
        },
        inputPlaceholder: 'Select Priority',
        showCancelButton: true,
        confirmButtonText: 'Set Priority',
        preConfirm: (priority) => {
            if (!priority) {
                Swal.showValidationMessage('Please select a priority');
            }
            return priority;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            updateIssue(issueId, 'priority', { priority: result.value, performed_by: 'Technical Team' });
        }
    });
}

function setTechLevel(issueId) {
    Swal.fire({
        title: 'Set Tech Level',
        input: 'select',
        inputOptions: {
            'L1': 'L1 - CE',
            'L2': 'L2 - Skidata/TKH',
            'L3': 'L3 - Skidata/TKH'
        },
        inputPlaceholder: 'Select Tech Level',
        showCancelButton: true,
        confirmButtonText: 'Set Tech Level',
        preConfirm: (techLevel) => {
            if (!techLevel) {
                Swal.showValidationMessage('Please select a tech level');
            }
            return techLevel;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            updateIssue(issueId, 'tech_level', { tech_level: result.value, performed_by: 'Technical Team' });
        }
    });
}

function startIssue(issueId) {
    Swal.fire({
        title: 'Start Work',
        text: 'Are you sure you want to start working on this issue?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, start work!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            updateIssue(issueId, 'start', { performed_by: 'Technical Team' });
        }
    });
}

function completeIssue(issueId) {
    Swal.fire({
        title: 'Complete Issue',
        input: 'textarea',
        inputLabel: 'Resolution Notes',
        inputPlaceholder: 'Enter resolution details...',
        inputAttributes: {
            'aria-label': 'Enter resolution details'
        },
        showCancelButton: true,
        confirmButtonText: 'Mark as Complete',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            updateIssue(issueId, 'complete', { 
                resolution_notes: result.value || 'Issue resolved successfully', 
                performed_by: 'Technical Team' 
            });
        }
    });
}

function viewHistory(issueId) {
    fetch(`/api/issues/${issueId}/history`)
        .then(response => response.json())
        .then(history => {
            if (history.length === 0) {
                Swal.fire('No History', 'No history found for this issue', 'info');
                return;
            }
            
            let historyHtml = '<div class="history-timeline">';
            history.forEach(entry => {
                const timestamp = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'N/A';
                historyHtml += `
                    <div class="history-item">
                        <div class="history-time">${timestamp}</div>
                        <div class="history-action">${entry.action}</div>
                        <div class="history-description">${entry.description}</div>
                        <div class="history-performed">Performed by: ${entry.performed_by}</div>
                    </div>
                `;
            });
            historyHtml += '</div>';
            
            Swal.fire({
                title: 'Issue History',
                html: historyHtml,
                icon: 'info',
                confirmButtonText: 'OK',
                width: '600px'
            });
        })
        .catch(error => {
            Swal.fire('Error', 'Failed to load history', 'error');
        });
}

function updateIssue(issueId, action, data) {
    const endpoints = {
        'priority': `/api/issues/${issueId}/priority`,
        'tech_level': `/api/issues/${issueId}/tech_level`,
        'start': `/api/issues/${issueId}/start`,
        'complete': `/api/issues/${issueId}/complete`
    };
    
    const endpoint = endpoints[action];
    if (!endpoint) return;
    
    fetch(endpoint, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('Success!', 'Update completed successfully', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification('Error', result.error || 'Failed to update', 'error');
        }
    })
    .catch(error => {
        showNotification('Error', 'Failed to update issue', 'error');
    });
}

// Export and Utility Functions
function exportToExcel() {
    fetch('/api/export')
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Export failed');
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `issue_export_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Export Successful!', 'Excel file has been downloaded', 'success');
        })
        .catch(error => {
            showNotification('Error', 'Failed to export data', 'error');
        });
}

function printData() {
    fetch('/api/print')
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showNotification('Data Printed!', `Printed ${result.total_issues} issues to console`, 'success');
            } else {
                throw new Error(result.error);
            }
        })
        .catch(error => {
            showNotification('Error', 'Failed to print data', 'error');
        });
}

function resetAllData() {
    Swal.fire({
        title: 'Are you sure?',
        text: 'This will delete ALL data permanently!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, reset all data!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/reset', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Reset!', 'All data has been reset.', 'success');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showNotification('Error', data.error, 'error');
                    }
                })
                .catch(error => {
                    showNotification('Error', 'Failed to reset data', 'error');
                });
        }
    });
}

// Image Modal Functions
function initializeImageModals() {
    // Global image modal functions
    window.showImages = function(imageFilenames, reportId) {
        if (!imageFilenames || imageFilenames.trim() === '') {
            Swal.fire({
                title: 'No Images',
                text: 'No images attached to this issue',
                icon: 'info',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        const images = imageFilenames.split(',').map(filename => filename.trim()).filter(filename => filename !== '');
        
        if (images.length === 0) {
            Swal.fire({
                title: 'No Images',
                text: 'No valid images found for this issue',
                icon: 'info',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        let imagesHtml = '<div class="images-gallery">';
        
        images.forEach((filename, index) => {
            const encodedFilename = encodeURIComponent(filename);
            const imageUrl = `/static/uploads/${encodedFilename}`;
            
            imagesHtml += `
                <div class="image-item" style="text-align: center; margin: 10px; padding: 10px; border: 1px solid #dee2e6; border-radius: 8px; background: #f8f9fa;">
                    <img src="${imageUrl}" alt="Issue Image ${index + 1}" 
                         loading="lazy"
                         style="width: 120px; height: 120px; object-fit: cover; border-radius: 4px; border: 1px solid #dee2e6; cursor: pointer; background: #f8f9fa; opacity: 0; transition: opacity 0.3s;" 
                         onclick="openImageModal('${imageUrl}')" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                         onload="this.style.opacity='1';">
                    <div class="image-error" style="display: none; padding: 1rem; text-align: center; color: #dc3545;">
                        ❌ Image not found: ${filename}
                    </div>
                    <div class="image-info" style="margin-top: 8px;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">${filename}</div>
                        <a href="${imageUrl}" download="${filename}" 
                           style="display: inline-block; padding: 5px 10px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; font-size: 12px;">
                            📥 Download
                        </a>
                    </div>
                </div>
            `;
        });
        
        imagesHtml += '</div>';
        
        Swal.fire({
            title: `Images for Issue ${reportId}`,
            html: imagesHtml,
            width: '80%',
            showConfirmButton: true,
            confirmButtonText: 'Close',
            customClass: {
                popup: 'images-popup'
            }
        });
    };

    window.openImageModal = function(imageUrl) {
        Swal.fire({
            imageUrl: imageUrl,
            imageAlt: 'Issue Image',
            showConfirmButton: false,
            showCloseButton: true,
            width: 'auto',
            padding: '2rem',
            background: '#000',
            customClass: {
                popup: 'image-modal-popup',
                image: 'image-modal-image'
            }
        });
    };
}

// Notification System
function initializeNotifications() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

function showNotification(title, text, type = 'info') {
    // Use SweetAlert2 for notifications
    const icons = {
        'success': 'success',
        'error': 'error',
        'warning': 'warning',
        'info': 'info'
    };
    
    Swal.fire({
        title: title,
        text: text,
        icon: icons[type] || 'info',
        timer: type === 'error' ? 0 : 3000,
        timerProgressBar: true,
        showConfirmButton: type === 'error'
    });
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load issues for dashboard
    if (document.querySelector('.dashboard')) {
        loadIssues();
    }
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.type === 'submit' || this.getAttribute('data-action')) {
                this.style.opacity = '0.7';
                this.style.pointerEvents = 'none';
                
                setTimeout(() => {
                    this.style.opacity = '';
                    this.style.pointerEvents = '';
                }, 2000);
            }
        });
    });
});

// Enhanced form submission for issue creation
document.addEventListener('DOMContentLoaded', function() {
    const issueForm = document.getElementById('issueForm');
    if (issueForm) {
        issueForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!validateForm(this)) {
                return;
            }
            
            const formData = new FormData(this);
            
            // Prepare data for API
            const data = new FormData();
            data.append('name', formData.get('name'));
            data.append('phone', formData.get('phone'));
            data.append('email', formData.get('email'));
            data.append('project', formData.get('project'));
            data.append('description', formData.get('description'));
            
            // Add images if selected
            const uploadedFiles = window.uploadedFiles || [];
            uploadedFiles.forEach((file, index) => {
                data.append(`image_${index}`, file);
            });
            
            // Add loading state to form
            this.classList.add('form-loading');
            
            // Show loading
            Swal.fire({
                title: 'Submitting Issue...',
                text: 'Please wait while we process your request',
                allowOutsideClick: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            try {
                const response = await fetch('/api/issues', {
                    method: 'POST',
                    body: data
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.classList.remove('form-loading');
                    this.classList.add('success-animation');
                    
                    Swal.fire({
                        title: '🎉 Issue Reported Successfully!',
                        text: `Your issue has been reported with ID: ${result.report_id}`,
                        icon: 'success',
                        confirmButtonText: 'Great!',
                        confirmButtonColor: '#667eea'
                    }).then(() => {
                        this.reset();
                        this.classList.remove('success-animation');
                        // Clear uploaded files
                        if (window.clearAllFiles) {
                            window.clearAllFiles();
                        }
                    });
                } else {
                    this.classList.remove('form-loading');
                    Swal.fire({
                        title: '❌ Error',
                        text: result.error || 'Failed to submit issue',
                        icon: 'error',
                        confirmButtonText: 'Try Again',
                        confirmButtonColor: '#dc3545'
                    });
                }
            } catch (error) {
                this.classList.remove('form-loading');
                Swal.fire({
                    title: '❌ Connection Error',
                    text: 'Failed to submit issue. Please check your connection and try again.',
                    icon: 'error',
                    confirmButtonText: 'Retry',
                    confirmButtonColor: '#dc3545'
                });
            }
        });
    }
});
