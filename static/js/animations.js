document.addEventListener('DOMContentLoaded', function() {
    // Animate blobs in header
    animateBlobs();
    
    // Setup any animation observers
    setupScrollAnimations();
});

/**
 * Animate background blobs in header
 */
function animateBlobs() {
    const blobs = document.querySelectorAll('.animated-background .blob');
    if (!blobs.length) return;
    
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Apply animation or static effect
    blobs.forEach((blob, index) => {
        if (prefersReducedMotion) {
            // Use static position for reduced motion
            blob.style.transform = `translate(${index * 10}px, ${index * 5}px)`;
        } else {
            // Float animation timing
            const duration = 15 + index * 5;
            const delay = index * 2;
            
            // Apply custom animation if not using CSS animation
            if (!blob.classList.contains('animated')) {
                blob.animate([
                    { transform: 'translate(0, 0) rotate(0deg)' },
                    { transform: `translate(${index * 30}px, ${index * 20}px) rotate(${index * 5}deg)` }
                ], {
                    duration: duration * 1000,
                    delay: delay * 1000,
                    iterations: Infinity,
                    direction: 'alternate',
                    easing: 'ease-in-out'
                });
            }
        }
    });
}

/**
 * Setup intersection observers for scroll animations
 */
function setupScrollAnimations() {
    // Check if intersection observer is supported
    if (!('IntersectionObserver' in window)) return;
    
    // Elements to animate on scroll
    const animateElements = [
        '.stat-item', 
        '.file-card',
        '.success-animation'
    ];
    
    // Collect all elements
    let elements = [];
    animateElements.forEach(selector => {
        elements = [...elements, ...document.querySelectorAll(selector)];
    });
    
    if (!elements.length) return;
    
    // Create observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    // Observe each element
    elements.forEach(element => {
        // Add base animation class and delay
        element.classList.add('scroll-animation');
        
        // Set delay based on position
        if (!element.style.animationDelay) {
            const delay = Array.from(element.parentNode.children).indexOf(element) * 0.1;
            element.style.animationDelay = `${delay}s`;
        }
        
        observer.observe(element);
    });
}

/**
 * Add ripple effect to buttons
 * @param {string} selector Button selector
 */
function addButtonRippleEffect(selector = '.btn') {
    const buttons = document.querySelectorAll(selector);
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}