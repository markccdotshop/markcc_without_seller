$(document).ready(function() {
    $(document).on('click', '.buyButton', function(e) {
        e.preventDefault();
        var button = $(this);
        var cardId = button.data('card-id');
        button.replaceWith('<div id="processing-' + cardId + '" class="processing-text"><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span></div>');
        initiatePurchase(cardId);
    });
    $(document).on('click', '.showButton', function(e) {
        e.preventDefault();
        var cardData = $(this).data('card-data');
        $('#cardModalBody').text(cardData || 'No data available');
        $('#cardModal').modal('show');
    });

    function initiatePurchase(cardId) {
        $.ajax({
            url: '/cvv/buy/' + cardId + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response) {
                if (response.taskId) {
                    pollOrderStatus(response.taskId, cardId);
                } else {
                    $('#cardModalBody').text(response.message || 'An unexpected error occurred.');
                    $('#cardModal').modal('show');
                }
            },
            error: function() {
                $('#processing-' + cardId).replaceWith(createBuyButton(cardId));
                alert('An error occurred during the request.');
            }
        });
    }
    
    function pollOrderStatus(taskId, cardId) {
        var pollInterval = setInterval(function() {
            $.ajax({
                url: `/cvv/purchase-status/${taskId}/`,
                success: function(response) {
                    if (response.data && response.data.order_status === 'Ready') {
                        clearInterval(pollInterval);
                        var showButton = createShowButton(cardId, response.data.card_data);
                        $('#processing-' + cardId).replaceWith(showButton);
                    }
                    if(response.data.new_balance !== undefined) {
                        updateBalance(parseFloat(response.data.new_balance));
                    } 
                    else if (response.data.order_status === 'Failed') {
                        clearInterval(pollInterval);
                        $('#processing-' + cardId).replaceWith(createBuyButton(cardId));
                        alert('Order processing failed.');
                    }
                },
                error: function() {
                    clearInterval(pollInterval);
                    $('#processing-' + cardId).replaceWith(createBuyButton(cardId));
                    alert('Error polling order status.');
                }
            });
        }, 3000);
    }
    
    function createBuyButton(cardId) {
        return '<button class="btn btn-outline-success buyButton" data-card-id="' + cardId + '">Buy</button>';
    }
    
    function createShowButton(cardId, cardData) {
        return '<button type="button" class="btn btn-outline-success showButton" data-card-id="' + cardId + '" data-card-data="' + cardData + '">Show</button>';
    }
    
});