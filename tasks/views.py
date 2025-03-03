from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from tasks.forms import TaskForm,TaskModelForm,TaskDetailModelForm
from tasks.models import Task,TaskDetails,Project
from datetime import date
from django.db.models import Q, Count, Min, Max, Avg
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required,permission_required
from users.views import is_admin
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView,DetailView,UpdateView,TemplateView

# Class based view re-use example
class Greetings(View):
    greetings = 'Hello Everyone'
    def get(self,request):
        return HttpResponse(self.greetings)
    
class HiGreetings(Greetings):
    greetings = 'Hi everyone!'


# Filter manager & employee
def is_manager(user):
    return user.groups.filter(name='Manager').exists()
def is_employee(user):
    return user.groups.filter(name='User').exists()


# Class based manager-dashboard
@method_decorator(user_passes_test(is_manager,login_url='no-permission'),name='dispatch')
class ManagerDashboardView(ListView):
    model = Task
    template_name = 'dashboard/manager-dashboard.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        type = self.request.GET.get('type','all')
        base_query = Task.objects.select_related('details').prefetch_related('assigned_to')
        if type == 'completed':
            tasks = base_query.filter(status='COMPLETED')
        elif type == 'in_progress':
            tasks = base_query.filter(status='IN_PROGRESS')
        if type == 'pending':
            tasks = base_query.filter(status='PENDING')
        if type == 'all':
            tasks = base_query.all()
    
    def get_context_data(self,**kwargs):
        context= super().get_context_data(**kwargs)
        context['counts'] = Task.objects.aggregate(
            total=Count('id'),
            completed = Count('id',filter=Q(status='COMPLETED')),
            in_progress = Count('id', filter=Q(status='IN_PROGRESS')),
            pending = Count('id',filter=Q(status='PENDING')),
        )        
        context['role'] = 'manager'
        return context

@method_decorator(user_passes_test(is_employee,login_url='no-permission'),name='dispatch')
class EmployeeDashboardView(TemplateView):
    template_name = 'dashboard/user-dashboard.html'

# Django Model Form
class CreateTask(ContextMixin,LoginRequiredMixin,PermissionRequiredMixin,View):
    permission_required = 'tasks.add_task'
    login_url = 'sign-in'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = kwargs.get('task_form',TaskModelForm())
        context['task_detail_form'] = kwargs.get('task_detail_form',TaskDetailModelForm())
        return context
    
    def get(self,request,*args,**kwargs):
        context = self.get_context_data()
        return render(request,'task_form.html',context)
     
    def post(self,request,*args,**kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES)
        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task=task
            task_detail.save()
            messages.success(request,'Task Created Successfully!')
        #    return redirect('create-task')
            context = self.get_context_data(task_form=task_form,task_detail_form=task_detail_form)
            return render(request,'task_form.html',context)

# class based view of update_task
class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg='id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        context['task_form'] = self.get_form()
        if hasattr(self.object,'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(instance=self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()
        return context
    
    def post(self,request,*args,**kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)
        task_detail_form=TaskDetailModelForm(request.POST,request.FILES, instance=getattr(self.object,'details',None))
        
        if task_form.is_valid() and task_detail_form.is_valid():
            task =task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request,'Task updated successfully!')
            return redirect('update-task',self.object.id)
        return redirect('update-task',self.object.id)


view_project_decorators = [login_required,permission_required('projects.view_project',login_url='no-permission')]

@method_decorator(view_project_decorators,name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'show_task.html'
    
    def get_queryset(self):
        queryset = Project.objects.annotate(num_task=Count('task'))
        return queryset    
    

class DeleteTaskView(LoginRequiredMixin,PermissionRequiredMixin,View):
    permission_required = 'tasks.delete_task'
    login_url = 'no-permission'
    
    def post(self,request,id,*args,**kwargs):
        task = get_object_or_404(Task,id=id)
        task.delete()
        messages.success(request,'Task Deleted Successfully!')
        return redirect('manager-dashboard')
    
    def get(self,request,id,*args,**kwargs):
        messages.error(request,'Something went wrong!')
        return redirect('manager-dashboard')


@login_required
@permission_required('tasks.delete_task',login_url='no-permission')
def delete_task(request,id):
    if request.method == 'POST':
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request,'Task Deleted Successfully!')
        return redirect('manager-dashboard')
    else:
        messages.error(request,'Something went wrong!')
        return redirect('manager-dashboard')
    
task_detail_decorators = [login_required,permission_required('tasks.task_details',login_url='no-permission')]

@method_decorator(task_detail_decorators,name='dispatch')

class TaskDetail(DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        context['status_choices'] = Task.STATUS_CHOICES
        return context

    def post(self,request,*args,**kwargs):
        task = self.get_object()
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details',task.id)

@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('employee-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')
    
    return redirect('no-permission')