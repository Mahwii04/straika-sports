document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality for both admin and blog predictions
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update active tab content
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Feature prediction functionality (admin only)
    const featureButtons = document.querySelectorAll('.feature-button');
    if (featureButtons.length > 0) {
        featureButtons.forEach(button => {
            button.addEventListener('click', function() {
                const card = this.closest('.prediction-card');
                const predictionId = card.getAttribute('data-prediction-id');
                
                fetch(`/admin/predictions/feature/${predictionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.is_featured) {
                            this.innerHTML = '<i class="fas fa-star"></i> Featured';
                            card.classList.add('featured');
                        } else {
                            this.innerHTML = '<i class="far fa-star"></i> Feature';
                            card.classList.remove('featured');
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    }
    
    // Bet button animation
    const betButtons = document.querySelectorAll('.bet-button');
    betButtons.forEach(button => {
        setInterval(() => {
            button.style.boxShadow = '0 0 15px rgba(26, 115, 232, 0.7)';
            setTimeout(() => {
                button.style.boxShadow = 'none';
            }, 1000);
        }, 3000);
    });
});