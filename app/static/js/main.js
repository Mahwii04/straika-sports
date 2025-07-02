document.addEventListener('DOMContentLoaded', function() {
    // Set default to light mode
    const defaultTheme = 'light';
    const themeToggle = document.querySelector('.theme-switcher');
    
    // Function to set theme with expiry
    function setTheme(theme, persist = true) {
        document.body.classList.toggle('dark-mode', theme === 'dark');
        themeToggle.innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        
        if (persist) {
            const expiryDate = new Date();
            expiryDate.setTime(expiryDate.getTime() + (30 * 60 * 1000)); // 30 minutes
            document.cookie = `theme=${theme}; expires=${expiryDate.toUTCString()}; path=/`;
        }
    }
    
    // Function to get theme from cookie
    function getTheme() {
        const cookies = document.cookie.split(';').map(c => c.trim());
        const themeCookie = cookies.find(c => c.startsWith('theme='));
        return themeCookie ? themeCookie.split('=')[1] : null;
    }
    
    // Initialize theme
    const savedTheme = getTheme();
    setTheme(savedTheme || defaultTheme, false);
    
    // Toggle theme on button click
    themeToggle.addEventListener('click', function() {
        const isDark = document.body.classList.contains('dark-mode');
        setTheme(isDark ? 'light' : 'dark');
    });
});



// Check for saved user preference or use system preference
const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'dark') {
    document.body.classList.add('dark-mode');
} else if (currentTheme === 'light') {
    document.body.classList.remove('dark-mode');
} else if (prefersDarkScheme.matches) {
    document.body.classList.add('dark-mode');
}

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
});

// Mobile Menu Toggle (for smaller screens)
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
}

// Hero Slider
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.slider-dot');
    let currentSlide = 0;
    
    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        currentSlide = index;
    }
    
    function nextSlide() {
        let newIndex = (currentSlide + 1) % slides.length;
        showSlide(newIndex);
    }
    
    // Set up dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
        });
    });
    
    // Auto-advance slides every 5 seconds
    setInterval(nextSlide, 5000);
    
    // Initialize first slide
    showSlide(0);
});

// Bet button animation
const betButton = document.querySelector('.bet-button');
if (betButton) {
    setInterval(() => {
        betButton.style.boxShadow = '0 0 15px rgba(26, 115, 232, 0.7)';
        setTimeout(() => {
            betButton.style.boxShadow = 'none';
        }, 1000);
    }, 3000);
}

// Flash message functionality
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash');
    
    flashMessages.forEach(flash => {
        // Add close button functionality
        const closeBtn = flash.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                flash.classList.add('fade-out');
                setTimeout(() => flash.remove(), 300);
            });
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            flash.classList.add('fade-out');
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Process YouTube embeds
    document.querySelectorAll('.embed-responsive iframe[src*="youtube.com"], .embed-responsive iframe[src*="youtu.be"]').forEach(iframe => {
        // Ensure iframe has proper attributes
        iframe.setAttribute('allowfullscreen', '');
        iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
    });

    // Process Twitter embeds
    document.querySelectorAll('.twitter-embed').forEach(embed => {
        const url = embed.textContent.trim();
        if (url.includes('twitter.com')) {
            // Replace with Twitter's embed script
            const script = document.createElement('script');
            script.src = 'https://platform.twitter.com/widgets.js';
            script.charset = 'utf-8';
            script.async = true;
            
            const blockquote = document.createElement('blockquote');
            blockquote.className = 'twitter-tweet';
            const anchor = document.createElement('a');
            anchor.href = url;
            blockquote.appendChild(anchor);
            
            embed.innerHTML = '';
            embed.appendChild(blockquote);
            document.body.appendChild(script);
        }
    });

    // Process Vimeo embeds
    document.querySelectorAll('.embed-responsive iframe[src*="vimeo.com"]').forEach(iframe => {
        iframe.setAttribute('allowfullscreen', '');
    });
});