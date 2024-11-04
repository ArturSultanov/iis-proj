const logout_btn = document.getElementById('logout');
const logout_all_btn = document.getElementById('logout_all');

if (logout_btn) {
    logout_btn.addEventListener('click', async function() {
        const response = await fetch('/user/logout', {
            method: 'DELETE',
        });

        if (response.ok) {
            window.location.href = '/';
        }
    });
}

if (logout_all_btn) {
    logout_all_btn.addEventListener('click', async function() {

        const keep_check = document.getElementById('keep_this');
        var keep_this_session = false;
        if (keep_check) {
            keep_this_session = keep_check.checked;
        }
        const response = await fetch('/user/logout/all?keep_current='+keep_this_session, {
            method: 'DELETE',
        });

        if (response.ok) {
            if (!keep_this_session) {
                window.location.href = '/';
            } else {
                alert('All other sessions have been logged out');
            }
        }
    });
}