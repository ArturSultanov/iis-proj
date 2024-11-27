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
        let status = '';

        if (target.classList.contains('accept-button')) {
            status = 'accepted';
        } else if (target.classList.contains('reject-button')) {
            status = 'rejected';
        } else if (target.classList.contains('start-button')) {
            status = 'started';
        } else if (target.classList.contains('finish-button')) {
            status = 'finished';
        } else if (target.classList.contains('cancel-button')) {
            status = 'cancelled';
        }

        if (status) {
            fetch(`/staff/walk_requests/${walkId}/status?status=${status}`, {
                method: 'PATCH'
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
                console.error(`Error walk request:`, error);
                alert('An error occurred.');
            });
        }
    }
});

