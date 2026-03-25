$(document).ready(function() {

	let notifications = [];

	function fetchNotifications() {
		$.ajax({
		url: "/api/notifications/get_notifs", 
		method: "GET"
	  }).done(function(data) {
		notifications = data;
		updateBadge();
		renderNotifications();
	  });
	}

	function getNumberUnreadNotifs() {
		return notifications.filter(n => !n.notified).length;
	}

	// render by adding them to the dropdown list
	function renderNotifications() {
		// empty notif list
	    const list = $("#notif-list");
	    list.empty();

		// are there notifs?
	    if (!notifications || notifications.length === 0) {
	        list.append('<li><span class="dropdown-item text-muted">No notifications</span></li>');
	        return;
	    }

		// for each notif add
	    notifications.forEach(n => {
	        list.append(`
	        <li>
	      	    <span class="dropdown-item ${n.notified ? 'read' : 'unread'}">
	      	    	${n.nudger} sent a nudge! Log your habits!
				</span>
	        </li>`);
		});
	}

	// adds red count icon to icon to indicate how many new notifs
	function updateBadge() {
		// get how many notifs have unread
		const no_unread = getNumberUnreadNotifs();
	    const badge = $("#notif-badge");
	    if (no_unread > 0) {
	    	badge.text(no_unread).show();
	    } else {
	    	badge.hide();
	    }
	}

	// initial fetch
	fetchNotifications();

	// update every 60 secs
	setInterval(fetchNotifications, 60000);

	$('#notifDropdown').on('shown.bs.dropdown', sendUpdateNudgeRequest);

	function sendUpdateNudgeRequest() {
		// are there actually unread notifs?
		const unread = getNumberUnreadNotifs();
		if (unread.length === 0) return;

		$.ajax({
			url: "/api/notifications/mark_read/",
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie('csrftoken')
			},
			success: clearUnreadNotifIndicators,
			error: function(err) {
				console.error("Failed to mark notifications read:", err);
			}
		});
	}

	function clearUnreadNotifIndicators() {
		// update local notifications state
		notifications.forEach(n => n.notified = true);
		updateBadge(); // hide badge
	}

	// need csrf token for post forms
	function getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let cookie of cookies) {
				cookie = cookie.trim();
				if (cookie.startsWith(name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
    return cookieValue;
}


});
