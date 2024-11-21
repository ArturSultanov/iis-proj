document.getElementById('status').addEventListener('change', function () {
    const selectedStatus = this.value;
    const rows = document.querySelectorAll('.vet-request-row');

    rows.forEach(row => {
        const status = row.getAttribute('data-status');
        if (selectedStatus === "" || status === selectedStatus) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

window.addEventListener('message', function(event) {
    if (event.data.action === 'updateStatus') {
        const requestId = event.data.requestId;
        const newStatus = event.data.status;

        const row = document.querySelector(`.vet-request-row[data-id="${requestId}"]`);
        if (row) {
            row.querySelector('td:nth-child(5)').innerText = newStatus;
            row.setAttribute('data-status', newStatus);
        }
    }
});