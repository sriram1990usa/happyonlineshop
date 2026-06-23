from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, TemplateView, UpdateView
from django.utils.decorators import method_decorator
from .models import User, Profile, Address
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, AddressForm


class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, self.template_name, {'form': UserRegistrationForm()})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome notification/email
            try:
                from notifications.services import NotificationService
                NotificationService.send_notification(
                    user=user,
                    notification_type='OFFER',
                    title="Welcome to PremiumShop AI! ⚡",
                    message=f"Hi {user.first_name or 'there'},\n\nThank you for registering at PremiumShop AI! Your account is active and you are ready to explore and shop premium items.\n\nEnjoy your premium shopping experience!\n\nThe PremiumShop AI Team"
                )
            except Exception:
                pass

            login(request, user)
            messages.success(request, f'Welcome to PremiumShop AI, {user.email}!')
            return redirect('core:home')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, self.template_name, {'form': UserLoginForm()})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                # Merge session cart on login
                from cart.services import CartService
                CartService.merge_session_cart_to_user(request, user)
                next_url = request.GET.get('next', 'core:home')
                messages.success(request, 'Welcome back!')
                return redirect(next_url)
            else:
                form.add_error(None, 'Invalid email or password.')
                messages.error(request, 'Invalid email or password.')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been signed out.')
        return redirect('core:home')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class AddressListView(View):
    template_name = 'accounts/addresses.html'

    def get(self, request):
        addresses = request.user.addresses.all()
        return render(request, self.template_name, {'addresses': addresses, 'form': AddressForm()})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added.')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:addresses')
        addresses = request.user.addresses.all()
        return render(request, self.template_name, {'addresses': addresses, 'form': form})


@method_decorator(login_required, name='dispatch')
class DeleteAddressView(View):
    def post(self, request, pk):
        get_object_or_404(Address, pk=pk, user=request.user).delete()
        messages.success(request, 'Address removed.')
        return redirect('accounts:addresses')
