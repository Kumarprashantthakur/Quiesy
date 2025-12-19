from django import forms
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Quiz, Question
from django.forms.models import inlineformset_factory
class TeacherRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'teacher'
        if commit:
            user.save()
        return user


class TeacherLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")



class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'description', 'time_limit', 'password', 'num_of_qus']

QuestionFormSet = inlineformset_factory(
    Quiz,
    Question,
    fields=['text', 'option1', 'option2', 'option3', 'option4', 'correct_option', 'marks'],
    extra=5,  # number of empty question forms shown
    can_delete=False,
    validate_min=False,
)
