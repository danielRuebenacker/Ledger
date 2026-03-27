$(document).ready(function () {
    // 1. INITIALIZE BOOTSTRAP MODALS
    // Using distinct variables to avoid the "ghost backdrop" issue
    var trackerModalEl = document.getElementById('createTrackerModal');
    var trackerModal = trackerModalEl ? new bootstrap.Modal(trackerModalEl) : null;

    var createHabitModalEl = document.getElementById('createHabitModal');
    var createHabitModal = createHabitModalEl ? new bootstrap.Modal(createHabitModalEl) : null;

    var logHabitModalEl = document.getElementById('logHabitModal');
    var logHabitModal = logHabitModalEl ? new bootstrap.Modal(logHabitModalEl) : null;

    var $book = $('#flipbook');

    // 2. AUTO-SHOW TRACKER SETUP IF NEEDED
    if (trackerModal && typeof SHOW_TRACKER_FORM !== 'undefined' && SHOW_TRACKER_FORM === true) {
        trackerModal.show();
    }

    // 3. FETCH LEDGER DATA AND BUILD BOOK
    $.ajax({
        url: MYHABITS_API_URL,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            var months = data.months;

            if (months.length === 0) {
                $('#no-data-msg').show();
                initBook();
                return;
            }

            // Iterate through months to create Left (Journal) and Right (Grid) pages
            $.each(months, function (i, month) {
                // LEFT PAGE: Journal entries
                var leftHtml = '<div class="page"><div class="page-inner ledger-left">';
                leftHtml += '<div class="ledger-header">';
                leftHtml += '<span class="ledger-month">' + month.month + '</span>';
                leftHtml += '<span class="ledger-days">\uD83D\uDCC5 ' + month.num_days + '</span>';
                leftHtml += '</div>';
                leftHtml += '<div class="journal-list">';
                $.each(month.journals, function (j, entry) {
                    var text = entry.text || '';
                    var cls = text ? '' : ' empty';
                    leftHtml += '<div class="journal-row' + cls + '">';
                    leftHtml += '<span class="journal-day">' + entry.day + '.</span>';
                    leftHtml += '<span class="journal-text">' + text + '</span>';
                    leftHtml += '</div>';
                });
                leftHtml += '</div></div></div>';
                $book.append(leftHtml);

                // RIGHT PAGE: Habit Grid
                var rightHtml = '<div class="page"><div class="page-inner ledger-right">';

                if (month.sections.length === 0) {
                    rightHtml += '<p class="habit-details">No habits tracked this month.</p>';
                } else { 
                    var allHabits = [];
                    var categoryStarts = {};
                    $.each(month.sections, function (s, section) {
                        categoryStarts[allHabits.length] = true;
                        $.each(section.habits, function (h, habit) {
                            allHabits.push({
                                name: habit.name,
                                emoji: section.emoji,
                                grid: habit.grid
                            });
                        });
                    });

                    rightHtml += '<table class="habit-grid"><thead><tr><th></th>';
                    $.each(month.sections, function (s, section) {
                        rightHtml += '<th class="grid-section-icon grid-category-start" colspan="' + section.habits.length + '">' + section.emoji + ' ' + section.label + '</th>';
                    });
                    rightHtml += '</tr><tr><th></th>';
                    $.each(allHabits, function (h, habit) {
                        var cls = 'grid-habit-name' + (categoryStarts[h] ? ' grid-category-start' : '');
                        rightHtml += '<th class="' + cls + '">' + habit.name + '</th>';
                    });
                    rightHtml += '</tr></thead><tbody>';

                    for (var d = 0; d < month.num_days; d++) {
                        rightHtml += '<tr><td class="grid-day-num">' + (d + 1) + '</td>';
                        $.each(allHabits, function (h, habit) {
                            var done = habit.grid[d];
                            var cls = 'grid-cell' + (categoryStarts[h] ? ' grid-category-start' : '');
                            rightHtml += '<td class="' + cls + '">';
                            if (done) rightHtml += '<span class="grid-x">\u2716</span>';
                            rightHtml += '</td>';
                        });
                        rightHtml += '</tr>';
                    }
                    rightHtml += '</tbody></table>';
                }
                rightHtml += '</div></div>';
                $book.append(rightHtml);
            });

            // Turn.js requirement: Ensure even page count
            var totalPages = $book.children('.page').length;
            if (totalPages % 2 !== 0) {
                $book.append('<div class="page"><div class="page-inner"><p class="habit-details">End of entries.</p></div></div>');
            }

            initBook();
        },
        error: function () {
            $('#no-data-msg').text('Failed to load habit data.').show();
            initBook();
        }
    });

    // 4. BOOK INITIALIZATION & CONTROLS
    function initBook() {
        $book.turn({
            width: 960,
            height: 600,
            autoCenter: true,
            when: {
                turned: function () { updateControls(); }
            }
        });
        updateControls();
    }

    function updateControls() {
        var current = $book.turn('page');
        var total = $book.turn('pages');
        var displayPage = Math.ceil((current - 1) / 2);
        var displayTotal = Math.floor((total - 1) / 2);

        if (displayPage < 1) {
            $('#page-indicator').text('Cover');
        } else if (displayPage > displayTotal) {
            $('#page-indicator').text('End');
        } else {
            $('#page-indicator').text('Page ' + displayPage + ' of ' + displayTotal);
        }
        $('#prev-btn').prop('disabled', current <= 1);
        $('#next-btn').prop('disabled', current >= total);
    }

    $('#prev-btn').on('click', function () { $book.turn('previous'); });
    $('#next-btn').on('click', function () { $book.turn('next'); });

    // 5. BUTTON TRIGGERS FOR MODALS
    $(document).on('click', '#setup-tracker-btn', function(e) {
        e.preventDefault();
        if (trackerModal) trackerModal.show();
    });

    $('#add-habit-btn').on('click', function () {
        if (createHabitModal) createHabitModal.show();
    });

    $('#log-habit-btn').on('click', function () {
        if (logHabitModal) {
            var today = new Date().toISOString().split('T')[0];
            $('#id_date').val(today).trigger('change');
            logHabitModal.show();
        }
    });

    // 6. LOG MODAL: FETCH DATA ON DATE CHANGE
    $(document).on('change', '#id_date', function() {
        var selectedDate = $(this).val();
        $.ajax({
            url: LOG_HABITS_URL,
            method: 'GET',
            data: { date: selectedDate },
            success: function(data) {
                // Populate Journal
                $('#id_journal_text').val(data.journal || '');
                // Reset and Populate Checkboxes
                $('input[name="habits"]').prop('checked', false);
                $.each(data.groups, function(i, group) {
                    $.each(group.habits, function(j, habit) {
                        if (habit.checked) {
                            $('input[value="' + habit.id + '"]').prop('checked', true);
                        }
                    });
                });
            }
        });
    });

    // 7. GLOBAL BACKDROP FIX
    // Ensures background is never stuck dark when a modal is closed via 'X' or Escape
    $(document).on('hidden.bs.modal', '.modal', function () {
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css('padding-right', '');
    });
});
