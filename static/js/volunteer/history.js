document.addEventListener('click', function(event) {
    if (event.target.classList.contains('cancel-button') && !event.target.disabled) {
        const walkId = event.target.dataset.walkId;
        fetch(`/volunteer/walks/${walkId}/cancel`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                // todo make div for status
                // alert('Walk canceled successfully.');
                window.location.reload();
            } else {
                response.json().then(data => {
                    // todo make div for status
                    // alert(`Error: ${data.detail}`);
                });
            }
        })
        .catch(error => {
            // todo make div for status
            // console.error('Error canceling walk:', error);
            // alert('An error occurred while canceling the walk.');
        });
    }
});