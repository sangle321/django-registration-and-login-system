from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import LoginForm, RegisterForm
from django.contrib.auth import get_user_model

def home(request):
    return render(request, 'users/home.html')



class CustomLoginView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user=False
    template_name='users/login.html'   
    authentication_form=LoginForm
    
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)

    def get_success_url(self):
        # Customize the redirect URL here
        return reverse_lazy('users-home')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        User = get_user_model()
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            # If the email doesn't exist or is not active, show an error message
            messages.error(self.request, 'Invalid email address.')
            return self.form_invalid(form)
        return super().form_valid(form)




