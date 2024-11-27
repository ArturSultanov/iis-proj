// submit logic
document.getElementById('registerForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Collect form data
    const formData = {
        name: document.getElementById('name').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        confirm_password: document.getElementById('confirm_password').value
    };

    // if password or username is empty
    if (formData.password === '' || formData.username === '') {
        document.getElementById('errorMessages').textContent = 'Username and password cannot be empty';
        return;
    }

    // Send data as JSON
    const response = await fetch('signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData) // Convert the form data to JSON
    });

    if (response.ok) {
        window.location.href = '/user/signin';
        localStorage.setItem('username', formData.username);
        localStorage.setItem('password', formData.password);
    } else {
        const error = await response.json();
        document.getElementById('errorMessages').textContent = error.detail || 'Registration failed';
    }
});

// input validation
document.getElementById('registerForm').addEventListener('input', function() {
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    document.getElementById('errorMessages').textContent = '';
    if (password.length < 6) {
        document.getElementById('errorMessages').textContent = 'Password must be at least 6 characters';
    } else if (password !== confirm_password) {
        document.getElementById('errorMessages').textContent = 'Passwords do not match';
    }
});