/**
 * Asynchronous AJAX Contact Form Handler
 * Validates inputs, handles honeypot spam traps, displays loading animations,
 * and communicates seamlessly with Django backend endpoints.
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    const feedback = document.getElementById('form-feedback');
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-btn-text');
    const submitIcon = document.getElementById('submit-btn-icon');

    if (!form || !submitBtn) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Honeypot spam bot check
        const honeypot = document.getElementById('website_hp');
        if (honeypot && honeypot.value.trim() !== '') {
            return;
        }

        const nameInput = document.getElementById('contact-sender-name');
        const emailInput = document.getElementById('contact-email');
        const messageInput = document.getElementById('contact-message');

        if (!nameInput || !emailInput || !messageInput) return;

        // Client-side validations
        if (nameInput.value.trim().length < 2) {
            showFeedback('Please enter a valid name (at least 2 characters).', 'error');
            nameInput.focus();
            return;
        }

        if (!emailInput.value.includes('@') || !emailInput.value.includes('.')) {
            showFeedback('Please enter a valid email address.', 'error');
            emailInput.focus();
            return;
        }

        if (messageInput.value.trim().length < 10) {
            showFeedback('Message must be at least 10 characters long.', 'error');
            messageInput.focus();
            return;
        }

        // Loading State
        submitBtn.disabled = true;
        const originalText = submitText ? submitText.textContent : 'Send Message';
        if (submitText) submitText.textContent = 'Sending...';
        if (submitIcon) submitIcon.className = 'fa-solid fa-spinner animate-spin text-xs';

        try {
            const formData = new FormData(form);
            const targetUrl = form.getAttribute('action') || '/contact/submit/';

            const response = await fetch(targetUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json().catch(() => ({}));
                const successMsg = data.message || 'Thank you! Your message has been sent successfully. I will get back to you soon!';
                showFeedback(successMsg, 'success');
                form.reset();
            } else {
                const errorData = await response.json().catch(() => ({}));
                let errorMsg = 'An error occurred while sending your message. Please try again.';
                if (errorData.errors) {
                    const firstErrorKey = Object.keys(errorData.errors)[0];
                    if (firstErrorKey && errorData.errors[firstErrorKey].length > 0) {
                        errorMsg = errorData.errors[firstErrorKey][0];
                    }
                }
                showFeedback(errorMsg, 'error');
            }
        } catch (err) {
            showFeedback('Network error. Please check your connection and try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            if (submitText) submitText.textContent = originalText;
            if (submitIcon) submitIcon.className = 'fa-solid fa-paper-plane text-xs';
        }
    });

    function showFeedback(message, type) {
        if (!feedback) return;
        feedback.classList.remove('hidden');
        if (type === 'success') {
            feedback.className = 'p-4 rounded-xl text-sm font-medium flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400';
            feedback.innerHTML = `<i class="fa-solid fa-circle-check text-base"></i> <span>${message}</span>`;
        } else {
            feedback.className = 'p-4 rounded-xl text-sm font-medium flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400';
            feedback.innerHTML = `<i class="fa-solid fa-circle-exclamation text-base"></i> <span>${message}</span>`;
        }
    }
});
