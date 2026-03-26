$(document).ready(function () {
	var modalElement = document.getElementById('createTrackerModal');
    var trackerModal;

    // 1. Initialize the modal instance if the element exists
    if (modalElement) {
        trackerModal = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true
        });

        // 2. Auto-show only if the Django flag is True
        // We use the variable you defined: SHOW_TRACKER_FORM
        if (typeof SHOW_TRACKER_FORM !== 'undefined' && SHOW_TRACKER_FORM === true) {
            trackerModal.show();
        }
    }

    // 3. Manual trigger for the button on the turn.js page
    $(document).on('click', '#setup-tracker-btn', function(e) {
        e.preventDefault();
        console.log("Setup button clicked"); // Debugging line
        
        if (trackerModal) {
            trackerModal.show();
        } else {
            console.error("Modal instance not initialized.");
        }
    });

    var $book = $('#flipbook');

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

            // Each month = left page (journals) + right page (habit grid)
            $.each(months, function (i, month) {
                // ── LEFT PAGE: month header + journal entries ──
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

                // ── RIGHT PAGE: habit grid with X marks ──
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
                    rightHtml += '<table class="habit-grid">';
                    rightHtml += '<thead>';
                    // Category row — emoji + label, spanning its habits
                    rightHtml += '<tr><th></th>';
                    $.each(month.sections, function (s, section) {
                        rightHtml += '<th class="grid-section-icon grid-category-start" colspan="' + section.habits.length + '">' + section.emoji + ' ' + section.label + '</th>';
                    });
                    rightHtml += '</tr>';
                    // Habit name row — one cell per habit
                    rightHtml += '<tr><th></th>';
                    $.each(allHabits, function (h, habit) {
                        var cls = 'grid-habit-name' + (categoryStarts[h] ? ' grid-category-start' : '');
                        rightHtml += '<th class="' + cls + '">' + habit.name + '</th>';
                    });
                    rightHtml += '</tr>';
                    rightHtml += '</thead>';
                    rightHtml += '<tbody>';
                    for (var d = 0; d < month.num_days; d++) {
                        rightHtml += '<tr>';
                        rightHtml += '<td class="grid-day-num">' + (d + 1) + '</td>';
                        $.each(allHabits, function (h, habit) {
                            var done = habit.grid[d];
                            var cls = 'grid-cell' + (categoryStarts[h] ? ' grid-category-start' : '');
                            rightHtml += '<td class="' + cls + '">';
                            if (done) {
                                rightHtml += '<span class="grid-x">\u2716</span>';
                            }
                            rightHtml += '</td>';
                        });
                        rightHtml += '</tr>';
                    }
                    rightHtml += '</tbody></table>';
                }

                rightHtml += '</div></div>';
                $book.append(rightHtml);
            });

            // Ensure even page count (turn.js needs pairs)
            var totalPages = $book.children('.page').length;
            if (totalPages % 2 !== 0) {
                $book.append(
                    '<div class="page"><div class="page-inner">' +
                    '<p class="habit-details">End of entries.</p>' +
                    '</div></div>'
                );
            }

            initBook();
        },
        error: function () {
            $('#no-data-msg').text('Failed to load habit data.').show();
            initBook();
        }
    });

    function initBook() {
        $book.turn({
            width: 960,
            height: 600,
            autoCenter: true,
            when: {
                turned: function () {
                    updateControls();
                }
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

    $('#prev-btn').on('click', function () {
        $book.turn('previous');
    });

    $('#next-btn').on('click', function () {
        $book.turn('next');
    });

    // Modal open/close
    $('#add-habit-btn').on('click', function () {
        $('#habit-modal-overlay').css('display', 'flex');
        $('#habit-form-error').hide();
    });

    $('#cancel-habit-btn').on('click', function () {
        $('#habit-modal-overlay').hide();
    });

    $('#habit-modal-overlay').on('click', function (e) {
        if (e.target === this) {
            $(this).hide();
        }
    });

    // Create habit form submission
    // $('#create-habit-form').on('submit', function (e) {
    //     e.preventDefault();
    //     var $form = $(this);
    //     var $error = $('#habit-form-error');
    //     $error.hide();
    //
    //     $.ajax({
    //         url: CREATE_HABIT_URL,
    //         method: 'POST',
    //         data: $form.serialize(),
    //         dataType: 'json',
    //         success: function (data) {
    //             $('#habit-modal-overlay').hide();
    //             $form[0].reset();
    //             location.reload();
    //         },
    //         error: function (xhr) {
    //             var msg = 'Something went wrong.';
    //             if (xhr.responseJSON && xhr.responseJSON.error) {
    //                 msg = xhr.responseJSON.error;
    //             }
    //             $error.text(msg).show();
    //         }
    //     });
    // });
    //
    // ── Log Habits Modal ──

    function formatDateLabel(dateStr) {
        var d = new Date(dateStr + 'T00:00:00');
        var day = d.getDate();
        var suffix = 'th';
        if (day % 10 === 1 && day !== 11) suffix = 'st';
        else if (day % 10 === 2 && day !== 12) suffix = 'nd';
        else if (day % 10 === 3 && day !== 13) suffix = 'rd';
        var months = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];
        return day + suffix + ' ' + months[d.getMonth()];
    }

    function loadLogHabits(dateStr) {
        var $container = $('#log-habits-container');
        $container.empty();

        $.ajax({
            url: LOG_HABITS_URL,
            method: 'GET',
            data: { date: dateStr },
            dataType: 'json',
            success: function (data) {
                $('#log-journal').val(data.journal || '');

                if (data.groups.length === 0) {
                    $container.html('<p style="color:#6b5a47; font-style:italic;">No habits yet. Create one first!</p>');
                    return;
                }

                $.each(data.groups, function (i, group) {
                    var html = '<div class="log-group">';
                    html += '<div class="log-group-header">';
                    html += '<span class="log-group-emoji">' + group.emoji + '</span>';
                    html += '<span>' + group.label + '</span>';
                    html += '</div>';
                    html += '<div class="log-habit-list">';

                    $.each(group.habits, function (j, habit) {
                        var checkedAttr = habit.checked ? ' checked' : '';
                        html += '<div class="log-habit-item">';
                        html += '<input type="checkbox" name="habits" value="' + habit.id + '" id="log-h-' + habit.id + '"' + checkedAttr + '>';
                        html += '<label for="log-h-' + habit.id + '">' + habit.name + '</label>';
                        html += '</div>';
                    });

                    html += '</div></div>';
                    $container.append(html);
                });
            },
            error: function () {
                $container.html('<p style="color:#ae2012;">Failed to load habits.</p>');
            }
        });
    }

	// Initialize the Bootstrap Modal
    var logModalEl = document.getElementById('logHabitModal');
    var logBootstrapModal = logModalEl ? new bootstrap.Modal(logModalEl) : null;

    // Show modal on button click
    $('#log-habit-btn').on('click', function () {
        if (logBootstrapModal) {
            // Set default date to today
            var today = new Date().toISOString().split('T')[0];
            $('#id_date').val(today);
            
            // Trigger the change event to fetch existing data for today
            $('#id_date').trigger('change');
            
            logBootstrapModal.show();
        }
    });

    // // Keep the GET AJAX to load existing data when date changes
    // $(document).on('change', '#id_date', function() {
    //     var selectedDate = $(this).val();
    //     $.ajax({
    //         url: LOG_HABITS_URL, // Your existing GET API
    //         method: 'GET',
    //         data: { date: selectedDate },
    //         success: function(data) {
    //             $('#id_journal_text').val(data.journal || '');
    //             $('input[name="habits"]').prop('checked', false);
    //
    //             $.each(data.groups, function(i, group) {
    //                 $.each(group.habits, function(j, habit) {
    //                     if (habit.checked) {
    //                         $('input[value="' + habit.id + '"]').prop('checked', true);
    //                     }
    //                 });
    //             });
    //         }
    //     });
    // });
	//
	
	// 1. Initialize Modals
    var createHabitModal = new bootstrap.Modal(document.getElementById('createHabitModal'));
    var logHabitModal = new bootstrap.Modal(document.getElementById('logHabitModal'));

    // 2. Button Triggers
    $('#add-habit-btn').on('click', function () {
        createHabitModal.show();
    });

    $('#log-habit-btn').on('click', function () {
        // Today logic we wrote earlier
        var today = new Date().toISOString().split('T')[0];
        $('#id_date').val(today).trigger('change');
        logHabitModal.show();
    });
});
