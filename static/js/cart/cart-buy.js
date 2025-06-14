
      
      function getCsrfToken() {
        return document.cookie.split('; ')
          .find(row => row.startsWith('csrftoken'))
          ?.split('=')[1];
      }
    
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
          }
        }
      });
    
      function buyAll() {
        const cardIds = Array.from(document.querySelectorAll('.cart-item')).map(item => item.dataset.cardId);
        
        if (cardIds.length === 0) {
          showFlashMessage('No items in your cart.', 'error');
          return;
        }
    
        $.ajax({
          url: '/cart/buycc/',
          type: 'POST',
          data: {
            'card_ids[]': cardIds
          },
          success: function(response) {
            showFlashMessage(response.message, response.status);
            window.setTimeout(function(){ location.reload(); }, 3000);
          },
          error: function(xhr, status, error) {
            showFlashMessage('Error buying cards: ' + xhr.responseText, 'error');
          }
        });
      }
    
      function showFlashMessage(message, type) {
        var flashMessage = document.getElementById('flash-message');
        flashMessage.textContent = message;
        
        flashMessage.classList.remove('alert-success', 'alert-warning', 'alert-danger', 'hidden');
        
        switch (type) {
            case 'success':
                flashMessage.classList.add('alert-success');
                break;
            case 'warning':
                flashMessage.classList.add('alert-warning');
                break;
            case 'error':
                flashMessage.classList.add('alert-danger');
                break;
            default:
                flashMessage.classList.add('alert-info');
        }
    
        
        flashMessage.style.display = 'block';
    
        setTimeout(function() {
            flashMessage.classList.add('hidden');
        }, 10000);
    }
    
      document.addEventListener('DOMContentLoaded', function() {
        const buyAllButton = document.querySelector('.buy-all-btn');
        if (buyAllButton) {
          buyAllButton.addEventListener('click', buyAll);
        }
      });