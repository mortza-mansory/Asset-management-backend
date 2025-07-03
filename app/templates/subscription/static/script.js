document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('paymentModal');
    const closeBtn = document.querySelector('.close');
    const planCards = document.querySelectorAll('.plan-card');
    
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const paymentId = window.location.pathname.split('/').pop();
    
    if (!token || !paymentId) {
        alert('لینک پرداخت نامعتبر است.');
        return;
    }
    
    planCards.forEach(card => {
        card.querySelector('.select-btn').addEventListener('click', function() {
            const planType = card.dataset.plan;
            startPaymentProcess(planType);
        });
    });
    
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    async function startPaymentProcess(planType) {
        modal.style.display = 'block';
        const paymentGateway = document.getElementById('paymentGateway');
        
        paymentGateway.innerHTML = `
            <div class="loader"></div>
            <p>در حال انتقال به درگاه پرداخت...</p>
        `;
        
        try {
            // Verify payment directly using the token from URL
            const verifyResponse = await fetch(`/subscriptions/verify-payment/${paymentId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!verifyResponse.ok) {
                const errorData = await verifyResponse.json();
                throw new Error(errorData.detail || 'Failed to verify payment');
            }
            
            const verifyData = await verifyResponse.json();
            
            paymentGateway.innerHTML = `
                <h3>پرداخت با موفقیت انجام شد!</h3>
                <p>اشتراک ${getPlanName(planType)} با موفقیت فعال شد.</p>
                <button id="closeSuccess">بستن</button>
            `;
            
            document.getElementById('closeSuccess').addEventListener('click', function() {
                modal.style.display = 'none';
                window.location.href = '/subscriptions/status/me';
            });
        } catch (error) {
            paymentGateway.innerHTML = `
                <h3>خطا در پرداخت</h3>
                <p>${error.message}</p>
                <button id="closeError">بستن</button>
            `;
            document.getElementById('closeError').addEventListener('click', function() {
                modal.style.display = 'none';
            });
        }
    }
    
    function getPlanName(planType) {
        const plans = {
            '6month': '۶ ماهه',
            'yearly': 'سالانه',
            'unlimited': 'نامحدود'
        };
        return plans[planType];
    }
});