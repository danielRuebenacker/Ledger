$(document).ready(function () {
    // 1. MODAL INITIALIZATION
    const getModal = (id) => {
        const el = document.getElementById(id);
        return el ? new bootstrap.Modal(el) : null;
    };

    const trackerModal = getModal('createTrackerModal');
    const createHabitModal = getModal('createHabitModal');
    const logHabitModal = getModal('logHabitModal');
    const $book = $('#flipbook');

    // 2. BOOK INITIALIZATION (Django-rendered)
    if ($book.length > 0 && $book.children().length > 0) {
        $book.turn({
            width: 960,
            height: 600,
            autoCenter: true,
            display: 'double',
            acceleration: true,
            elevation: 50,
            gradients: true,
            when: {
                turned: function () { updateControls(); }
            }
        });
        // Jump to the end of the ledger by default
        $book.turn('page', $book.turn('pages'));
    }

    // 3. CONTROLS & INDICATORS
    function updateControls() {
        const current = $book.turn('page');
        const total = $book.turn('pages');
        
        // Logical page math: Cover is 1, then Spreads are (2,3), (4,5)
        const displayPage = Math.floor(current / 2);
        const displayTotal = Math.floor(total / 2);

        if (current === 1) {
            $('#page-indicator').text('Cover');
        } else if (current >= total - 1 && total > 2) {
            $('#page-indicator').text('End');
        } else {
            $('#page-indicator').text('Month ' + displayPage + ' of ' + displayTotal);
        }

        $('#prev-btn').prop('disabled', current <= 1);
        $('#next-btn').prop('disabled', current >= total);
    }

    $('#prev-btn').on('click', () => $book.turn('previous'));
    $('#next-btn').on('click', () => $book.turn('next'));

    // 4. BUTTON CLICK EVENTS
    // Check your HTML: ensure the buttons have these EXACT IDs
    $(document).on('click', '#setup-tracker-btn', (e) => {
        e.preventDefault();
        trackerModal?.show();
    });

    $(document).on('click', '#add-habit-btn', () => createHabitModal?.show());

    // Matches the "Log Habits" button in your UI
    $(document).on('click', '#log-habit-btn', function() {
        if (logHabitModal) {
            const today = new Date().toISOString().split('T')[0];
            $('#id_date').val(today).trigger('change');
            logHabitModal.show();
        }
    });

    // 6. CLEANUP FIX (Ghost Backdrops)
    $(document).on('hidden.bs.modal', '.modal', function () {
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css('padding-right', '');
    });

    // Auto-show tracker if flag is set
    if (typeof SHOW_TRACKER_FORM !== 'undefined' && SHOW_TRACKER_FORM) {
        trackerModal?.show();
    }
});
