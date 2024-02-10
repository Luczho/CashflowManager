from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserRegisterForm
from django.contrib import messages


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'costs_records/sign-up.html'
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
#     return render(request, 'costs_records/sign-up.html', {'form': form})