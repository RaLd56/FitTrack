from django.contrib import admin
from .models import Exercise, ExercisePerformance, SetPerformance, MealLog, WorkoutSession, UserStats

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'muscle_groups')  
    search_fields = ('name',)

@admin.register(ExercisePerformance)
class ExercisePerformanceAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'workout_session')  
    search_fields = ('exercise',)

@admin.register(SetPerformance)
class SetPerformanceAdmin(admin.ModelAdmin):
    list_display = ('exercise_performance', 'repetitions', 'weight')  
    search_fields = ('exercise',)

@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_name', 'quantity')  
    search_fields = ('meal_name',)

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_date', 'workout_counter')  
    search_fields = ('meal_name',)

@admin.register(UserStats)
class UserstatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'height', 'bodyfat', 'waist')  
    search_fields = ('user',)
