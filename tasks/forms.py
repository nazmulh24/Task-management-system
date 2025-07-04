from django.utils import timezone
from django import forms
from tasks.models import Task, TaskDetail


# --> Django Form
class TaskForm(forms.Form):
    title = forms.CharField(max_length=200, label="Task Title")

    description = forms.CharField(
        widget=forms.Textarea(),
        label="Task Descrioption",  # --> Label for the textarea...
    )  # --> Textarea widget for multiline input

    due_date = forms.DateField(
        widget=forms.SelectDateWidget(),
        label="Due Date",
    )

    assigned_to = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=[],
        label="Assigned To",
    )

    def __init__(self, *args, **kwargs):
        # print(args, kwargs)
        employees = kwargs.pop("employees", [])
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].choices = [(emp.id, emp.name) for emp in employees]


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_widgets()

    default_classes = (
        "border-2 border-gray-300 p-2 rounded-lg shadow-sm focus:border-green-400"
    )

    def apply_style_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update(
                    {
                        "class": f"{self.default_classes} w-full",
                        "placeholder": f"Enter {field.label.lower()}...",
                    }
                )
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update(
                    {
                        "class": f"{self.default_classes} w-full bg-gray-50",
                        "placeholder": f"Enter {field.label.lower()}...",
                        "rows": 4,
                    }
                )
            elif isinstance(field.widget, forms.SelectDateWidget):
                # print("Inside Date")
                field.widget.attrs.update(
                    {
                        "class": "border-2 border-gray-300 p-2 rounded-lg shadow-sm focus:border-green-400",
                    }
                )
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                # print("Inside Checkbox")
                field.widget.attrs.update(
                    {
                        # "class": "flex flex-col gap-2",
                        "class": "space-y-2",
                    }
                )
            else:
                print("Inside else")
                field.widget.attrs.update(
                    {
                        "class": f"{self.default_classes} w-full",
                    }
                )


class TaskModelForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "assigned_to"]

        widgets = {
            "due_date": forms.SelectDateWidget,
            "assigned_to": forms.CheckboxSelectMultiple,
        }


class TaskDetailModelForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = TaskDetail
        fields = ["priority", "notes", "asset"]
