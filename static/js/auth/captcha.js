$(document).ready(function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function refreshCaptcha() {
        $.getJSON('/auth/captcha/refresh/', function(json) {
            $('img.captcha').attr('src', json.image_url);
            $('input[name="captcha_0"]').val(json.key);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log('Failed to refresh CAPTCHA: ');
        });
    }

    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    $(".form-check").html('<p class="text-danger">' + response.error + '</p>');
                    refreshCaptcha();
                }
            },
            error: function(xhr, status, error) {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    $('.form-check').html('<p class="text-danger">' + xhr.responseJSON.error + '</p>');
                } else {
                    $('.form-check').html('<p class="text-danger">An error occurred. Please try again.</p>');
                }
                refreshCaptcha();
            }
        });
    });

    
    $(document).on('click', '.js-captcha-refresh', function() {
        refreshCaptcha(); 
        return false;
    });
    
    refreshCaptcha();
});
