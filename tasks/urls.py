from django.urls import path
from .views import dashboard,CreateTask,UpdateTask,ViewProject,TaskDetail,ManagerDashboardView,EmployeeDashboardView,DeleteTaskView

urlpatterns = [
     path('manager-dashboard/',ManagerDashboardView.as_view(),name='manager-dashboard'),
     path('employee-dashboard/',EmployeeDashboardView.as_view(),name='employee-dashboard'),
     path('create_task/',CreateTask.as_view(),name='create-task'),
     path('view_project/',ViewProject.as_view(),name='view-task'),
     path('task/<int:task_id>/details/',TaskDetail.as_view(),name='task-details'),
     path('update_task/<int:id>/',UpdateTask.as_view(),name='update-task'),
     path('delete_task/<int:id>/',DeleteTaskView.as_view(),name='delete-task'),
     path('dashboard/',dashboard,name='dashboard'),
]
