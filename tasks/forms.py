from django import forms
from tasks.models import Task,TaskDetails

# Django Form
class TaskForm(forms.Form):
    title = forms.CharField(max_length=250,label='Task Title')
    description = forms.CharField(widget=forms.Textarea(), label='Task Description')
    due_date = forms.DateField(widget=forms.SelectDateWidget,label='Due Date')
    assigned_to = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=[],label='Assigned To')
    
    def __init__(self, *args, **kwargs):
        print(args, kwargs)
        employees = kwargs.pop('employees',[])
        # print(employees)
        super().__init__(*args, **kwargs)
        # print(self.fields)
        self.fields['assigned_to'].choices = [(emp.id,emp.name) for emp in employees]
        
# style mixin
class StyledFormMixin:
    ''' Using mixin widget '''
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.apply_styled_widgets()
    default_classes = 'border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500'
    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class':self.default_classes,
                    'placeholder':f'Enter {field.label.lower()}'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class':f"{self.default_classes} resize-none",
                    'placeholder':f'Enter {field.label.lower()}',
                    'rows':5
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class':f"{self.default_classes} resize-none",
                    'placeholder':f'enter@email.com',
                    'rows':5
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class':f"{self.default_classes} resize-none",
                    'placeholder':f'*********',
                    'rows':5
                })
            elif isinstance(field.widget, forms.SelectDateWidget):
                field.widget.attrs.update({
                    'class':'border-2 border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500',
                    'placeholder':f'Enter {field.label.lower()}'
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class':'space-y-2',
                    'placeholder':f'Enter {field.label.lower()}'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': self.default_classes
                })

# Django Model Form
class TaskModelForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','due_date','assigned_to']
        widgets = {
            'due_date':forms.SelectDateWidget,
            'assigned_to':forms.CheckboxSelectMultiple
        }
        # jokhon field hobe 10ta ba something like that and ami khub kom field bad dite chai tokhon aivabe likbo:
        # exclude = ['project','is_completed','created_at','updated_at']
        
        
        # Style the form using widgets
        # widgets = {
        #     'title': forms.TextInput(attrs={
        #        'class':"w-full border-2 border-gray-300 rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500 p-2 my-2",
        #        'placeholder': 'Enter Title',
        #         }),
        #     'description': forms.Textarea(attrs={
        #         'class':"w-full border-2 border-gray-300 rounded-lg shadow-sm focus:border-rose-500 focus:ring-rose-500 p-2 my-2",
        #        'placeholder': 'Describe the task',
        #        'rows':3
        #     }),
        #     'due_date':forms.SelectDateWidget(attrs={
        #        'class':"border-2 border-gray-300 py-1 rounded-lg shadow-sm",
        #         }),
        #     'assigned_to':forms.CheckboxSelectMultiple(attrs={
        #        'class':"w-1 rounded-lg shadow-sm",
        #         }),
        # }
        
class TaskDetailModelForm(StyledFormMixin,forms.ModelForm):
    class Meta:
        model = TaskDetails
        fields = ['priority','notes','asset']