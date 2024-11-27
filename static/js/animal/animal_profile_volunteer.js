// static/js/animal_profile_volunteer.js

const reserveBtn = document.getElementById('reserve-animal');

reserveBtn.addEventListener('click', () => {
    window.location.href = `/volunteer/animals/${animalId}/calendar`;
});
