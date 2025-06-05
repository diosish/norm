document.addEventListener('DOMContentLoaded', function() {
    // Check for touch device support
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    // Check for dark theme preference
    const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Adapt for touch devices
    if (isTouchDevice) {
        document.body.classList.add('touch-device');
    }

    // Handle tooltips
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        if (isTouchDevice) {
            tooltip.addEventListener('click', function(e) {
                e.preventDefault();
                this.classList.toggle('tooltip-active');
            });
        }
    });

    // Check connection status for offline mode
    window.addEventListener('online', function() {
        document.body.classList.remove('offline-mode');

        // Enable submit buttons when back online
        const submitButtons = document.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            button.disabled = false;
        });
    });

    window.addEventListener('offline', function() {
        document.body.classList.add('offline-mode');
        alert('No internet connection. Some features may be unavailable.');

        // Disable submit buttons when offline
        const submitButtons = document.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            button.disabled = true;
        });
    });

    // Adapt for mobile devices
    function adjustForMobile() {
        if (window.innerWidth <= 480) {
            // Reduce animation size for very small screens
            const lottieContainers = document.querySelectorAll('lottie-player');
            lottieContainers.forEach(container => {
                container.style.width = '60px';
                container.style.height = '60px';
            });
        }
    }

    // Check screen size on load and resize
    adjustForMobile();
    window.addEventListener('resize', adjustForMobile);
});