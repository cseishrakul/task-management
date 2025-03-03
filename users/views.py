from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import Group
from users.forms import RegisterForm,CustomRegisterForm,CustomPasswordChangeForm,CustomPasswordResetForm,CustomPasswordResetConfirmForm,EditProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from users.forms import LoginForm,AssignRoleForm,CreateGroupForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import LoginView,PasswordChangeView,PasswordResetView,PasswordResetConfirmView
from django.views.generic import TemplateView,UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

# Test for users
def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def sign_up(request):
    if request.method == 'GET':
        form = CustomRegisterForm()
    elif request.method == 'POST':  
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create user but don't save yet
            user.is_active = False
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            messages.success(request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
    return render(request, 'registration/register.html', context={'form': form})


def user_login(request):
    # print(request.POST)
    form = LoginForm()
    if request.method == 'POST':
        # username = request.POST.get('username')
        # password = request.POST.get('password')
        # user = authenticate(request,username=username,password=password)
        # print(username,password)
        # print(user)
        # if user is not None:
        #     login(request,user)
        #     return redirect('home')
        
        # Authentication form
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('home')
    return render(request,'registration/login.html',{'form':form})

class CustomLoginView(LoginView):
    form_class = LoginForm
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()

@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    
class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    
def activate_user(request,user_id,token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user,token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or Token!')
    
    except User.DoesNotExist:
        return HttpResponse('User not found')

@user_passes_test(is_admin,login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
            Prefetch('groups',queryset=Group.objects.all(),to_attr='all_groups')
        ).all()
    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'
    return render(request,'admin/dashboard.html',{'users':users})


@user_passes_test(is_admin,login_url='no-permission')
def assign_role(request,user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm(request.POST)
    if request.method == 'POST':
        form =AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear() # Remove old roles
            user.groups.add(role)
            messages.success(request,f'User {user.username} has been assigned to the {role.name} role')
            return redirect('admin-dashboard')
    return render(request,'admin/assigned_role.html',{'form':form})


@user_passes_test(is_admin,login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request,f'Group {group.name} has been created successfully!')
            return redirect('create-group')
    return render(request,'admin/create-group.html',{'form':form})

@user_passes_test(is_admin,login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request,'admin/group_list.html',{'groups':groups})


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

"""
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'
    def get_object(self):
        return self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['userprofile'] = UserProfile.objects.get(user=self.request.user)
        return kwargs
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['form'] = self.form_class(
            instance = self.object,userprofile = user_profile
        )
        
        return context"""
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