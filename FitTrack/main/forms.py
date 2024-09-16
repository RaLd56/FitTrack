from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from main.models import Exercise, UsersMeal


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Электронная почта'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        
        # Настройка виджетов
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
    
class AddWorkoutForm(forms.Form):
    TYPE_CHOICES = [
        ('strength', 'Силовая'),
        ('cardio', 'Кардио'),
        ('yoga', 'Йога'),
        ('other', 'Другое')
    ]
    MUSCLE_GROUP_CHOICES = [
        ('chest', 'Грудь'),
        ('back', 'Спина'),
        ('arms', 'Руки'),
        ('legs', 'Ноги'),
        ('chest_bi', 'Грудь-бицепс'),
        ('back_tri', 'Спина-трицепс'),
        ('full_body', 'Фулбади'),
        ('push', '"Толкай"'),
        ('pull', '"Тяни"'),
        ('other', 'Другое'),
    ]
    type = forms.ChoiceField(choices=TYPE_CHOICES, label='Укажите тип тренировки')
    length = forms.CharField(
        label='Продолжительность, мин',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Продолжительность, мин',
            'id': 'id_length',
        })
    )
    muscle_group = forms.ChoiceField(
        choices=MUSCLE_GROUP_CHOICES, label='Укажите мышечную группу', required=False
    )

class ExerciseSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Поиск упражнений")


class WorkoutForm(forms.Form):
    exercise_name = forms.ModelChoiceField(queryset=Exercise.objects.none(), label='Упражнение')
    weight = forms.FloatField(label='Вес')
    repetitions = forms.IntegerField(label='Повторения')

    def __init__(self, *args, **kwargs):
        exercises = kwargs.pop('exercises', None)  
        super().__init__(*args, **kwargs)

        if exercises:
            self.fields['exercise_name'].queryset = exercises

class AddUsersMealForm(forms.ModelForm):
    class Meta:
        model = UsersMeal
        fields = ['name', 'proteins', 'carbohydrates', 'fats', 'calories']