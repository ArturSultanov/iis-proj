const accept = document.getElementById('accept-btn');

const complete = document.getElementById('complete-btn');

accept?.addEventListener('click', function() {
    fetch(`/vet/request/${requestId}/accept`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('status').innerText = 'accepted';
            accept.style.display = 'none';
            window.parent.postMessage({ action: 'updateStatus', requestId: requestId, status: 'accepted' }, '*');
        } else {
            alert('Failed to accept the request.');
        }
    });
});

complete?.addEventListener('click', function() {
    fetch(`/vet/request/${requestId}/complete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('status').innerText = 'completed';
            complete.style.display = 'none';
            accept.style.display = 'none';
            window.parent.postMessage({ action: 'updateStatus', requestId: requestId, status: 'completed' }, '*');
        } else {
            alert('Failed to complete the request.');
        }
    });
});