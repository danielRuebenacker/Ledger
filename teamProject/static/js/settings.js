const btn = document.getElementById('dark-light');
const picInput = document.getElementById('profile-pic-input');
const picPreview = document.getElementById('profile-preview');
const aboutMe = document.getElementById('aboutme');
const aboutMeStatus = document.getElementById('aboutme-status');

const isDarkOnLoad = document.body.classList.contains('dark-mode');
btn.textContent = isDarkOnLoad ? 'Switch to Light Mode' : 'Switch to Dark Mode';

btn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');

    const isDark = document.body.classList.contains('dark-mode');
    btn.textContent = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';

    fetch('/settings/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ theme: isDark ? 'dark' : 'light' }),
    });
});

picInput.addEventListener('change', async () => {
    const file = picInput.files[0];
    if (!file) return;

    picPreview.src = URL.createObjectURL(file);

    const formData = new FormData();
    formData.append('picture', file);

    const response = await fetch('/settings/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
    });

    const data = await response.json();
    if (data.status === 'ok') {
        picPreview.src = data.picture_url;
    }
});

let lastSaved = aboutMe.value.trim();
let Timer;

aboutMe.addEventListener('input', () => {
    clearTimeout(Timer);
    Timer = setTimeout(async () => {
        const current = aboutMe.value.trim();

        if (current === lastSaved) return;

        const response = await fetch('/settings/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ about_me: current }),
        });

        const data = await response.json();
        if (data.status === 'ok') {
            lastSaved = current;
            aboutMeStatus.textContent = 'Saved!';
            setTimeout(() => aboutMeStatus.textContent = '', 2000);
        } else {
            aboutMeStatus.textContent = 'Error saving';
        }
    }, 800);
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}