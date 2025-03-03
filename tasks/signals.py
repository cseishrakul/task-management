from tasks.models import Task
from django.db.models.signals import post_save,pre_save,post_delete,m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail

# Signals
# @receiver(post_save,sender=Task)
# def notify_task_creation(sender,instance,created,**kwargs):
#     if created:
#         print('sender',sender)
#         print('instance',instance)
#         print(kwargs)
#         instance.is_completed = True
#         instance.save()
# @receiver(pre_save,sender=Task)
# def notify_task_creation(sender,instance,**kwargs):
#     print('sender',sender)
#     print('instance',instance)
#     print(kwargs)
#     instance.is_completed = True

# @receiver(post_delete,sender=Task)
# def notify_task_creation(sender,instance,**kwargs):
#     print('Task Deletd:',instance)
    
@receiver(m2m_changed,sender=Task.assigned_to.through)
def notify_employee_on_task_creation(sender,instance,action,**kwargs):
    if action == 'post_add':
        assigned_emails = [emp.email for emp in instance.assigned_to.all()]
        send_mail(
            "New Task Assigned",
            f"You have been assigned to the task: {instance.title}",
            "ishrak236@gmail.com",
            assigned_emails
        )

@receiver(post_delete,sender=Task)
def delete_associate_details(sender,instance,**kwargs):
    if instance.details:
        print(isinstance)
        instance.details.delete()
        print("Delete Successfully!")