from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

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

TYPE_CHOICES = [
        ('strength', 'Силовая'),
        ('cardio', 'Кардио'),
        ('yoga', 'Йога'),
        ('other', 'Другое')
]

MUSCLE_CHOICES = [
    ('chest', 'Грудь'),
    ('triceps', 'Трицепс'),
    ('biceps', 'Бицепс'),
    ('shoulders', 'Плечи'),
    ('back', 'Спина'),
    ('lats', 'Широчайшие'),
    ('abs', 'Пресс'),
    ('quads', 'Квадрицепсы'),
    ('hamstrings', 'Бицепсы бедра'),
    ('glutes', 'Ягодицы'),
    ('calves', 'Икры'),
    ('chest_triceps', 'Грудь, трицепс'),
    ('back_biceps', 'Широчайшие, бицепс'),
    ('shoulders_triceps', 'Плечи, трицепс'),
    ('legs_glutes', 'Ноги, ягодицы'),
    ('quads_hamstrings', 'Квадрицепсы, бицепсы бедра'),
    ('calves_quads', 'Икры, квадрицепсы'),
    ('abs_obliques', 'Пресс, косые мышцы живота'),
    ('chest_shoulders_triceps', 'Грудь, плечи, трицепс'),
    ('back_shoulders_biceps', 'Спина, плечи, бицепс'),
]


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=36, default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class MealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_logs')
    meal_name = models.CharField(max_length=255)
    quantity = models.FloatField() 
    meal_nutrition = models.CharField(max_length=50)  
    log_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.meal_name} - {self.quantity}g"

    class Meta:
        ordering = ['-log_date']
        verbose_name = 'Meal Log'
        verbose_name_plural = 'Meal Logs'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Exercise(models.Model):
    name = models.CharField(max_length=32)
    muscle_groups = models.CharField(max_length=23, choices=MUSCLE_CHOICES, default='other')
    description = models.TextField()
    tags = models.ManyToManyField(Tag)
    workout_type = models.CharField(max_length=23, choices=TYPE_CHOICES, default='other')

    def __str__(self):
        return str(self.name)


class Workout(models.Model):
    TYPE_CHOICES = [
        ('strength', 'Силовая'),
        ('cardio', 'Кардио'),
        ('yoga', 'Йога'),
        ('other', 'Другое')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout')
    workout_type = models.CharField(choices=TYPE_CHOICES, max_length=8, default='other')
    workout_length = models.IntegerField()
    workout_muscle_group = models.CharField(max_length=9, choices=MUSCLE_GROUP_CHOICES, default='other')
    chosen_exercises = models.ManyToManyField(Exercise, related_name='workout')
    day = models.CharField(max_length=9)
    workout_counter = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'day')

class WorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField(default=timezone.now)
    workout_counter = models.IntegerField(default=0)  


    def __str__(self):
        return f"Workout session on {self.session_date} for {self.user}"


class ExercisePerformance(models.Model):
    workout_session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercise_performances')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.exercise.name} in session {self.workout_session}"


class SetPerformance(models.Model):
    exercise_performance = models.ForeignKey(ExercisePerformance, on_delete=models.CASCADE, related_name='set_performances')
    repetitions = models.IntegerField()
    weight = models.FloatField()

    def __str__(self):
        return f"{self.weight}kg x {self.repetitions} reps"

    
class UsersMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_meal')
    name = models.CharField(max_length=150, unique=True)
    proteins = models.FloatField()
    carbohydrates = models.FloatField()
    fats = models.FloatField()
    calories = models.FloatField()


class UserStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_stats')
    weight = models.FloatField(blank=True, null=True, default=False)
    height = models.FloatField(blank=True, null=True, default=False)
    bodyfat = models.FloatField(blank=True, null=True, default=False)
    waist = models.FloatField(blank=True, null=True, default=False)
    date = models.DateTimeField(auto_now_add=True)

class Goal(models.Model):
    GOAL_CHOICES = [
        ('weightloss', 'Похудение'),
        ('bulk', 'Набор веса'),
        ('waist', 'Уменьшение талии'),
        ('cut', 'Сушка')
    ]
    type = models.CharField(max_length=10, choices=GOAL_CHOICES, default='other')
    progress = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_goals')
    start_point = models.FloatField()
    end_point = models.FloatField()

    class Meta:
        unique_together = ('user', 'type')

class CalorieGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_calories_goal')
    calories = models.FloatField()
