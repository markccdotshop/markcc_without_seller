document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('button[name="check_balance"]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            this.textContent = 'Checking...';
            this.disabled = true;
            var billingId = this.getAttribute('data-billing-id');

            fetch('/billing/check/balance/' + billingId + '/', {
                method: 'POST',
                headers: {'X-CSRFToken': getCSRFToken()},
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.task_id) {
                    pollTaskStatus(data.task_id, this, billingId);
                } else {
                    displayMessage(data.error || 'Error occurred', false);
                    resetButton(this);
                }
            })
            .catch(error => {
                displayMessage('Failed to check', false);
                resetButton(this);
            });
        });
    });
});

function pollTaskStatus(taskId, button, billingId) {
    var intervalId = setInterval(function() {
        fetch('/billing/task-status/' + taskId)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'SUCCESS') {
                clearInterval(intervalId);
                displayMessage(data.result, true);
                if (data.result === "Payment Received!") {
                    button.textContent = 'Received';
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    resetButton(button);
                }
            } else if (data.status === 'FAILURE') {
                clearInterval(intervalId);
                displayMessage('Failed to check balance', false);
                resetButton(button);
            }
        })
        .catch(() => {
            clearInterval(intervalId);
            displayMessage('Error checking task status', false);
            resetButton(button);
        });
    }, 2000);
}



function resetButton(button) {
    button.textContent = 'Check';
    button.disabled = false;
}

function displayMessage(message, isSuccess) {
    var messageContainer = document.querySelector('.message-container');
    var messageElement = document.createElement('div');
    messageElement.className = isSuccess ? 'alert alert-success' : 'alert alert-danger';
    messageElement.textContent = message;
    messageContainer.appendChild(messageElement);
    setTimeout(() => messageElement.remove(), 5000);
}

function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}
