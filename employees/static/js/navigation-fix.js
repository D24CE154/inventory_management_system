/**
 * Fix for navigation issues:
 * 1. Prevents showing cached authenticated pages after logout
 * 2. Prevents infinite refresh loops
 */

document.addEventListener('DOMContentLoaded', function() {
    // Special handling for login page
    if (window.location.pathname.includes('/login')) {
        // Check if we were redirected here after logout
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get("logged_out") === "True") {
            // Replace the URL to remove the parameter
            history.replaceState(null, "", "/login/");
        }

        // If this is a back navigation to login page, force refresh
        // This prevents showing cached authenticated content after logout
        if (window.performance &&
            window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
            // Check if we're coming from a logged-in state
            if (sessionStorage.getItem("wasLoggedIn") === "true") {
                sessionStorage.removeItem("wasLoggedIn");
                window.location.reload(true);
            }
        }
    }
    // For authenticated pages
    else if (document.querySelector('.dashboard-layout')) {
        // Mark that user is in logged-in area
        sessionStorage.setItem("wasLoggedIn", "true");

        // Handle "back button" for dashboards
        if (window.performance &&
            window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
            const refreshKey = `refreshed_${window.location.pathname}`;

            // Only refresh once per page path
            if (!sessionStorage.getItem(refreshKey)) {
                sessionStorage.setItem(refreshKey, "true");
                window.location.reload();
            } else {
                // Clear the flag after a delay (prevents issues if user keeps clicking back/forward)
                setTimeout(function() {
                    sessionStorage.removeItem(refreshKey);
                }, 5000);
            }
        }
    }
});