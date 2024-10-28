
document.getElementById('logout').addEventListener('click', async function() {
    const response = await fetch('/user/logout', {
        method: 'POST'
    });

    if (response.ok) {
        window.location.href = '/';
    }
});