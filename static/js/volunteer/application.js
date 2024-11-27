document.getElementById('application_form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const response = await fetch('/user/volunteer_application', {
        method: 'POST',
        body: formData
    });
    if (response.ok) {
        window.location.reload();
    }
});