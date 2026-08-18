/**
 * Main Application Script for Portfolio UI Kit
 * Handles: Mouse Glow Tracking, Scroll Reveal, Mobile Navigation, and Smooth Scrolling
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mouse Glow Effect Tracking
    const mouseGlow = document.getElementById('mouse-glow');
    if (mouseGlow) {
        window.addEventListener('mousemove', (e) => {
            mouseGlow.style.setProperty('--mouse-x', `${e.clientX}px`);
            mouseGlow.style.setProperty('--mouse-y', `${e.clientY}px`);
        });
    }

    // 2. Scroll Reveal Observer with IntersectionObserver
    const revealElements = document.querySelectorAll('.reveal');
    const observerOptions = {
        root: null,
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    };

    const revealOnScroll = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    revealElements.forEach(el => revealOnScroll.observe(el));

    // 3. Mobile Navigation Menu Toggle
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            if (menuIcon) {
                if (menuIcon.classList.contains('fa-bars')) {
                    menuIcon.classList.remove('fa-bars');
                    menuIcon.classList.add('fa-xmark');
                } else {
                    menuIcon.classList.remove('fa-xmark');
                    menuIcon.classList.add('fa-bars');
                }
            }
        });

        // Close mobile menu when a navigation link is clicked
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                if (menuIcon) {
                    menuIcon.classList.remove('fa-xmark');
                    menuIcon.classList.add('fa-bars');
                }
            });
        });
    }
});
