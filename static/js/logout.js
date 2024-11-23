const logout_btns = document.getElementsByClassName('logout-this')
const logout_all_btns = document.getElementsByClassName('logout-all')

for (const logout_btn of logout_btns) {
    logout_btn.addEventListener('click', async function() {
        const response = await fetch('/user/logout', {
            method: 'DELETE',
        });

        if (response.ok) {
            window.location.href = '/';
        }
    });
}

for (const logout_all_btn of logout_all_btns) {
    logout_all_btn.addEventListener('click', async function() {
        const keep_logged_in = document.getElementById('keep_this').checked;
        const response = await fetch(`/user/logout/all?keep_current=${keep_logged_in}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            if (!keep_logged_in) window.location.href = '/';
        }
    });
}