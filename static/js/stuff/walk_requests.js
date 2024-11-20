// static/js/walk_requests.js

document.addEventListener('DOMContentLoaded', () => {
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const selectedStatus = this.value;
            const url = new URL(window.location.href);
            if (selectedStatus) {
                url.searchParams.set('status_filter', selectedStatus);
            } else {
                url.searchParams.delete('status_filter');
            }
            window.location.href = url.toString();
        });
    }
});

// Handle Accept, Reject, Finish, and Cancel buttons
document.addEventListener('click', function(event) {
    const target = event.target;

    if (target.classList.contains('action-button')) {
        const walkId = target.dataset.walkId;
        let action = '';

        if (target.classList.contains('accept-button')) {
            action = 'accept';
        } else if (target.classList.contains('reject-button')) {
            action = 'reject';
        } else if (target.classList.contains('start-button')) {
            action = 'start';
        } else if (target.classList.contains('finish-button')) {
            action = 'finish';
        } else if (target.classList.contains('cancel-button')) {
            action = 'cancel';
        }

        if (action) {
            const confirmAction = confirm(`Are you sure you want to ${action} this walk request?`);

            if (confirmAction) {
                fetch(`/staff/walk_requests/${walkId}/${action}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        response.json().then(data => {
                            alert(`Error: ${data.detail}`);
                        });
                    }
                })
                .catch(error => {
                    console.error(`Error ${action}ing walk request:`, error);
                    alert('An error occurred.');
                });
            }
        }
    }
});

