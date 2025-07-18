document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendationForm');
    const resultsDiv = document.getElementById('results');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingText = document.getElementById('loadingText');
    const tips = [
        "Diversify your portfolio across sectors.",
        "Always set stop-loss orders to manage risk.",
        "Monitor market news for timely decisions.",
        "Invest in fundamentally strong companies for long-term gains.",
        "Use technical indicators like RSI and SMA for better analysis."
    ];
    let tipIndex = 0;

    // Rotate tips during loading
    const rotateTips = () => {
        loadingText.textContent = tips[tipIndex];
        tipIndex = (tipIndex + 1) % tips.length;
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        loadingSpinner.classList.remove('d-none');
        const tipInterval = setInterval(rotateTips, 3000);
        resultsDiv.innerHTML = '';

        const formData = new FormData(form);
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        const data = {
            csrf_token: csrfToken,
            price_range: formData.get('price_range'),
            time_horizon: formData.get('time_horizon'),
            risk_level: formData.get('risk_level')
        };

        try {
            const response = await fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            clearInterval(tipInterval);
            loadingSpinner.classList.add('d-none');

            if (result.messages && result.messages.length) {
                resultsDiv.innerHTML = result.messages.map(message => `
                    <div class="alert alert-danger alert-dismissible fade show">
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `).join('');
                return;
            }

            if (!result.stocks || !result.stocks.length) {
                resultsDiv.innerHTML = '<div class="alert alert-warning">No recommendations were generated. Please try different criteria or select "None" for broader results.</div>';
                return;
            }

            const stockHtml = result.stocks.map(stock => `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${stock.name} (${stock.symbol})</h5>
                        <p class="card-text">Price: ₹${stock.price.toFixed(2)}</p>
                        <p class="card-text">Reason: ${stock.reason}</p>
                        <button class="btn btn-sm btn-outline-primary copy-btn" data-text="${stock.symbol}">Copy Symbol</button>
                        <button class="btn btn-sm btn-outline-secondary save-btn" data-stock='${JSON.stringify(stock)}'>Save</button>
                    </div>
                </div>
            `).join('');

            resultsDiv.innerHTML = `
                <h3>Recommended Stocks</h3>
                <div class="stock-recommendations">
                    ${stockHtml}
                </div>
                <div class="mt-3">
                    <button class="btn btn-secondary copy-all-btn">Copy All Results</button>
                    <button class="btn btn-secondary save-btn" data-bs-toggle="modal" data-bs-target="#savedModal">Save All Results</button>
                </div>
            `;
            addCopyAndSaveListeners();
        } catch (error) {
            clearInterval(tipInterval);
            loadingSpinner.classList.add('d-none');
            resultsDiv.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show">
                    Error fetching recommendations: ${error.message}. Please try again.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
        }
    });

    function addCopyAndSaveListeners() {
        // Copy individual symbol
        document.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', () => {
                const text = button.getAttribute('data-text');
                navigator.clipboard.writeText(text).then(() => {
                    alert('Symbol copied to clipboard!');
                });
            });
        });

        // Copy all results
        document.querySelector('.copy-all-btn').addEventListener('click', () => {
            const stockItems = document.querySelectorAll('.stock-recommendations .card');
            let textToCopy = "STOCK RECOMMENDATIONS:\n\n";
            stockItems.forEach(item => {
                const title = item.querySelector('.card-title').textContent;
                const price = item.querySelector('.card-text:nth-child(2)').textContent;
                const reason = item.querySelector('.card-text:nth-child(3)').textContent;
                textToCopy += `${title}\n${price}\n${reason}\n\n`;
            });
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert('Recommendations copied to clipboard!');
            });
        });

        // Save all results
        document.querySelector('.save-btn:not([data-stock])').addEventListener('click', () => {
            const stockItems = document.querySelectorAll('.stock-recommendations .card');
            let stocksToSave = [];
            stockItems.forEach(item => {
                const title = item.querySelector('.card-title').textContent;
                const price = item.querySelector('.card-text:nth-child(2)').textContent;
                const reason = item.querySelector('.card-text:nth-child(3)').textContent;
                stocksToSave.push({ title, price, reason });
            });
            let saved = JSON.parse(localStorage.getItem('recommendations') || '[]');
            saved.push({
                date: new Date().toLocaleString(),
                stocks: stocksToSave
            });
            localStorage.setItem('recommendations', JSON.stringify(saved));
            updateSavedRecommendations();
        });

        // Save individual stock
        document.querySelectorAll('.save-btn[data-stock]').forEach(button => {
            button.addEventListener('click', () => {
                const stock = JSON.parse(button.getAttribute('data-stock'));
                let saved = JSON.parse(localStorage.getItem('recommendations') || '[]');
                saved.push({
                    date: new Date().toLocaleString(),
                    stocks: [{
                        title: `${stock.name} (${stock.symbol})`,
                        price: `Price: ₹${stock.price.toFixed(2)}`,
                        reason: `Reason: ${stock.reason}`
                    }]
                });
                localStorage.setItem('recommendations', JSON.stringify(saved));
                updateSavedRecommendations();
            });
        });
    }

    function updateSavedRecommendations() {
        const saved = JSON.parse(localStorage.getItem('recommendations') || '[]');
        const modalBody = document.getElementById('savedRecommendations');
        modalBody.innerHTML = saved.map(item => {
            if (item.stocks) {
                const stockItems = item.stocks.map(stock => `
                    <li>${stock.title}<br>${stock.price}<br>${stock.reason}</li>
                `).join('');
                return `
                    <div class="saved-item mb-4">
                        <h5>${item.date}</h5>
                        <ul>${stockItems}</ul>
                    </div>`;
            }
        }).join('');
    }
});