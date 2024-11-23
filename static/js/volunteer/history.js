const statusDiv = document.getElementById('response-status');


document.addEventListener('click', function(event) {
    if (event.target.classList.contains('cancel-button') && !event.target.disabled) {
        const walkId = event.target.dataset.walkId;
        fetch(`/volunteer/walks/${walkId}/cancel`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                statusDiv.innerHTML = 'Walk canceled successfully.';
                // timeout to allow user to see success message
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                response.json().then(data => {
                    statusDiv.innerHTML = `Error: ${data.detail}`;
                });
            }
        })
        .catch(error => {
            console.error(`Error canceling walk:`, error);
            statusDiv.innerHTML = 'An error occurred.';
        });
    }
});