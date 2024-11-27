const createHistoryBtn = document.getElementById('create-history');
const treatmentBtn = document.getElementById('add-treatment');
const vaccinationBtn = document.getElementById('add-vaccination');
const requestsBtn = document.getElementById('show-requests');

if (createHistoryBtn) {
    createHistoryBtn.addEventListener('click', () => {
        window.location.href = `/vet/new_medical_history/${animalId}`;
    });
}

treatmentBtn.addEventListener('click', () => {
    window.location.href = `/vet/new_treatment/${animalId}`;
});

vaccinationBtn.addEventListener('click', () => {
    window.location.href = `/vet/new_vaccination/${animalId}`;
});

requestsBtn.addEventListener('click', () => {
    window.location.href = `/vet/requests/${animalId}`;
});