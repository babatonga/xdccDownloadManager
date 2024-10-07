const URL_IRC_CONNECTIONS_LIST = '/api/irc_connections/?format=json';
const URL_IRC_CONNECTIONS_DETAIL = '/api/irc_connections/{id}/?format=json';
const URL_IRC_CHANNELS_LIST = '/api/irc_channels/?format=json';
const URL_IRC_CHANNELS_DETAIL = '/api/irc_channels/{id}/?format=json';
const URL_XDCC_OFFERS_LIST = '/api/xdcc_offers/?format=json';
const URL_XDCC_OFFERS_DETAIL = '/api/xdcc_offers/{id}/?format=json';

/**
 * Gets the current timestamp.
 * @returns {number} The current timestamp in milliseconds.
 */
function getCurrentTimestamp() {
    var date = new Date();
    return date.getTime();
}

function getSecondsSince(timestamp) {
    var currentTimestamp = getCurrentTimestamp();
    var secondsSince = (currentTimestamp - timestamp) / 1000;
    return secondsSince;
}

/**
 * Calculates the time elapsed since a given timestamp.
 * @param {number} timestamp - The timestamp to calculate time since.
 * @returns {string} A string representing the time elapsed.
 */
function getTimeSince(timestamp) {
    var secondsSince = getSecondsSince(timestamp);
    var timeSince = "";
    if (secondsSince < 60) {
        timeSince = Math.round(secondsSince) + " seconds ago";
    } else if (secondsSince < 3600) {
        timeSince = Math.round(secondsSince / 60) + " minutes ago";
    } else if (secondsSince < 86400) {
        timeSince = Math.round(secondsSince / 3600) + " hours ago";
    } else {
        timeSince = Math.round(secondsSince / 86400) + " days ago";
    }
    return timeSince;
}

/**
 * Creates a toast notification.
 * @param {string} title - The title of the toast notification.
 * @param {string} message - The message content of the toast notification.
 * @param {string} type - The type of the toast notification (success, info, warning, error).
 * @param {number} [autohide=0] - The duration in milliseconds after which the toast automatically hides.
 */
function createToast(title, message, type, autohide = 0, escape = true) {
    var toastcontainer = document.getElementById("toastcontainer");
    var toast = document.createElement("div");
    toast.className = "toast";
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");
    var toast_header = document.createElement("div");
    toast_header.className = "toast-header " + (type == "success" ? " bg-success" : type == "info" ? " bg-info" : type == "warning" ? " bg-warning" : type == "error" ? " bg-danger text-white" : " bg-info");
    var header_icon = document.createElement("i");
    header_icon.className = "bi";
    header_icon.className += type == "success" ? " bi-check-circle-fill" : type == "info" ? " bi-info-circle-fill" : type == "warning" ? " bi-exclamation-triangle-fill" : type == "error" ? " bi-x-circle-fill" : " bi-info-circle-fill";
    var toast_title = document.createElement("strong");
    toast_title.className = "me-auto"
    toast_title.innerHTML = "&nbsp;" + escapeHtml(title);
    var toast_time = document.createElement("small");
    toast_time.innerText = "now";
    var toast_button = document.createElement("button");
    toast_button.type = "button";
    toast_button.className = "btn-close";
    toast_button.setAttribute("data-bs-dismiss", "toast");
    toast_button.setAttribute("aria-label", "Close");
    toast_button.addEventListener("click", function () {
        clearInterval(intervalId);
    });
    var toast_body = document.createElement("div");
    toast_body.className = "toast-body";
    if (escape) {
        toast_body.innerHTML = escapeHtml(message);
    } else {
        toast_body.innerHTML = message;
    }
    toast.appendChild(toast_header);
    toast_header.appendChild(header_icon);
    toast_header.appendChild(toast_title);
    toast_header.appendChild(toast_time);
    toast_header.appendChild(toast_button);
    toast.appendChild(toast_body);
    toastcontainer.appendChild(toast);

    const timestamp = getCurrentTimestamp()
    function updateTimeSince() {;
        const timeSince = getTimeSince(timestamp);
        toast_time.innerText = timeSince;
    }

    const intervalId = setInterval(updateTimeSince, 1000);
    var bsToast = new bootstrap.Toast(toast, { autohide: autohide > 0 ? true : false, delay: autohide });
    bsToast.show();

    toast.addEventListener("hidden.bs.toast", function () {
        clearInterval(intervalId);
    });
}

function getIRCConnectionsList(ordering = [], filter = []) {
    var orderingStr = ordering.length > 0 ? "&" + ordering.join("&") : "";
    var filterStr = filter.length > 0 ? "&" + filter.join("&") : "";
    return new Promise((resolve, reject) => {
        $.ajax({
            url: URL_IRC_CONNECTIONS_LIST + orderingStr + filterStr,
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                console.error(data);
                reject(data);
            }
        });
    });
}

function getIRCConnectionDetail(id) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: URL_IRC_CONNECTIONS_DETAIL.replace("{id}", id),
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                console.error(data);
                reject(data);
            }
        });
    });
}

function getIRCChannelsList(ordering = [], filter = []) {
    var orderingStr = ordering.length > 0 ? "&" + ordering.join("&") : "";
    var filterStr = filter.length > 0 ? "&" + filter.join("&") : "";
    return new Promise((resolve, reject) => {
        $.ajax({
            url: URL_IRC_CHANNELS_LIST + orderingStr + filterStr,
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                console.error(data);
                reject(data);
            }
        });
    });
}

function getIRCChannelDetail(id) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: URL_IRC_CHANNELS_DETAIL.replace("{id}", id),
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                console.error(data);
                reject(data);
            }
        });
    });
}

function getXDCCOffersList(ordering = [], filter = []) {
    var orderingStr = ordering.length > 0 ? "&" + ordering.join("&") : "";
    var filterStr = filter.length > 0 ? "&" + filter.join("&") : "";
    return new Promise((resolve, reject) => {
        $.ajax({
            url: URL_XDCC_OFFERS_LIST + orderingStr + filterStr,
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                console.error(data);
                reject(data);
            }
        });
    });
}

function getXDCCOfferDetail(id) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: URL_XDCC_OFFERS_DETAIL.replace("{id}", id),
            type: 'GET',
            beforeSend: function (xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function(data) {
                resolve(data);
            },
            error: function(data) {
                console.error(data);
                reject(data);
            }
        });
    });
}
