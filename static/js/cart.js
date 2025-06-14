document.addEventListener('DOMContentLoaded', function () {
    var addToCartButton = document.getElementById('addToCartButton');
    var selectAllCheckbox = document.getElementById('selectAllCheckboxes');
    var individualCheckboxes = document.querySelectorAll('.individual-checkbox');
    var flashMessage = document.getElementById('flashMessage');

    function updateAddToCartButtonVisibility() {
        var isAnyCheckboxChecked = Array.from(individualCheckboxes).some(checkbox => checkbox.checked);
        addToCartButton.style.display = isAnyCheckboxChecked ? 'block' : 'none';
    }

    function fetchAndUpdateCartCount() {
        $.ajax({
            url: '/cart/count/',
            type: 'GET',
            success: function(response) {
                updateCartCount(response.cart_count);
            },
            error: function(error) {
                console.error('Error fetching cart count');
            }
        });
    }

    function updateCartCount(newCount) {
        var cartCountElement = document.getElementById('cartCount');
        cartCountElement.textContent = newCount;
    }

    selectAllCheckbox.addEventListener('change', function () {
        individualCheckboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateAddToCartButtonVisibility();
    });

    individualCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            updateAddToCartButtonVisibility();
        });
    });

    addToCartButton.addEventListener('click', function() {
        var selectedCardIds = Array.from(individualCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        $.ajax({
            url: '/cart/add/',
            type: 'POST',
            headers: {'X-CSRFToken': getCsrfToken()},
            data: {'card_ids[]': selectedCardIds},
            success: function(response) {
                handleAddToCartResponse(response, selectedCardIds);
            },
            error: function(error) {
                showFlashMessage(error.responseJSON.message, 'error');
            }
        });
    });

    function handleAddToCartResponse(response, selectedCardIds) {
        const { cart_count, unavailable_ids = [], over_limit_ids = [], message, status } = response;

        updateCartCount(cart_count);
        showFlashMessage(message, status);
        updateCheckboxStates(selectedCardIds, unavailable_ids, over_limit_ids);
    }

    function updateCheckboxStates(selectedIds, unavailableIds, overLimitIds) {
        unavailableIds = unavailableIds.map(String);
        overLimitIds = overLimitIds.map(String);

        selectedIds.forEach(id => {
            var checkbox = document.querySelector(`.individual-checkbox[value="${id}"]`);
            if (checkbox) {
                var tdElement = checkbox.closest('td');
                if (unavailableIds.includes(id)) {
                    tdElement.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle-fill"></i> Unavailable</span>';
                } else if (overLimitIds.includes(id)) {
                    tdElement.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-triangle-fill"></i> Limit Exceeded</span>';
                } else {
                    tdElement.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill"></i> Added</span>';
                }
            }
        });
    }

    function getCsrfToken() {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showFlashMessage(message, status) {
        flashMessage.textContent = message;
        flashMessage.className = 'flash-message ' + (status === 'error' ? 'error' : 'success');
        flashMessage.style.display = 'block';
        setTimeout(() => flashMessage.style.display = 'none', 3000);
    }
});
