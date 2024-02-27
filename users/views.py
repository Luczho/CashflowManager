from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserRegisterForm, MyLoginForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import User


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'users/sign-up_form.html'
    success_url = reverse_lazy('costs-list-filter')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"


# def register(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f"Dear {username} you have been successfully signed up!")
#             return redirect('costs-list-filter')
#     else:
#         form = UserRegisterForm()
#
#     return render(request, 'users/sign-up_form.html', {'form': form})

class MyLoginView(LoginView):
    template_name = 'users/sign-in.html'
    success_url = reverse_lazy('profile')
    form_class = MyLoginForm
    success_message = "Your are successfully log in"


@login_required
@xframe_options_exempt
def profile(request):
    user = request.user
    user_group = user.groups.all()
    group_name = ', '.join([group.name for group in user_group])
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your profile's been updated!")
            return redirect('profile')

        elif profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile image has been updated!")
            return redirect('profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user': user, 'user_form': user_form, 'user_group': group_name, 'profile_form': profile_form})
