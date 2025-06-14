$(document).ready(function() {
    function CheckCard(cardId, button) {
        $.ajax({
            url: '/orders/check/cc/' + cardId + '/',
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response) {
                var statusCell = button.closest('td');
                switch (response.status) {
                    case 'Success':
                        statusCell.html('<span class="text-info">' + response.message + '</span>');
                        if (response.new_balance !== undefined) {
                            updateBalance(parseFloat(response.new_balance));
                        }
                        break;
                    case 'TimesUp':
                        statusCell.html('<span class="text-info">' + response.message + '</span>');
                        break;
                    case 'LowFunds':
                        statusCell.html('<span class="text-warning">' + response.message + '</span>');
                        break;
                    default:
                        statusCell.html('<span class="text-danger">' + response.message + '</span>');
                }
                button.text('Check').prop('disabled', false);
            },
            error: function(xhr) {
                var errorMessage = 'Error occurred';
                try {
                    var jsonResponse = JSON.parse(xhr.responseText);
                    errorMessage = jsonResponse.message || errorMessage;
                } catch (e) {
                }
                var statusCell = button.closest('td');
                statusCell.html('<span class="text-danger">' + errorMessage + '</span>');
                button.text('Check').prop('disabled', false);
            }
        });
    }

    $(document).on('click', '.CheckButton', function() {
        var button = $(this);
        var cardId = button.data('card-id');
        CheckCard(cardId, button);
        button.text('Checking...').prop('disabled', true);
    });
});


function updateBalance(newBalance) {
    $('#userBalance').text(newBalance.toFixed(2) + ' USD'); 
}
