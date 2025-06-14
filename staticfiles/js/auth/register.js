$(document).ready(function() {
    function refreshCaptcha() {
        $.getJSON('/auth/captcha/refresh/', function(json) {
            var newCaptchaSrc = json.image_url + '?_=' + new Date().getTime();
            $('img.captcha').attr('src', newCaptchaSrc);
            $('input[name="captcha_0"]').val(json.key);
        });
    }
    $('#button-captcha-refresh').click(function(event) {
        event.preventDefault();
        refreshCaptcha();
    });

    $('#registration-form').submit(function(e) {
        e.preventDefault(); 

        var formData = new FormData(this);

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function(response) {
                alert(response.message);
                window.location.href = response.redirect_url;
            },
            error: function(xhr) {
                
                $('.form-control').removeClass('is-invalid');
                $('.error-message').remove();

                var errors = xhr.responseJSON.errors;
                $.each(errors, function(field, message) {
                    if (field === 'password1' || field === 'password2') {
                        var input = $('#id_' + field); 
                        input.addClass('is-invalid').after('<div class="error-message text-danger">' + message + '</div>');
                    }
                    else if (field === 'captcha') {
                        var captchaInput = $('[name=' + field + '_0]');
                        captchaInput.addClass('is-invalid').closest('.input-group').after('<div class="error-message text-danger">' + message + '</div>');
                    } else {
                        var input = $('[name=' + field + ']');
                        input.addClass('is-invalid').after('<div class="error-message text-danger">' + message + '</div>');
                    }
                });
            }
        });
    });
});
