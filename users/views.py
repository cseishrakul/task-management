from django.shortcuts import redirect,HttpResponse,get_object_or_404
from django.contrib.auth.models import Group
from users.forms import CustomRegisterForm,CustomPasswordChangeForm,CustomPasswordResetForm,CustomPasswordResetConfirmForm,EditProfileForm
from django.contrib import messages
from django.contrib import messages
from users.forms import LoginForm,AssignRoleForm,CreateGroupForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView,PasswordChangeView,PasswordResetView,PasswordResetConfirmView
from django.views.generic import TemplateView,UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic.edit import FormView,View,CreateView
from django.views.generic import ListView
from django.utils.decorators import method_decorator

User = get_user_model()

# Create your views here.

# Test for users
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

class SignUpView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomRegisterForm
    success_url = 'sign-in'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(self.request,'A confirmation mail sent.Please check your email!')
        return redirect(self.success_url)
    

class CustomLoginView(LoginView):
    form_class = LoginForm
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()
    
class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    

class ActivateUserView(View):
    def get(self, request, user_id, token, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('sign-in')
            else:
                return HttpResponse('Invalid Id or Token!')
        except User.DoesNotExist:
            return HttpResponse('User not found')

@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class AdminDashboardView(ListView):
    model = User
    template_name = 'admin/dashboard.html'
    context_object_name = 'users'

    def get_queryset(self):
        users = User.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
        ).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = 'No Group Assigned'

        return users


@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class AssignRoleView(FormView):
    template_name = 'admin/assigned_role.html'
    form_class = AssignRoleForm
    success_url = reverse_lazy('admin-dashboard')

    def form_valid(self, form):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        role = form.cleaned_data.get('role')
        user.groups.clear()
        user.groups.add(role)

        messages.success(self.request, f'User {user.username} has been assigned to the {role.name} role')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_object_or_404(User, id=self.kwargs['user_id'])
        return context


@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class CreateGroupView(CreateView):
    form_class = CreateGroupForm
    template_name = 'admin/create-group.html'
    success_url = reverse_lazy('create-group')
    def form_valid(self, form):
        response = super().form_valid(form)
        group = form.save()
        messages.success(self.request, f'Group {group.name} has been created successfully!')
        return response

@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class GroupListView(ListView):
    model = Group
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'
    queryset = Group.objects.prefetch_related('permissions').all()

    def get_queryset(self):
        return self.queryset


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["username"] = user.username
        context["email"] = user.email
        context["name"] = user.get_full_name()
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["protocol"] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        return context
    
    
    def form_valid(self, form):
        messages.success(
            self.request,'A reset email sent. Please check your email!'
        )
        return super().form_valid(form)


class CustomPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    
    def form_valid(self, form):
        messages.success(
            self.request,'Password reset successfully!'
        )
        return super().form_valid(form)

class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self,form):
        form.save()
        return redirect('profile')