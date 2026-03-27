$(document).ready(function () {
    const getModal = (id) => {
        const el = document.getElementById(id);
        return el ? new bootstrap.Modal(el) : null;
    };

    const trackerModal = getModal('createTrackerModal');
    const createHabitModal = getModal('createHabitModal');
    const logHabitModal = getModal('logHabitModal');
    const $book = $('#flipbook');

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
		// jump to last page
        $book.turn('page', $book.turn('pages'));
    }

    function updateControls() {
        const current = $book.turn('page');
        const total = $book.turn('pages');
        
        // logical page math: Cover is 1, then Spreads are (2,3), (4,5)
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

	// create tracker button (on rhs page)
    $(document).on('click', '#setup-tracker-btn', (e) => {
        e.preventDefault();
        trackerModal?.show();
    });

	// create/add habits button
    $(document).on('click', '#add-habit-btn', () => createHabitModal?.show());

	// log habits button
    $(document).on('click', '#log-habit-btn', function() {
        if (logHabitModal) {
            const today = new Date().toISOString().split('T')[0];
            $('#id_date').val(today).trigger('change');
            logHabitModal.show();
        }
    });

	// bug fix: issue with not exiting when pressing x
    $(document).on('hidden.bs.modal', '.modal', function () {
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css('padding-right', '');
    });

    // auto show tracker creation form if flag is set
    if (typeof SHOW_TRACKER_FORM !== 'undefined' && SHOW_TRACKER_FORM) {
        trackerModal?.show();
    }
});
