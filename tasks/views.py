from django.shortcuts import render,redirect
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
from django.views.generic import ListView,DetailView,UpdateView

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

# For Homepage
def index(request):
    names = ['Efaz','Deep','Alavi']
    count = 0
    for name in names:
        count +=1
    context = {
        'names':names,
        'count':count
    }
    return render(request,'test.html',context)

@user_passes_test(is_manager,login_url='no-permission')
def manager_dashboard(request):
    # total_task = tasks.count()
    # completed_task = Task.objects.filter(status='COMPLETED').count()
    # in_progress_task = Task.objects.filter(status='IN_PROGRESS').count()
    # pending_task = Task.objects.filter(status='PENDING').count()
    # context={
    #     'tasks':tasks,
    #     'total_task':total_task,
    #     'completed_task':completed_task,
    #     'in_progress_task':in_progress_task,
    #     'pending_task':pending_task
    # }
    
    type = request.GET.get('type','all')
    base_query = Task.objects.select_related('details').prefetch_related('assigned_to')
    
    if type == 'completed':
        tasks = base_query.filter(status='COMPLETED')
    elif type == 'in_progress':
        tasks = base_query.filter(status='IN_PROGRESS')
    if type == 'pending':
        tasks = base_query.filter(status='PENDING')
    if type == 'all':
        tasks = base_query.all()
    
    counts = Task.objects.aggregate(
        total=Count('id'),
        completed = Count('id',filter=Q(status='COMPLETED')),
        in_progress = Count('id',filter=Q(status='IN_PROGRESS')),
        pending = Count('id',filter=Q(status='PENDING')),
        )
    
    context = {
        'tasks':tasks,
        'counts':counts,
        'role':'manager'
    }
    
    return render(request,"dashboard/manager-dashboard.html",context)

@user_passes_test(is_employee,login_url='no-permission')
def employee_dashboard(request):
    return render(request,"dashboard/user-dashboard.html")
# Used for django form
# def create_task(request):
#     employees = Employee.objects.all()
#     form = TaskForm(employees=employees) # For get method
#     if request.method == 'POST':
#         form = TaskForm(request.POST,employees = employees)
#         print(form)
#         if form.is_valid():
#             # print(form.cleaned_data)
#             data = form.cleaned_data
#             title = data.get('title')
#             description = data.get('description')
#             due_date = data.get('due_date')
#             assigned_to = data.get('assigned_to')
#             task = Task.objects.create(
#                 title = title, description = description, due_date = due_date
#             )
            
#             # Assign employees to tasks
#             for emp_id in assigned_to:
#                 employee = Employee.objects.get(id=emp_id)
#                 task.assigned_to.add(employee) 
#             return HttpResponse('Task Added Successfully!')
#     context = {'form':form}
#     return render(request,'task_form.html',context)

# Django Model Form

@login_required
@permission_required('tasks.add_task',login_url='no-permission')
def create_task(request):
    task_form = TaskModelForm() # For get method
    task_detail_form = TaskDetailModelForm() # For get method
    if request.method == 'POST':
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES)
        if task_form.is_valid() and task_detail_form.is_valid():
           task = task_form.save()
           task_detail = task_detail_form.save(commit=False)
           task_detail.task=task
           task_detail.save()
           messages.success(request,'Task Created Successfully!')
           return redirect('create-task')
    context = {'task_form':task_form,'task_detail_form':task_detail_form}
    return render(request,'task_form.html',context)

# Variable for permission required
# create_decorators = [login_required,permission_required('tasks.add_task',login_url='no-permission')]
# @method_decorator(create_decorators,name='dispatch')

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
@login_required
@permission_required('tasks.change_task',login_url='no-permission')
def update_task(request,id):
    task = Task.objects.get(id=id)
    task_form = TaskModelForm(instance=task) # For get method
    if task.details:
        task_detail_form = TaskDetailModelForm(instance=task.details) # For get method
    if request.method == 'POST':
        task_form = TaskModelForm(request.POST,instance=task)
        task_detail_form = TaskDetailModelForm(request.POST,instance=task.details)
        if task_form.is_valid() and task_detail_form.is_valid():
           task = task_form.save()
           task_detail = task_detail_form.save(commit=False)
           task_detail.task=task
           task_detail.save()
           messages.success(request,'Task Updated Successfully!')
           return redirect('update-task',id)
    context = {'task_form':task_form,'task_detail_form':task_detail_form}
    return render(request,'task_form.html',context)

