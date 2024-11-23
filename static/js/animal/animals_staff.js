const form = document.querySelector('form');

form?.addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(form);

    // if no file is selected, remove the photo field
    if (formData.get('photo').size === 0) {
        formData.delete('photo');
    }

    // send with form data content type
    const response = await fetch('/staff/animals/new', {
        method: 'POST',
        body: formData
    });

    if (response.ok && response.status === 201) {
       window.location.reload();
    }
});