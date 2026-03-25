$(document).ready(function () {
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
                    rightHtml += '<div class="habit-grid-container">';
                    $.each(month.sections, function (s, section) {
                        rightHtml += '<div class="grid-section">';
                        // Section header row with emoji + habit names
                        rightHtml += '<div class="grid-section-header">';
                        rightHtml += '<span class="grid-section-icon">' + section.emoji + '</span>';
                        rightHtml += '</div>';
                        // Habit name headers
                        rightHtml += '<table class="habit-grid">';
                        rightHtml += '<thead><tr><th></th>';
                        $.each(section.habits, function (h, habit) {
                            rightHtml += '<th class="grid-habit-name">' + habit.name + '</th>';
                        });
                        rightHtml += '</tr></thead><tbody>';
                        // One row per day
                        for (var d = 0; d < month.num_days; d++) {
                            rightHtml += '<tr>';
                            rightHtml += '<td class="grid-day-num">' + (d + 1) + '</td>';
                            $.each(section.habits, function (h, habit) {
                                var done = habit.grid[d];
                                rightHtml += '<td class="grid-cell">';
                                if (done) {
                                    rightHtml += '<span class="grid-x">\u2716</span>';
                                }
                                rightHtml += '</td>';
                            });
                            rightHtml += '</tr>';
                        }
                        rightHtml += '</tbody></table></div>';
                    });
                    rightHtml += '</div>';
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
        $('#page-indicator').text('Page ' + current + ' of ' + total);
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
    $('#create-habit-form').on('submit', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $error = $('#habit-form-error');
        $error.hide();

        $.ajax({
            url: CREATE_HABIT_URL,
            method: 'POST',
            data: $form.serialize(),
            dataType: 'json',
            success: function (data) {
                $('#habit-modal-overlay').hide();
                $form[0].reset();
                location.reload();
            },
            error: function (xhr) {
                var msg = 'Something went wrong.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg = xhr.responseJSON.error;
                }
                $error.text(msg).show();
            }
        });
    });

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

    // Open log modal
    $('#log-habit-btn').on('click', function () {
        var today = new Date().toISOString().split('T')[0];
        $('#log-date').val(today);
        $('#log-form-error').hide();
        loadLogHabits(today);
        $('#log-modal-overlay').css('display', 'flex');
    });

    // When date changes, reload habits for that date
    $('#log-date').on('change', function () {
        loadLogHabits($(this).val());
    });

    // Close log modal
    $('#cancel-log-btn').on('click', function () {
        $('#log-modal-overlay').hide();
    });

    $('#log-modal-overlay').on('click', function (e) {
        if (e.target === this) {
            $(this).hide();
        }
    });

    // Submit log
    $('#log-habit-form').on('submit', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $error = $('#log-form-error');
        $error.hide();

        $.ajax({
            url: LOG_HABITS_URL,
            method: 'POST',
            data: $form.serialize(),
            dataType: 'json',
            success: function () {
                $('#log-modal-overlay').hide();
                location.reload();
            },
            error: function (xhr) {
                var msg = 'Something went wrong.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg = xhr.responseJSON.error;
                }
                $error.text(msg).show();
            }
        });
    });

});
