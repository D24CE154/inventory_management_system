/**
 * Navigation Handler
 * Handles back/forward navigation and prevents infinite refresh loops
 * while ensuring data is fresh when needed
 */

document.addEventListener('DOMContentLoaded', function() {
    // Track page visits to prevent infinite refreshes
    const currentPath = window.location.pathname;
    const currentFullPath = window.location.pathname + window.location.search;

    // Generate a unique visit ID for this page load
    const visitId = new Date().getTime();
    const visitKey = `page_visit_${currentPath}`;

    // LOGOUT DETECTION
    // If we're on the login page and were redirected after logout
    if (window.location.pathname.includes('/login') && window.location.search.includes('logged_out=True')) {
        // Clear navigation history tracking
        Object.keys(sessionStorage).forEach(key => {
            if (key.startsWith('page_visit_')) {
                sessionStorage.removeItem(key);
            }
        });

        // Clean up URL by removing the query parameter
        if (history.replaceState) {
            history.replaceState(null, document.title, window.location.pathname);
        }
    }

    // BACK NAVIGATION HANDLING
    // Check if this is a back/forward navigation
    if (performance && performance.getEntriesByType && performance.getEntriesByType('navigation').length) {
        const navType = performance.getEntriesByType('navigation')[0].type;

        if (navType === 'back_forward') {
            // This is a back/forward navigation
            const cachedVisitId = sessionStorage.getItem(visitKey);

            if (cachedVisitId) {
                // We've been to this page before
                // For authenticated pages, refresh once to get fresh data, but avoid infinite loop
                const isAuthPage = document.querySelector('.dashboard-layout') !== null;
                const refreshedKey = `refreshed_${currentFullPath}`;

                if (isAuthPage && !sessionStorage.getItem(refreshedKey)) {
                    // Mark that we've refreshed this URL
                    sessionStorage.setItem(refreshedKey, 'true');

                    // Only refresh after a short delay to ensure browser history is properly updated
                    setTimeout(() => {
                        window.location.reload();
                    }, 50);
                    return;
                }
            }
        }
    }

    // Record this visit for future reference
    sessionStorage.setItem(visitKey, visitId.toString());

    // Clear any "refreshed" flags for other pages
    Object.keys(sessionStorage).forEach(key => {
        if (key.startsWith('refreshed_') && !key.includes(currentFullPath)) {
            sessionStorage.removeItem(key);
        }
    });

    // Set flag for logout security
    if (document.querySelector('.dashboard-layout')) {
        sessionStorage.setItem('wasLoggedIn', 'true');
    }
});