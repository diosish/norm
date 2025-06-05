document.addEventListener('DOMContentLoaded', function() {
    // Initialize result page animations
    initResultAnimations();

    // Setup file download tracking
    setupDownloadTracking();

    // Handle back navigation
    setupBackNavigation();
});

/**
 * Initialize result page animations
 */
function initResultAnimations() {
    // Animate statistics items entrance
    const statItems = document.querySelectorAll('.stat-item');

    statItems.forEach((item, index) => {
        // Set sequential delay
        item.style.animationDelay = `${0.2 + (index * 0.2)}s`;
    });

    // Animate file cards entrance
    const fileCards = document.querySelectorAll('.file-card');

    fileCards.forEach((card, index) => {
        // Set sequential delay
        card.style.animationDelay = `${0.4 + (index * 0.1)}s`;
    });

    // Ensure success animation plays
    const successAnimation = document.querySelector('.success-animation lottie-player');
    if (successAnimation && !successAnimation.isPlaying) {
        successAnimation.play();
    }
}

/**
 * Setup download button tracking
 */
function setupDownloadTracking() {
    const downloadButtons = document.querySelectorAll('.file-card .btn');

    downloadButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Visual feedback when download starts
            const card = this.closest('.file-card');
            if (card) {
                card.classList.add('downloading');

                // Change button text temporarily
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';

                // Reset after a short delay
                setTimeout(() => {
                    card.classList.remove('downloading');
                    this.innerHTML = originalText;
                }, 1500);
            }
        });
    });

    // Highlight primary download button
    const mainDownloadBtn = document.querySelector('.download-file-btn');
    if (mainDownloadBtn) {
        mainDownloadBtn.classList.add('btn-pulse');
    }
}

/**
 * Setup back navigation handling
 */
function setupBackNavigation() {
    const backButton = document.querySelector('.btn-back');

    if (backButton) {
        backButton.addEventListener('click', function(e) {
            // Check if there are custom handling requirements
            // For example, warning about losing current results

            // If session needs to be preserved, we might add a confirmation
            const shouldConfirm = false; // Set to true if confirmation needed

            if (shouldConfirm) {
                e.preventDefault();
                if (confirm('Are you sure you want to return to the main page? Current results will remain available for 24 hours.')) {
                    window.location.href = this.getAttribute('href');
                }
            }
            // Otherwise, normal navigation occurs
        });
    }
}

/**
 * Handle file search functionality
 */
function setupFileSearch() {
    const searchInput = document.getElementById('file-search');
    const fileGrid = document.querySelector('.file-grid');

    if (!searchInput || !fileGrid) return;

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const fileCards = fileGrid.querySelectorAll('.file-card');

        fileCards.forEach(card => {
            const fileName = card.querySelector('.file-name').textContent.toLowerCase();

            if (fileName.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
}