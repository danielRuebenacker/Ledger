function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const nudgeBtn = document.getElementById('nudge-btn');

if (nudgeBtn) {
    nudgeBtn.addEventListener('click', async () => {
        const response = await fetch(`/profile/${profileUsername}/nudge/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });

        const data = await response.json();
        if (data.status === 'ok') {
            nudgeBtn.textContent = '✅ Nudged!';
            nudgeBtn.disabled = true;
        }
    });
}