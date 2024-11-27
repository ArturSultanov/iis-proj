// const animalId = {{ animal.id }};

const animalIdInt = parseInt(animalId, 10);
if (isNaN(animalIdInt)) {
    console.error('Invalid animal ID');
}

const editBtn = document.getElementById('edit-animal-profile');
const hideBtn = document.getElementById('hide-animal');
const deleteBtn = document.getElementById('delete-animal');
const createRequestBtn = document.getElementById('create-request');

editBtn.addEventListener('click', () => {
    window.location.href = `/staff/animals/${animalId}/edit`;
});

createRequestBtn.addEventListener('click', () => {
    window.location.href = `/staff/new_request/${animalId}`;
});

hideBtn.addEventListener('click', () => {
    const isCurrentlyHidden = hideBtn.textContent.trim().toLowerCase() === 'show';
    fetch(`/staff/animals/${animalId}/hide?hidden=${!isCurrentlyHidden}`, {
        method: 'PATCH',
    })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to hide the animal');
            }
        });
});

deleteBtn.addEventListener('click', () => {
    // ask for confirmation
    if (confirm('Are you sure you want to delete this animal?')) {
        fetch(`/staff/animals/${animalId}`, {
            method: 'DELETE',
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/animals';
                } else {
                    alert('Failed to delete the animal');
                }
            });
    }
});