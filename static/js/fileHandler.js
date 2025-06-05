document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const fileDropArea = document.getElementById('file-drop-area');
    const fileInputText = document.getElementById('file-input-text');
    const fileName = document.getElementById('file-name');
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    // Handle file selection
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            handleFileSelection(fileInput.files);
        });
    }

    function handleFileSelection(files) {
        if (files.length > 0) {
            const file = files[0];
            const extension = file.name.split('.').pop().toLowerCase();

            if (['xlsx', 'xls'].includes(extension)) {
                fileInputText.style.display = 'none';
                fileName.textContent = file.name;
                fileName.style.display = 'block';
                fileDropArea.classList.add('has-file');

                // Change animation to success
                document.getElementById('upload-animation').innerHTML =
                    '<lottie-player src="/static/lottie/success.json" background="transparent" speed="1" style="width: 100%; height: 100%;" autoplay></lottie-player>';

                // Add pulse animation to preview button
                const previewBtn = document.getElementById('preview-btn');
                if (previewBtn) {
                    previewBtn.classList.add('btn-pulse');
                }

                // Check file size
                if (file.size > 5000000) { // 5MB
                    alert('Warning: File size is larger than 5MB. Processing may take longer.');
                }
            } else {
                // Invalid file type
                alert('Please upload an Excel file (.xlsx or .xls)');
                fileInput.value = ''; // Clear the input
            }
        } else {
            fileInputText.style.display = 'block';
            fileName.style.display = 'none';
            fileDropArea.classList.remove('has-file');

            // Reset to initial animation
            document.getElementById('upload-animation').innerHTML =
                '<lottie-player src="/static/lottie/upload.json" background="transparent" speed="1" style="width: 100%; height: 100%;" loop autoplay></lottie-player>';

            const previewBtn = document.getElementById('preview-btn');
            if (previewBtn) {
                previewBtn.classList.remove('btn-pulse');
            }
        }
    }

    // Drag & Drop functionality (only for non-touch devices)
    if (!isTouchDevice && fileDropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileDropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            fileDropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            fileDropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            fileDropArea.classList.add('highlight');
        }

        function unhighlight() {
            fileDropArea.classList.remove('highlight');
        }

        fileDropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            // Check for valid file extension
            if (files.length > 0) {
                const file = files[0];
                const extension = file.name.split('.').pop().toLowerCase();
                if (['xlsx', 'xls'].includes(extension)) {
                    fileInput.files = files;
                    handleFileSelection(files);
                } else {
                    alert('Please upload an Excel file (.xlsx or .xls)');
                }
            }
        }
    }

    // Prevent accidental page close with data entered
    const form = document.getElementById('upload-form');
    if (form) {
        window.addEventListener('beforeunload', function(e) {
            if (fileInput && fileInput.files.length > 0) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Animation on form submit
        form.addEventListener('submit', function(e) {
            const phoneColumnInput = document.getElementById('phone_column');
            const typeColumnInput = document.getElementById('type_column');

            // Check required fields
            if (phoneColumnInput && !phoneColumnInput.value) {
                e.preventDefault();
                alert('Please specify the phone numbers column');
                return;
            }

            if (typeColumnInput && !typeColumnInput.value) {
                e.preventDefault();
                alert('Please specify the participant type column');
                return;
            }

            if (fileInput && !fileInput.files.length) {
                e.preventDefault();
                alert('Please select a file');
                return;
            }

            form.classList.add('form-submitted');
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    }
});