const vaccinationForm = document.getElementById('vaccination_form');

vaccinationForm.addEventListener('submit', async function(event) {
    event.preventDefault();

    const dateInput = document.getElementById('date').value;
    const timeInput = document.getElementById('time').value;

    const datetime = `${dateInput}T${timeInput}:00`;

    const formData = new FormData();
    formData.append("date", datetime);
    formData.append("description", document.getElementById('description').value);

    const response = await fetch(`/vet/new_vaccination/${animalId}`, {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        window.location.href = `/vet/medical_history_profile/${animalId}`;}
    else if (response.status === 404) {
            alert("Medical history not found. Please create it first.");}
    else {
        alert("Error: Could not submit vaccination.");
    }
});

const now = new Date();
const today = now.toISOString().split('T')[0];
const currentTime = now.toTimeString().slice(0, 5);

const dateInput = document.getElementById('date');
const timeInput = document.getElementById('time');
dateInput.value = today;
dateInput.min = today;
timeInput.value = currentTime;