document.addEventListener('DOMContentLoaded', function() {
    const previewBtn = document.getElementById('preview-btn');
    const loading = document.getElementById('loading');
    const columnsContainer = document.getElementById('columns-container');
    const columnList = document.getElementById('column-list');
    const phoneColumnInput = document.getElementById('phone_column');
    const typeColumnInput = document.getElementById('type_column');
    const sortColumnInput = document.getElementById('sort_column');
    const fileInput = document.getElementById('file');

    // Preview columns button handler
    if (previewBtn && fileInput) {
        previewBtn.addEventListener('click', function() {
            const file = fileInput.files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }

            // Remove pulse animation from button
            previewBtn.classList.remove('btn-pulse');
            previewBtn.disabled = true;
            previewBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

            // Show loading indicator
            if (loading) {
                loading.style.display = 'block';
            }
            if (columnsContainer) {
                columnsContainer.style.display = 'none';
            }

            // Create FormData object and add file
            const formData = new FormData();
            formData.append('file', file);

            // Send request to server
            fetch('/preview', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (loading) {
                    loading.style.display = 'none';
                }
                previewBtn.disabled = false;
                previewBtn.innerHTML = '<i class="fas fa-list"></i> Preview Columns';

                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }

                // Show columns container
                if (columnsContainer) {
                    columnsContainer.style.display = 'block';
                }

                // Clear list
                if (columnList) {
                    columnList.innerHTML = '';

                    // Populate column list
                    data.columns.forEach(column => {
                        const columnItem = document.createElement('div');
                        columnItem.className = 'column-item';
                        columnItem.innerHTML = `<strong>${column.index}</strong> ${column.name}`;

                        // Add click handler for item
                        columnItem.addEventListener('click', function() {
                            // Get last selected input and deselect all items
                            const allItems = document.querySelectorAll('.column-item');
                            allItems.forEach(item => item.classList.remove('active'));

                            // Highlight current item
                            columnItem.classList.add('active');

                            // Get active element
                            const activeInput = document.activeElement;

                            // Set value to appropriate input
                            if (activeInput === phoneColumnInput ||
                                activeInput === typeColumnInput ||
                                activeInput === sortColumnInput) {
                                activeInput.value = column.index;

                                // Add animation for selected field
                                addInputAnimation(activeInput);
                            } else {
                                // If no active field, select default field
                                if (phoneColumnInput && !phoneColumnInput.value) {
                                    phoneColumnInput.value = column.index;
                                    addInputAnimation(phoneColumnInput);
                                } else if (typeColumnInput && !typeColumnInput.value) {
                                    typeColumnInput.value = column.index;
                                    addInputAnimation(typeColumnInput);
                                } else if (sortColumnInput && !sortColumnInput.value) {
                                    sortColumnInput.value = column.index;
                                    addInputAnimation(sortColumnInput);
                                } else {
                                    // If all fields are filled, update first one
                                    if (phoneColumnInput) {
                                        phoneColumnInput.value = column.index;
                                        addInputAnimation(phoneColumnInput);
                                    }
                                }
                            }
                        });

                        columnList.appendChild(columnItem);
                    });

                    // Help message if many columns
                    if (data.columns.length > 10) {
                        const infoAlert = document.createElement('div');
                        infoAlert.className = 'alert alert-info';
                        infoAlert.innerHTML = '<i class="fas fa-info-circle"></i><span>Your table has many columns. Use browser search (Ctrl+F) to quickly find the column you need.</span>';
                        columnList.parentNode.insertBefore(infoAlert, columnList);
                    }
                }
            })
            .catch(error => {
                if (loading) {
                    loading.style.display = 'none';
                }
                previewBtn.disabled = false;
                previewBtn.innerHTML = '<i class="fas fa-list"></i> Preview Columns';
                alert('An error occurred: ' + error.message);
            });
        });
    }

    // Input field animation
    function addInputAnimation(input) {
        input.style.transition = 'background-color 0.3s ease';
        input.style.backgroundColor = 'rgba(67, 97, 238, 0.1)';
        setTimeout(() => {
            input.style.backgroundColor = '';
        }, 500);
    }

    // Add focus handlers for input fields
    [phoneColumnInput, typeColumnInput, sortColumnInput].forEach(input => {
        if (input) {
            input.addEventListener('focus', function() {
                // If column list is open, add hint
                if (columnsContainer && columnsContainer.style.display === 'block') {
                    const columnItems = document.querySelectorAll('.column-item');
                    columnItems.forEach(item => {
                        item.style.transition = 'transform 0.3s ease';
                        item.style.transform = 'translateX(5px)';
                        setTimeout(() => {
                            item.style.transform = 'translateX(0)';
                        }, 300);
                    });
                } else if (fileInput && fileInput.files.length > 0) {
                    // If file is selected but columns not viewed
                    if (previewBtn) {
                        previewBtn.classList.add('btn-pulse');
                    }
                }
            });
        }
    });
});