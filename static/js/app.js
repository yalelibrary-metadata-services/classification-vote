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

            // Check if user wants to vote on all identical notes
            const voteAllCheckbox = noteCard.querySelector('.vote-all-identical');
            const voteAll = voteAllCheckbox && voteAllCheckbox.checked;

            // Show loading spinner
            voteStatus.style.display = 'block';
            this.disabled = true;

            const endpoint = voteAll ? '/vote-identical' : '/vote';
            const requestBody = voteAll ?
                {
                    note_text: voteAllCheckbox.dataset.noteText,
                    classification: classification
                } :
                {
                    bib_id: BIB_ID,
                    note_index: parseInt(noteIndex),
                    classification: classification
                };

            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (voteAll) {
                        // Bulk vote success
                        showNotification(
                            `Vote applied to ${data.total_notes} identical notes! (${data.votes_created} new, ${data.votes_updated} updated)`,
                            'success'
                        );
                    } else {
                        // Single vote success
                        try {
                            // Update vote distribution display
                            updateVoteDisplay(noteCard, data.distribution, classification);

                            // Update who voted section
                            if (data.voters) {
                                updateVotersDisplay(noteCard, data.voters);
                            }

                            showNotification(
                                `Vote recorded! Consensus: ${data.consensus.toUpperCase()} at ${Math.round(data.consensus_probability * 100)}%`,
                                'success'
                            );
                        } catch (error) {
                            console.error('Error updating displays:', error);
                            showNotification('Vote saved, but error updating display: ' + error.message, 'warning');
                        }
                    }

                    // Update button highlighting
                    noteCard.querySelectorAll('.vote-btn').forEach(btn => {
                        const btnClass = btn.dataset.classification;
                        const colorClass = getColorForClassification(btnClass);

                        // Remove all color classes
                        btn.className = 'btn btn-sm vote-btn';

                        // Add appropriate class
                        if (btnClass === classification) {
                            btn.classList.add('btn-' + colorClass);
                        } else {
                            btn.classList.add('btn-outline-' + colorClass);
                        }
                    });
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

    // Toggle votes visibility
    document.querySelectorAll('.toggle-votes-btn').forEach(button => {
        button.addEventListener('click', function() {
            const noteCard = this.closest('.note-card');
            const voteDistribution = noteCard.querySelector('.vote-distribution');
            const votersSection = noteCard.querySelector('.voters-section');

            // Toggle visibility
            if (voteDistribution.style.display === 'none') {
                voteDistribution.style.display = 'block';
                votersSection.style.display = 'block';
                this.innerHTML = '<i class="fas fa-eye-slash"></i> Hide Other Votes';
            } else {
                voteDistribution.style.display = 'none';
                votersSection.style.display = 'none';
                this.innerHTML = '<i class="fas fa-eye"></i> Show Other Votes';
            }
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

// Helper function to update vote distribution display
function updateVoteDisplay(noteCard, distribution, userVote) {
    const voteDistDiv = noteCard.querySelector('.vote-distribution');

    if (distribution.total === 0) {
        voteDistDiv.innerHTML = '<small class="text-warning"><strong>No votes yet</strong> - be the first to classify!</small>';
        return;
    }

    // Build vote badges HTML
    let html = '<small class="text-muted"><strong>All Votes:</strong><br>';

    // Sort by count descending
    const sortedVotes = Object.entries(distribution.votes).sort((a, b) => b[1] - a[1]);

    for (const [classification, count] of sortedVotes) {
        const prob = distribution.probabilities[classification];
        const isConsensus = classification === distribution.consensus;
        const badgeClass = isConsensus ? 'success' : 'secondary';
        html += `<span class="badge bg-${badgeClass} me-1">${classification.toUpperCase()}: ${Math.round(prob * 100)}% (${count})</span>`;
    }

    html += '</small><br><small><strong>Consensus:</strong> ';
    html += `<span class="badge bg-primary">${distribution.consensus.toUpperCase()}</span> `;
    html += `at ${Math.round(distribution.consensus_probability * 100)}% confidence `;
    html += `(${distribution.total} vote${distribution.total !== 1 ? 's' : ''})`;

    if (distribution.is_contentious) {
        html += ' <span class="badge bg-warning text-dark">CONTENTIOUS</span>';
    }

    html += '</small>';

    if (userVote) {
        html += `<br><small class="text-info"><strong>Your vote:</strong> ${userVote.toUpperCase()}</small>`;
    }

    voteDistDiv.innerHTML = html;
}

// Helper function to update voters display
function updateVotersDisplay(noteCard, voters) {
    const votersSection = noteCard.querySelector('.voters-section');

    // Check if element exists
    if (!votersSection) {
        console.error('Voters section not found in note card');
        return;
    }

    if (!voters || Object.keys(voters).length === 0) {
        votersSection.innerHTML = `
            <h6 class="mb-2">Who Voted?</h6>
            <small class="text-muted">No votes yet</small>
        `;
        return;
    }

    try {
        // Build voters list HTML
        let html = '<h6 class="mb-2">Who Voted?</h6><div class="voters-list">';

        // Sort classifications for consistent display
        const sortedClassifications = Object.keys(voters).sort();

        for (const classification of sortedClassifications) {
            const users = voters[classification];
            html += '<div class="mb-2">';
            html += '<span class="badge bg-primary">' + classification.toUpperCase() + '</span>';
            html += '<div class="mt-1">';

            for (const username of users) {
                html += '<small class="badge bg-secondary me-1">' + username + '</small>';
            }

            html += '</div></div>';
        }

        html += '</div>';
        votersSection.innerHTML = html;
    } catch (error) {
        console.error('Error updating voters display:', error);
    }
}

// Helper function to get Bootstrap color class for classification
function getColorForClassification(classification) {
    const colors = {
        'w': 'info',
        'o': 'warning',
        'a': 'success',
        'ow': 'secondary',
        'aw': 'dark',
        'ao': 'primary',
        '?': 'danger'
    };
    return colors[classification] || 'secondary';
}
