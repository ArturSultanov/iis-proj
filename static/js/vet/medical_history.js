const historyForm = document.getElementById('history_form');

historyForm.addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(historyForm);

    const response = await fetch(`/vet/new_medical_history/${animalId}`, {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        if (data.message === "Medical history created successfully") {
            window.location.href = `/vet/medical_history_profile/${animalId}`;
        } else {
            alert("Error: " + data.message);
        }
    } else {
        alert("Error: Failed to create medical history.");
    }
});