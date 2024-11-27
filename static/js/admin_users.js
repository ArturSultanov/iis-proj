document.addEventListener('DOMContentLoaded', function () {
    const activeCheckboxes = document.querySelectorAll('.active-checkbox');
    activeCheckboxes.forEach(function (activeCheckbox) {
        activeCheckbox.addEventListener('change', async function () {
            const userId = activeCheckbox.getAttribute('user_id');
            const active = !activeCheckbox.checked;

            const response = await fetch(`/admin/users/${userId}/state?active=${active}`, {
                method: 'PATCH'
            });

            if (!response.ok) {
                const error = await response.json();
                document.getElementById('error').textContent = error.detail;
            } else {
                document.getElementById('success').textContent = 'User state updated';
                // Remove the success message after 3 seconds
                setTimeout(function () {
                    document.getElementById('success').textContent = '';
                }, 3000);
            }
        });
    });

    const roleSelects = document.querySelectorAll('.role-select');
    roleSelects.forEach(function (roleSelect) {
        roleSelect.addEventListener('change', async function () {
            const userId = roleSelect.getAttribute('user_id');
            const role = roleSelect.value;

            const response = await fetch(`/admin/users/${userId}/role?role=${role}`, {
                method: 'PATCH'
            });

            if (!response.ok) {
                const error = await response.json();
                document.getElementById('error').textContent = error.detail;
            } else {
                document.getElementById('success').textContent = 'Role updated';
                // Remove the success message after 3 seconds
                setTimeout(function () {
                    document.getElementById('success').textContent = '';
                }, 3000);
            }
        });
    });

    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(function (deleteButton) {
        deleteButton.addEventListener('click', async function () {
            const userId = deleteButton.getAttribute('user_id');

            const response = await fetch(`/admin/users/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                document.getElementById(`user-${userId}`).remove();
                document.getElementById('success').textContent = 'User deleted';
                // Remove the success message after 3 seconds
                setTimeout(function () {
                    document.getElementById('success').textContent = '';
                }, 3000);
            } else {
                const error = await response.json();
                document.getElementById('error').textContent = error.detail;
            }
        });
    });
});