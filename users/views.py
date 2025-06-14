from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db import DatabaseError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from .forms import SignUpForm,CaptchaForm
from .utils import get_active_users

def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                auth_login(request, user)  # Log the user in directly after registration
                return JsonResponse({
                    'success': True,
                    'message': f'Account created for {user.username}! You are now logged in.',
                    'redirect_url': reverse('index')  # Adjust the redirect URL as needed
                }, status=200)
            else:
                errors = {}
                # Iterate over form errors
                for field, field_errors in form.errors.items():
                    # Assign the first error message to the field
                    errors[field] = field_errors[0]

                    # Special case for handling password errors
                    if 'password1' in form.errors:
                        errors['password1'] = form.errors['password1'][0]
                    if 'password2' in form.errors:
                        # Check if 'password1' is also in errors, if not, add the 'password2' error to 'password1' instead
                        if 'password1' not in errors:
                            errors['password1'] = form.errors['password2'][0]
                        else:
                            errors['password2'] = form.errors['password2'][0]

            return JsonResponse({'errors': errors}, status=400)
        except DatabaseError as e:
            # Handle database errors
            return JsonResponse({'success': False, 'error': "An error occurred. Please try again later!"}, status=500)
        except ValidationError as e:
            # Handle specific validation errors
            return JsonResponse({'success': False, 'error': "An error occurred. Please try again later!"}, status=400)
        except Exception as e:
            # Handle any other exceptions
            return JsonResponse({'success': False, 'error': "An unexpected error occurred!"}, status=500)
    
    else:
        form = SignUpForm()
    return render(request, 'auth/register.html', {'form': form})




def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        formcaptcha = CaptchaForm(request.POST)

        try:
            if formcaptcha.is_valid():
                username = request.POST.get('username')
                password = request.POST.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    next_page = request.POST.get('next', '/')
                    if url_has_allowed_host_and_scheme(next_page, allowed_hosts=settings.ALLOWED_HOSTS):
                        return JsonResponse({'success': True, 'redirect_url': next_page})
                    else:
                        return JsonResponse({'success': True, 'redirect_url': '/'})
                else:
                    return JsonResponse({'success': False, 'error': "Username or password is incorrect!"}, status=400)
            else:
                return JsonResponse({'success': False, 'error': "Captcha is incorrect!"}, status=400)
            
        except DatabaseError as e:
            # Handle database errors
            return JsonResponse({'success': False, 'error': "An error occurred. Please try again later!"}, status=500)
        except ValidationError as e:
            # Handle specific validation errors
            return JsonResponse({'success': False, 'error': "An error occurred. Please try again later!"}, status=400)
        except Exception as e:
            # Handle any other exceptions
            return JsonResponse({'success': False, 'error': "An unexpected error occurred!"}, status=500)
            
    else:
        formcaptcha = CaptchaForm()
    return render(request, 'auth/login.html', {'formcaptcha': formcaptcha})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get("q_Old_Password")
        new_password = request.POST.get("q_new_Password")
        confirmed_new_password = request.POST.get("q_confirm_new_Password")

        if old_password and new_password and confirmed_new_password:
            if request.user.is_authenticated:
                try:
                    user = User.objects.get(username=request.user.username)
                except User.DoesNotExist:
                    messages.error(request, "User does not exist.")
                    return redirect('login')

                if not user.check_password(old_password):
                    messages.error(request, "Your old password is not correct!")
                elif new_password != confirmed_new_password:
                    messages.error(request, "Your new password does not match the confirm password!")
                elif len(new_password) < 8 or new_password.lower() == new_password or \
                     new_password.upper() == new_password or new_password.isalnum() or \
                     not any(i.isdigit() for i in new_password):
                    messages.error(request, "Your password is too weak!")
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)

                    messages.success(request, "Your password has been changed successfully!")

                    return redirect('change/password')
            else:
                messages.error(request, "You need to be logged in to change your password.")
                return redirect('login')
        else:
            messages.error(request, "Sorry, all fields are required!")

    context = {}
    return render(request, "auth/change_password.html", context)

@staff_member_required
def active_users_view(request):
    # Call the utility function to get active users
    active_users = get_active_users()
    # Pass the active users to the template
    return render(request, 'active_users.html', {'active_users': active_users})

