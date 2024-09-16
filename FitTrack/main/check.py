from models import Workout, SetPerformance
# Найдём тренировку по пользователю и уникальному идентификатору тренировки
workout = Workout.objects.get(user='Admin', workout_counter=1)

# Получаем все выполнения упражнений (ExercisePerformance) для этой тренировки
exercise_performances = workout.exercise_performances.all()

# Получаем все подходы (SetPerformance) для каждого выполнения упражнения
all_sets = SetPerformance.objects.filter(exercise_performance__in=exercise_performances)

# Теперь в all_sets содержатся все подходы, сделанные в этой тренировке
for set_performance in all_sets:
    print(f"Упражнение: {set_performance.exercise_performance.exercise.name}, "
          f"Вес: {set_performance.weight} кг, "
          f"Повторения: {set_performance.repetitions}")
