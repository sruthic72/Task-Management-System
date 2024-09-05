// js/tasks.js
document.addEventListener('DOMContentLoaded', function() {
    const editButtons = document.querySelectorAll('.btn-success');
    const deleteButtons = document.querySelectorAll('.btn-danger');

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Edit functionality to be implemented.');
        });
    });

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this task?')) {
                // Code to delete the task
                alert('Task deleted successfully.'); // Placeholder
            }
        });
    });
});
