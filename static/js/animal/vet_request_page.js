const vetRequestForm = document.getElementById('vet_request_form');

vetRequestForm.addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(vetRequestForm);

    const response = await fetch(`/staff/new_request/${animalId}`, {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        window.location.href = `/animals/${animalId}/profile`;
    }
});