# class based view of update_task
class UpdateTask2(View):
    def get(self,request,*args,**kwargs):
        task_id = kwargs.get('id')
        task = Task.objects.get(id=task_id)
        task_form = TaskModelForm(instance=task)
        if task.details:
            task_detail_form = TaskDetailModelForm(instance=task.details)
        context = {'task_form':task_form,'task_detail_form':task_detail_form}
        return render(request,'task_form.html',context)
            
    def post(self,request,*args,**kwargs):
        task_id = kwargs.get('id')
        task = Task.objects.get(id=task_id)
        task_form = TaskModelForm(request.POST,instance=task)
        task_detail_form = TaskDetailModelForm(request.POST,instance=task.details)
        if task_form.is_valid() and task_detail_form.is_valid():
           task = task_form.save()
           task_detail = task_detail_form.save(commit=False)
           task_detail.task=task
           task_detail.save()
           messages.success(request,'Task Updated Successfully!')
           return redirect('update-task',id=task_id)    


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


# def view_task(request):
#     # tasks = Task.objects.all()
#     # task3 = Task.objects.get(id=3)
#     # f_task = Task.objects.first()
#     # return render(request,'show_task.html',context={'tasks':tasks,'task3':task3,'f_task':f_task})
    
#     # Filter
#     # tasks = Task.objects.filter(status='PENDING') # filter by status
#     # tasks = Task.objects.filter(due_date =date.today()) # filter by date
    
#     # filter by exlude priority low
#     # tasks = TaskDetails.objects.exclude(priority = 'L')
    
#     """ Show the task that contain word 'paper' """
#     # tasks = Task.objects.filter(title__icontains='c',status='PENDING')
    
#     """ Show the task which are pending or in-progress """
#     # tasks = Task.objects.filter(Q(status='PENDING') | Q(status='IN_PROGRESS'))
#     tasks = Task.objects.filter(status='PENDING').exists()
#     return render(request,'show_task.html',context={'tasks':tasks})

# Related Data Queries
# def view_task(request):
#     # select_related (ForeignKey, OneToOneField)
#     # tasks = Task.objects.all()
#     # tasks = Task.objects.select_related('details').all()
#     # tasks = TaskDetails.objects.select_related('task').all()
#     tasks = Task.objects.select_related('project').all()
    
#     """ prefetch_related (Reverse Foreignkey, Manytomany)"""
#     # tasks = Project.objects.prefetch_related('task_set').all()
#     tasks = Task.objects.prefetch_related('assigned_to').all()
#     return render(request,'show_task.html',context={'tasks':tasks})

# Aggregants (Min, Max)


@login_required
@permission_required('tasks.view_task',login_url='no-permission')
def view_task(request):
    # task_count = Task.objects.aggregate(num_task=Count('id'))
    task_count = Project.objects.annotate(num_task=Count('task'))
    return render(request,'show_task.html',{'task_count':task_count})

view_project_decorators = [login_required,permission_required('projects.view_project',login_url='no-permission')]

@method_decorator(view_project_decorators,name='dispatch')
class ViewProject(ListView):
    model = Project
    context_object_name = 'projects'
    template_name = 'show_task.html'
    
    def get_queryset(self):
        queryset = Project.objects.annotate(num_task=Count('task'))
        return queryset    
    


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
    
@login_required
@permission_required('tasks.view_task',login_url='no-permission')
def task_details(request,task_id):
    task = Task.objects.get(id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == 'POST':
        selected_status = request.POST.get('task_status')
        # print(selected_status)
        task.status = selected_status
        task.save()
        return redirect('task-details',task.id)
    
    return render(request,'task_detail.html',{'task':task,'status_choices':status_choices})


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