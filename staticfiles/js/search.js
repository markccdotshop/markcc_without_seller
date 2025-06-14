document.addEventListener('DOMContentLoaded', function() {
    const sellerSelectElement = document.getElementById('sellerSelect');
    const baseSelectElement = document.getElementById('baseSelect');
    const urlParams = new URLSearchParams(window.location.search);
    const selectedSellerId = urlParams.get('seller');
    const selectedBaseId = urlParams.get('base');

    function populateBases(sellerId) {
        baseSelectElement.innerHTML = '<option>Loading...</option>';

        fetch(`/cvv/get_bases_for_seller/?seller_id=${encodeURIComponent(sellerId)}`)
            .then(response => response.json())
            .then(data => {
                baseSelectElement.innerHTML = '<option value="">Any</option>';
                data.forEach(base => {
                    const option = new Option(base.display, base.id);
                    baseSelectElement.appendChild(option);
                });
                if (selectedBaseId) {
                    baseSelectElement.value = selectedBaseId;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                baseSelectElement.innerHTML = '<option value="">Any</option>';
            });
    }

    sellerSelectElement.addEventListener('change', function() {
        populateBases(this.value);
    });

    if (selectedSellerId) {
        populateBases(selectedSellerId);
    }
});
