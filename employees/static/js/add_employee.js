// Toggle password visibility
function togglePassword(inputId) {
    const passwordInput = document.getElementById(inputId);
    const toggleButton = passwordInput.nextElementSibling.querySelector('i');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleButton.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize OTP timer if on OTP page
    const resendButton = document.getElementById('resend-otp');
    if (resendButton && !resendButton.disabled) {
        let countdown = 30;
        const timer = setInterval(() => {
            countdown--;
            if (countdown <= 0) {
                resendButton.textContent = 'Resend OTP';
                clearInterval(timer);
                resendButton.disabled = false;
            } else {
                resendButton.textContent = `Resend OTP (${countdown}s)`;
                resendButton.disabled = true;
            }
        }, 1000);
    }
});