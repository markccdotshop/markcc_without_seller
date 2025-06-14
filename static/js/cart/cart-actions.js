document.addEventListener('DOMContentLoaded', function() {
  const removeItemButtons = document.querySelectorAll('.remove-item-btn');
  const removeAllButton = document.querySelector('.remove-all-btn');
  const removeAllModal = new bootstrap.Modal(document.getElementById('removeAllConfirmModal'));

 
  if (removeAllButton) {
    removeAllButton.addEventListener('click', function() {
      removeAllModal.show();
    });
  }

  document.getElementById('confirmRemoveAll').addEventListener('click', function() {
      $.ajax({
          url: '/cart/remove_all/',
          type: 'GET',
          success: function(response) {
              console.log('All items removed successfully');
              window.location.reload();
          },
          error: function(error) {
              console.error('Error removing all items:', error);
          }
      });
  });

  function removeItem(itemId) {
    $.ajax({
      url: `/cart/remove/${itemId}/`,
      type: 'GET',
      success: function(response) {
        console.log('Item removed successfully');
        window.location.reload();
        document.querySelector(`button[data-item-id="${itemId}"]`).closest('tr').remove();
        updateCartCount();
      },
      error: function(error) {
        console.error('Error removing item:', error);
      }
    });
  }
  removeItemButtons.forEach(button => {
    button.addEventListener('click', () => {
      const itemId = button.getAttribute('data-item-id');
      removeItem(itemId);
    });
  });
  

  function updateCartCount() {
    const cartCountElement = document.querySelector('#cartCount');
    let currentCount = parseInt(cartCountElement.textContent);
    cartCountElement.textContent = currentCount > 0 ? currentCount - 1 : 0;
  }




});
