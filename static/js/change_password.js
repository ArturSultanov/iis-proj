const password_form = document.getElementById('change-password-form');

password_form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(password_form);

    //clear form
    password_form.reset();

    const response = await fetch('/user/change_password', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        document.getElementById('error').textContent = error.detail;
    } else {
        document.getElementById('success').textContent = 'Password updated';
        // Remove the success message after 3 seconds
        setTimeout(function () {
            document.getElementById('success').textContent = '';
            window.location.href = '/user/profile';
        }, 3000);
    }
});

password_form.addEventListener('input', async function (event) {
    document.getElementById('error').textContent = '';

    const formData = new FormData(password_form);
    const password = formData.get('new_password');
    const password_confirm = formData.get('confirm_password');

    if (password !== password_confirm) {
        document.getElementById('error').textContent = 'Passwords do not match';
        return;
    }
    document.getElementById('success').textContent = '';
});