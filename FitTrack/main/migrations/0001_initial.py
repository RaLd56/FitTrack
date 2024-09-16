# Generated by Django 5.1 on 2024-09-07 22:14

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('muscle_groups', models.CharField(choices=[('chest', 'Грудь'), ('triceps', 'Трицепс'), ('biceps', 'Бицепс'), ('shoulders', 'Плечи'), ('back', 'Спина'), ('lats', 'Широчайшие'), ('abs', 'Пресс'), ('quads', 'Квадрицепсы'), ('hamstrings', 'Бицепсы бедра'), ('glutes', 'Ягодицы'), ('calves', 'Икры'), ('chest_triceps', 'Грудь, трицепс'), ('back_biceps', 'Широчайшие, бицепс'), ('shoulders_triceps', 'Плечи, трицепс'), ('legs_glutes', 'Ноги, ягодицы'), ('quads_hamstrings', 'Квадрицепсы, бицепсы бедра'), ('calves_quads', 'Икры, квадрицепсы'), ('abs_obliques', 'Пресс, косые мышцы живота'), ('chest_shoulders_triceps', 'Грудь, плечи, трицепс'), ('back_shoulders_biceps', 'Спина, плечи, бицепс')], default='other', max_length=23)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UsersExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(default='нет описания')),
            ],
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=uuid.uuid4, editable=False, max_length=36)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExercisePerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.exercise')),
            ],
        ),
        migrations.CreateModel(
            name='MealLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_name', models.CharField(max_length=255)),
                ('quantity', models.FloatField()),
                ('meal_nutrition', models.CharField(max_length=50)),
                ('log_date', models.DateField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Meal Log',
                'verbose_name_plural': 'Meal Logs',
                'ordering': ['-log_date'],
            },
        ),
        migrations.CreateModel(
            name='SetPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repetitions', models.IntegerField()),
                ('weight', models.FloatField()),
                ('exercise_performance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='set_performances', to='main.exerciseperformance')),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='tags',
            field=models.ManyToManyField(to='main.tag'),
        ),
        migrations.CreateModel(
            name='UsersMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('proteins', models.FloatField()),
                ('carbohydrates', models.FloatField()),
                ('fats', models.FloatField()),
                ('calories', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_meal', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workout_type', models.CharField(choices=[('strength', 'Силовая'), ('cardio', 'Кардио'), ('yoga', 'Йога'), ('other', 'Другое')], default='other', max_length=8)),
                ('workout_length', models.CharField(max_length=50)),
                ('workout_muscle_group', models.CharField(choices=[('chest', 'Грудь'), ('back', 'Спина'), ('arms', 'Руки'), ('legs', 'Ноги'), ('chest_bi', 'Грудь-бицепс'), ('back_tri', 'Спина-трицепс'), ('full_body', 'Фулбади'), ('push', '"Толкай"'), ('pull', '"Тяни"'), ('other', 'Другое')], default='other', max_length=9)),
                ('day', models.CharField(max_length=9)),
                ('workout_counter', models.IntegerField(default=0)),
                ('chosen_exercises', models.ManyToManyField(related_name='workout', to='main.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workout', to=settings.AUTH_USER_MODEL)),
                ('users_exercises', models.ManyToManyField(related_name='workout', to='main.usersexercise')),
            ],
            options={
                'unique_together': {('user', 'day')},
            },
        ),
        migrations.CreateModel(
            name='WorkoutSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_date', models.DateField(default=django.utils.timezone.now)),
                ('workout_counter', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workout_sessions', to=settings.AUTH_USER_MODEL)),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='main.workout')),
            ],
        ),
        migrations.AddField(
            model_name='exerciseperformance',
            name='workout_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_performances', to='main.workoutsession'),
        ),
    ]
