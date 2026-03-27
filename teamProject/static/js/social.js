document.addEventListener('DOMContentLoaded', function() {
    
    function getCsrfToken() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;

        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            const token = getCsrfToken();

            fetch('/api/friends/request/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': token 
                },
                body: JSON.stringify({ user_id: userId }),
            })
            .then(r => r.json())
            .then(data => {
                this.textContent = 'Pending';
                this.disabled = true;
                this.style.backgroundColor = '#ccc';
                this.classList.add('btn-disabled');
            })
            .catch(err => console.error('Error sending request:', err));
        });
    });

    document.querySelectorAll('.btn-accept, .btn-decline').forEach(btn => {
        btn.addEventListener('click', function () {
            const requestId = this.dataset.requestId;
            const action = this.dataset.action;
            const token = getCsrfToken();

            fetch('/api/friends/handle/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': token 
                },
                body: JSON.stringify({ request_id: requestId, action: action }),
            })
            .then(r => r.json())
            .then(data => {
                const card = document.getElementById('req-card-' + requestId);
                if (card) card.remove();
            })
            .catch(err => console.error('Error handling request:', err));
        });
    });
});
