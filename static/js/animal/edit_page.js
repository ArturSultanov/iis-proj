document.getElementById('edit-name').addEventListener('click', function() {
    var name = prompt('Enter new name');
    // put with new_name as query parameter
    if (name) {
        fetch('/staff/animals/{{ animal.id }}/name?new_name=' + name, {
            method: 'PUT'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('name').textContent = data.name;
        });
    }
});

document.getElementById('photo_upload_form').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData();
    let photo = document.getElementById('photo').files[0];
    // if photo is undefined send empty put request to clear photo
    let response;
    if (photo) {
        formData.append('photo', photo);
        response = fetch('/staff/animals/{{ animal.id }}/photo', {
            method: 'PATCH',
            body: formData
        });
    } else {
        response = fetch('/staff/animals/{{ animal.id }}/photo', {
            method: 'DELETE'
        });
    }

    if (response) {
        response
        .then(response => response.json())
        .then(data => {
            // fetch new photo
            fetch('/animals/{{ animal.id }}/photo', {
                method: 'GET'
            })
            .then(response => response.blob())
            .then(blob => {
                document.querySelector('img').src = URL.createObjectURL(blob);
                // reset file input
                document.getElementById('photo').value = '';
                document.getElementById('photo_submit').textContent = 'Delete Photo';
            });
        });
    }
});

// on file input change
document.getElementById('photo').addEventListener('change', function() {
    let photo = document.getElementById('photo').files[0];
    if (photo) {
        document.getElementById('photo_submit').textContent = 'Upload Photo';
    } else {
        document.getElementById('photo_submit').textContent = 'Delete Photo';
    }
});

document.getElementById('edit-age').addEventListener('click', function() {
    var age = prompt('Enter new age');
    if (age) {
        fetch('/staff/animals/{{ animal.id }}/age?new_age=' + age, {
            method: 'PATCH'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('age').textContent = data.age;
        });
    }
});

document.getElementById('edit-description').addEventListener('click', function() {
    var description = document.getElementById('description').textContent;
    console.log(description);
    // encode description with newlines
    var query_encoded = encodeURIComponent(description).replace(/%0A/g, '%0D%0A');
    if (description) {
        fetch('/staff/animals/{{ animal.id }}/description?new_description=' + query_encoded, {
            method: 'PATCH'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('description').textContent = data.description;
        });
    }
});

document.getElementById('edit-species').addEventListener('click', function() {
    var species = prompt('Enter new species');
    if (species) {
        fetch('/staff/animals/{{ animal.id }}/species?new_species=' + species, {
            method: 'PATCH'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('species').textContent = data.species;
        });
    }
});

const editableDiv = document.getElementById('description');

    editableDiv.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default behavior (new block)
            document.execCommand('insertLineBreak'); // Insert a line break
        }
    });