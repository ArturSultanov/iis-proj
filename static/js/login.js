const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    const response = await fetch('/user/signin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    });

    if (response.ok) {
        window.location.href = '/user/profile';
    } else {
        const error = await response.json();
        document.getElementById('error').textContent = error.detail;
    }
});

loginForm.addEventListener('input', function () {
    document.getElementById('error').textContent = '';
});

// get username and password from local storage
const username = localStorage.getItem('username');
const password = localStorage.getItem('password');
if (username) {
    document.getElementById('username').value = username;
}
if (password) {
    document.getElementById('password').value = password;
}
localStorage.clear();