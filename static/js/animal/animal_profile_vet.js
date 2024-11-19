const showHistoryBtn = document.getElementById('show-history');

showHistoryBtn.addEventListener('click', () => {
    window.location.href = `/vet/medical_history_profile/${animalId}`;
});