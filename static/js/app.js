// Classification voting functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle classification votes
    document.querySelectorAll('.vote-btn').forEach(button => {
        button.addEventListener('click', function() {
            const noteCard = this.closest('.note-card');
            const noteIndex = noteCard.dataset.noteIndex;
            const classification = this.dataset.classification;
            const voteStatus = noteCard.querySelector('.vote-status');
            const currentType = noteCard.querySelector('.current-type');
            
            // Show loading spinner
            voteStatus.style.display = 'block';
            this.disabled = true;
            
            fetch('/vote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bib_id: BIB_ID,
                    note_index: parseInt(noteIndex),
                    classification: classification
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentType.textContent = data.new_type || 'unclassified';
                    showNotification('Classification saved successfully!', 'success');
                } else {
                    showNotification('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Network error occurred', 'error');
            })
            .finally(() => {
                voteStatus.style.display = 'none';
                this.disabled = false;
            });
        });
    });

    // Handle review submissions
    document.querySelectorAll('.review-btn').forEach(button => {
        button.addEventListener('click', function() {
            const noteCard = this.closest('.note-card');
            const noteIndex = noteCard.dataset.noteIndex;
            const review = this.dataset.review;
            const initialsInput = noteCard.querySelector('.reviewer-initials');
            const reviewStatus = noteCard.querySelector('.review-status');
            const reviewLoading = noteCard.querySelector('.review-loading');
            
            const initials = initialsInput.value.trim();
            if (!initials) {
                showNotification('Please enter reviewer initials', 'error');
                initialsInput.focus();
                return;
            }
            
            // Show loading spinner
            reviewLoading.style.display = 'block';
            this.disabled = true;
            
            fetch('/review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bib_id: BIB_ID,
                    note_index: parseInt(noteIndex),
                    reviewer: initials,
                    review: review
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the review status display
                    let statusText = `<strong>${data.reviewer}:</strong> `;
                    if (data.review === 'y') {
                        statusText += '<span class="text-success">Approved</span>';
                    } else if (data.review === 'n') {
                        statusText += '<span class="text-danger">Not Approved</span>';
                    } else {
                        statusText += '<span class="text-warning">Unknown</span>';
                    }
                    reviewStatus.innerHTML = '<small class="text-muted">' + statusText + '</small>';
                    showNotification('Review saved successfully!', 'success');
                } else {
                    showNotification('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Network error occurred', 'error');
            })
            .finally(() => {
                reviewLoading.style.display = 'none';
                this.disabled = false;
            });
        });
    });

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return; // Don't interfere with form inputs
        }
        
        if (e.key === 'ArrowLeft') {
            const prevButton = document.querySelector('a[href*="record/"][href*="Previous"]');
            if (prevButton && !prevButton.disabled) {
                window.location.href = prevButton.href;
            }
        } else if (e.key === 'ArrowRight') {
            const nextButton = document.querySelector('a[href*="record/"][href*="Next"]');
            if (nextButton && !nextButton.disabled) {
                window.location.href = nextButton.href;
            }
        }
    });
});

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification-toast alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}
                