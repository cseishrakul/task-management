from django import forms
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import Group,Permission
import re
from tasks.forms import StyledFormMixin
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm,PasswordResetForm,SetPasswordForm
from users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta():
        model = User
        fields = ['username','first_name','last_name','email','password','password2']
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm,self).__init__(*args, **kwargs)
        # self.fields['username'].help_text=None
        # self.fields['password'].help_text=None
        # self.fields['password2'].help_text=None
        for fieldName in ['username','password','password2']:
            self.fields[fieldName].help_text=None
            
# Model From
class CustomRegisterForm(StyledFormMixin,forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta():
        model = User
        fields = ['username','first_name','last_name','email','password']
    
    # Field Error
    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []
        if len(password) < 8:
            errors.append('Password must 8 character long')
        
        if not (re.search(r'[A-Z]', password) and 
                re.search(r'[a-z]', password) and 
                re.search(r'\d', password) and 
                re.search(r'[@#$%^&+=]', password)):
            errors.append('Password must include at least one uppercase letter, one lowercase letter, one number, and one special character')
            
        if errors:
            raise forms.ValidationError(errors)
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already exists')
        return email
    # Non-field Error
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password and confirm password didn't matched")
        return cleaned_data
    

class LoginForm(StyledFormMixin,AuthenticationForm):
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        

class AssignRoleForm(StyledFormMixin,forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label= "Select a Role"
    )
    
class CreateGroupForm(StyledFormMixin,forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Permission"
    )
    
    class Meta:
        model = Group
        fields = ['name','permissions']
        

class CustomPasswordChangeForm(StyledFormMixin,PasswordChangeForm):
    pass

class CustomPasswordResetForm(StyledFormMixin,PasswordResetForm):
    pass

class CustomPasswordResetConfirmForm(StyledFormMixin,SetPasswordForm):
    pass


"""class EditProfileForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','first_name','last_name']
    bio = forms.CharField(required=False,widget=forms.Textarea,label="Bio")
    profile_image = forms.ImageField(required=False,label="Profile Image")
    
    def __init__(self,*args,**kwargs):
        self.userprofile = kwargs.pop('userprofile',None)
        super().__init__(*args,**kwargs)
        if self.userprofile:
            self.fields['bio'].initial = self.userprofile.bio
            self.fields['profile_image'].initial = self.userprofile.profile_image
    
    def save(self,commit=True):
        user = super().save(commit=False)
        if self.userprofile:
            self.userprofile.bio = self.cleaned_data.get('bio')
            self.userprofile.profile_image = self.cleaned_data.get('profile_image')
            
            if commit:
                self.userprofile.save()
        
        if commit:
            user.save()
        
        return user"""
        
class EditProfileForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email','first_name','last_name','bio','profile_image']