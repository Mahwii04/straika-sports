document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.slider-dot');
    let currentIndex = 0;
    let interval;
    let isAnimating = false;
    const transitionTime = 5000; // 5 seconds

    function showSlide(index) {
        if (isAnimating || index === currentIndex) return;
        
        isAnimating = true;
        
        // Fade out current slide
        slides[currentIndex].classList.remove('active');
        dots[currentIndex].classList.remove('active');
        
        // Update index
        currentIndex = index;
        
        // Fade in new slide
        setTimeout(() => {
            slides[currentIndex].classList.add('active');
            dots[currentIndex].classList.add('active');
            isAnimating = false;
        }, 600); // Match this with CSS transition time
    }

    function nextSlide() {
        const newIndex = (currentIndex + 1) % slides.length;
        showSlide(newIndex);
    }

    // Initialize slider only if slides exist
    if (slides.length > 0) {
        // Dot navigation
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                if (!isAnimating) showSlide(index);
            });
        });

        // Auto-advance with smooth transitions
        function startSlider() {
            clearInterval(interval);
            interval = setInterval(() => {
                if (!isAnimating) nextSlide();
            }, transitionTime);
        }
        
        // Pause on hover (desktop only)
        const slider = document.querySelector('.hero-slider');
        if (window.matchMedia("(hover: hover)").matches) {
            slider.addEventListener('mouseenter', () => clearInterval(interval));
            slider.addEventListener('mouseleave', startSlider);
        }

        // Touch events for mobile
        let touchStartX = 0;
        let touchEndX = 0;
        
        slider.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            clearInterval(interval);
        }, {passive: true});
        
        slider.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
            startSlider();
        }, {passive: true});
        
        function handleSwipe() {
            const diff = touchStartX - touchEndX;
            if (diff > 50 && !isAnimating) { // Swipe left
                nextSlide();
            } else if (diff < -50 && !isAnimating) { // Swipe right
                const newIndex = (currentIndex - 1 + slides.length) % slides.length;
                showSlide(newIndex);
            }
        }

        // Initialize first slide
        showSlide(0);
        startSlider();
        
        // Reset on window resize
        window.addEventListener('resize', () => {
            clearInterval(interval);
            startSlider();
        });
    }
});