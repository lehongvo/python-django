/**
 * TechStore 2025 - 3D Effects JavaScript
 * Mouse tracking and 3D animations
 */

(function() {
    'use strict';

    // Initialize 3D tilt effect on product cards
    function init3DTilt() {
        const cards = document.querySelectorAll('.product-card-3d, .card-tilt-3d');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;
                
                card.style.transform = `perspective(1000px) rotateX(${-rotateX}deg) rotateY(${rotateY}deg) translateZ(20px)`;
            });
            
            card.addEventListener('mouseleave', function() {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0)';
            });
        });
    }

    // Initialize parallax effect
    function initParallax() {
        const parallaxElements = document.querySelectorAll('.parallax-3d, .parallax-3d-slow');
        
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const rate = scrolled * (element.classList.contains('parallax-3d-slow') ? 0.2 : 0.5);
                element.style.transform = `translateY(${rate}px)`;
            });
        });
    }

    // Intersection Observer for stagger animations
    function initStaggerAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'perspective(1000px) translateZ(0) rotateX(0deg)';
                }
            });
        }, observerOptions);

        document.querySelectorAll('.stagger-3d-in, [class*="stagger-3d-in-"]').forEach(el => {
            observer.observe(el);
        });
    }

    // 3D carousel rotation effect
    function init3DCarousel() {
        const carousel = document.getElementById('productCarousel');
        if (!carousel) return;

        let currentRotation = 0;
        const items = carousel.querySelectorAll('.carousel-item');
        
        setInterval(function() {
            currentRotation += 2;
            if (currentRotation >= 360) currentRotation = 0;
            
            items.forEach((item, index) => {
                if (item.classList.contains('active')) {
                    const offset = (index * 360 / items.length) + currentRotation;
                    item.style.transform = `perspective(1200px) rotateY(${offset % 360}deg) translateZ(30px)`;
                }
            });
        }, 100);
    }

    // Initialize all 3D effects when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            init3DTilt();
            initParallax();
            initStaggerAnimations();
            init3DCarousel();
        });
    } else {
        init3DTilt();
        initParallax();
        initStaggerAnimations();
        init3DCarousel();
    }

    // Smooth scroll with 3D effect
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add 3D glow effect on button hover
    document.querySelectorAll('.btn-3d').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'perspective(800px) translateZ(20px) rotateX(-5deg)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(800px) translateZ(0)';
        });
    });

})();

