document.addEventListener('DOMContentLoaded', function() {
    // Index page specific initialization
    initFormValidation();
});

/**
 * Initialize form validation
 */
function initFormValidation() {
    const form = document.getElementById('upload-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const phoneColumn = document.getElementById('phone_column');
        const typeColumn = document.getElementById('type_column');
        const fileInput = document.getElementById('file');
        let isValid = true;
        let errorMessage = '';

        // Check file selection
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            isValid = false;
            errorMessage += 'Please select an Excel file.\n';
        }

        // Check phone column
        if (!phoneColumn || !phoneColumn.value.trim()) {
            isValid = false;
            errorMessage += 'Please specify the phone numbers column.\n';
        }

        // Check type column
        if (!typeColumn || !typeColumn.value.trim()) {
            isValid = false;
            errorMessage += 'Please specify the participant type column.\n';
        }

        // Validate and prevent default if invalid
        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
        } else {
            // Show processing animation
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }

            // Add processing class
            form.classList.add('form-submitted');
        }
    });

    // Reset form state if needed
    if (window.location.search.includes('error') || window.location.search.includes('message')) {
        form.classList.remove('form-submitted');
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-cogs"></i> Process Database';
        }
    }
}

/**
 * Show file selection prompt
 */
function promptFileSelection() {
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.click();
    }
}