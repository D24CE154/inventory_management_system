/**
 * Auto-hide popup messages after a delay
 * @param {string} containerId - The ID of the popup message container
 * @param {number} delay - Time in milliseconds before hiding the popup (default: 5000ms)
 */
function autoHidePopup(containerId, delay = 5000) {
    const popup = document.getElementById(containerId);
    if (popup) {
        setTimeout(() => {
            popup.style.opacity = "0";
            setTimeout(() => {
                popup.style.display = "none";
            }, 500);
        }, delay);
    }
}

// Call the function after DOM content is loaded
document.addEventListener("DOMContentLoaded", function() {
    autoHidePopup("message-container");
});
