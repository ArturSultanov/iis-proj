// keyboard arrow navigation
document.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft' && document.getElementById('prev_page')) {
        document.getElementById('prev_page').click();
    } else if (event.key === 'ArrowRight' && document.getElementById('next_page')) {
        document.getElementById('next_page').click();
    }
});
// Row clicks
document.addEventListener('click', function (event) {
    if (event.target.tagName === 'TD') {
        const id = event.target.parentElement.id;
        window.location.href = `/animals/${id}/profile`;
    }
});