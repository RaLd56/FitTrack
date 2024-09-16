from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Sum
from datetime import timedelta, datetime
from .forms import CustomUserCreationForm, CustomLoginForm, AddWorkoutForm, ExerciseSearchForm, WorkoutForm, AddUsersMealForm
from .utils import send_verification_email, ProductSearchSession, calculate_totals
from .models import EmailVerification, MealLog, Workout, Exercise, ExercisePerformance, SetPerformance, UsersMeal, WorkoutSession, UserStats, Goal, CalorieGoal
from .search_session import product_search_session
import re
import json





now = now()

    # Начало и конец текущего дня
start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_day = start_of_day + timedelta(days=1)


def homepage(request):
    return render(request, 'main/homepage.html')
def sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            code = get_random_string(length=6)  
            EmailVerification.objects.create(user=user, code=code)
            send_verification_email(user, code)
            return redirect('email_confirmation')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/sign_up.html', {'form': form})

def email_confirmation(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            verification = EmailVerification.objects.get(code=code, is_verified=False)
            verification.is_verified = True
            verification.save()
            return redirect('homepage')  # Перенаправление на страницу входа
        except EmailVerification.DoesNotExist:
            return render(request, 'main/email_confirmation.html', {'error': 'Invalid code'})
    return render(request, 'main/email_confirmation.html')

def password_reset(request):
    return render(request, 'main/password_reset.html')

def sign_in(request):
    error = None
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tracking')  
        else:
            error = 'Неправильное имя пользователя или пароль'
    else:
        form = CustomLoginForm()

    return render(request, 'main/sign_in.html', {'form': form, 'error': error})

@login_required 
def tracking(request):
    todays_meals = MealLog.objects.filter(
    user=request.user,
    log_date__gte=start_of_day,
    log_date__lt=end_of_day,
    )
    goal = Goal.objects.filter(user=request.user).first()
    calories_data = (MealLog.objects
                     .filter(user=request.user)
                     .values('log_date')
                     .annotate(total_calories=Sum('meal_nutrition'))
                     .order_by('-log_date'))
    
    # Подготавливаем данные для графика (массив дат и массив калорий)
    dates = [entry['log_date'].strftime('%Y-%m-%d') for entry in calories_data]
    total_calories = [entry['total_calories'] for entry in calories_data]

    WEEKDAY = [(0, 'Понедельник'), 
               (1, 'Вторник'), 
               (2, 'Среда'),
               (3, 'Четверг'),
               (4, 'Пятница'),
               (5, 'Суббота'),
               (6, 'Воскресенье')
               ]
    workouts_weekdays = []
    for day in WEEKDAY:
        try:
            closest_workout = Workout.objects.get(user = request.user, day=day[1])
            workouts_weekdays.append(day[0])
        except:
            pass

    for day in workouts_weekdays:
        if day == (now.date().weekday()):
            closest_workout = 'Сегодня'
            break
        elif day > (now.date().weekday()):
            for item in WEEKDAY:
                if item[0] == day:  
                    closest_workout = item[1]  
                    break
            break
        else:
            closest_workout = 'На этой неделе тренировок нет'
    if not(Workout.objects.filter(user=request.user)):
        closest_workout = 'Нет тренировок'

   

    totals = calculate_totals(todays_meals)
    return render(request, 'main/tracking.html', {'totals': totals, 'closest_workout_display': closest_workout, 'goal': goal, 'dates': dates, 'total_calories': total_calories})

@login_required
def nutrition(request):
    todays_meals = MealLog.objects.filter(
    user=request.user,
    log_date__gte=start_of_day,
    log_date__lt=end_of_day
    )
    totals = calculate_totals(todays_meals)
    try:
        calorie_goal = CalorieGoal.objects.get(user=request.user).calories
    except:
        calorie_goal = 'Цель не указана'
    return render(request, 'main/nutrition.html', {'totals': totals, 'calorie_goal': calorie_goal})

@login_required
def add_meal(request):
    recent_meals = MealLog.objects.filter(user=request.user)
    users_meals = UsersMeal.objects.filter(user=request.user)
    form = AddUsersMealForm()
    return render(request, 'main/add_meal.html', {'recent_meals': recent_meals, 'users_meals': users_meals, 'form': form})

@login_required
@never_cache
def search(request):
    query = request.GET.get('query')
    results = product_search_session.search_products(query)

    def split_name_and_nutrition(info_str):
        nutrition_pattern = re.compile(r'(\d+\s*ккал|\bБ\s*\d+\.?\d*\s*г|\bЖ\s*\d+\.?\d*\s*г|\bУ\s*\d+\.?\d*\s*г)', re.IGNORECASE)
        
        matches = nutrition_pattern.findall(info_str)
        
        if matches:
            nutrition = ', '.join(matches)
            
            first_match_pos = info_str.find(matches[0])
            name = info_str[:first_match_pos].strip()
            
            return name, nutrition
        else:
            return info_str, ''
        
    if results != 404:
        processed_results = []
        for result in results:
            name, nutrition = split_name_and_nutrition(result)
            processed_results.append({
                'name': name,
                'nutrition': nutrition,
            })
    else:
        processed_results = results

    return render(request, 'main/search_results.html', {'results': processed_results, 'query': query})

@login_required
def todays_meals(request):

    todays_meals = MealLog.objects.filter(
        user=request.user,
        log_date__gte=start_of_day,
        log_date__lt=end_of_day
    )
    return render(request, 'main/todays_meals.html', {'todays_meals': todays_meals})

@login_required
@require_POST
def log_meal(request):
    data = json.loads(request.body)
    meal_name = data.get('meal_name')
    meal_nutrition = data.get('meal_nutrition')
    quantity = data.get('quantity')

    if meal_name and meal_nutrition and quantity:
        MealLog.objects.create(
            meal_name=meal_name,
            meal_nutrition=meal_nutrition,
            quantity=quantity,
            log_date=datetime.now(),
            user=request.user
        )
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
    
@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_meal(request, meal_id):
    try:
        meal = MealLog.objects.get(id=meal_id, user=request.user)
        meal.delete()
        return JsonResponse({'success': True})
    except MealLog.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Meal not found'}, status=404)
    
@login_required
def workouts(request):
    workouts = Workout.objects.filter(user=request.user)

    workouts_by_day = {workout.day: workout for workout in workouts}

    return render(request, 'main/workouts.html', {
        'workouts_by_day': workouts_by_day,  
        'days_of_week': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']  
    })


@login_required
def add_workout(request, date):
    if request.method == 'POST':
        form = AddWorkoutForm(request.POST)
        if form.is_valid():
            workout_type = form.cleaned_data.get('type')
            workout_length = form.cleaned_data.get('length')
            muscle_group = form.cleaned_data.get('muscle_group')
            day = date
            workout = Workout(
                user=request.user, 
                day=day,
                workout_type=workout_type,
                workout_length=workout_length,
            )
            if muscle_group:
                Workout.workout_muscle_group = muscle_group
            workout.save()
            return redirect('../../workouts')
        else:
            return render(request, 'main/add_workout.html', {'form': form})
    else:
        form = AddWorkoutForm()
        return render(request, 'main/add_workout.html', {'form': form})

@login_required
def update_workout(request, date):
    exercises_with_muscle_groups = []
    try:
        workout = Workout.objects.filter(user=request.user, day=date).first()
        if workout:
            exercises = workout.chosen_exercises.all()  
            
            for exercise in exercises:
                exercise_name = exercise.name
                muscle_group = exercise.get_muscle_groups_display()
                exercises_with_muscle_groups.append((exercise_name, muscle_group))
                
            print(exercises_with_muscle_groups)
    except Exception as e:
        print(f"Error: {e}")
        pass

    return render(request, 'main/update_workout.html', {'day': date, 'exercises_with_muscle_groups': exercises_with_muscle_groups})


@login_required
def search_exercise(request, date):
    search_form = ExerciseSearchForm(request.GET)
    if Workout.objects.get(day=date, user=request.user).workout_type == 'other':
        exercises = Exercise.objects.all()
    else:
        exercises = Exercise.objects.all().filter(workout_type=Workout.objects.get(day=date, user=request.user).workout_type)
    num_empty_elements = []


    if search_form.is_valid():
        query = search_form.cleaned_data['query']
        if query:
            exercises = exercises.filter(name__icontains=query)


    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'q' in request.GET:
        query = request.GET.get('q', '').strip().lower()
        suggestions = []

        if query:
            all_exercises = Exercise.objects.all()

            # Поиск по названиям
            for exercise in all_exercises:
                if query in exercise.name.lower():
                    suggestions.append({'id': exercise.id, 'name': exercise.name})

            # Поиск по тегам
            for exercise in all_exercises:
                tags = exercise.tags.values_list('name', flat=True)
                for tag in tags:
                    if query in tag.lower():
                        if not any(suggestion['id'] == exercise.id for suggestion in suggestions):
                            suggestions.append({'id': exercise.id, 'name': exercise.name})

            # Ограничиваем количество подсказок
            suggestions = suggestions[:5]

        return JsonResponse(suggestions, safe=False)

    num_empty_elements = range(25 - exercises.count())

    return render(request, 'main/search_exercise.html', {
        'search_form': search_form,
        'exercises': exercises,
        'num_empty_elements': num_empty_elements,
        'day': date  
    })


@login_required
@require_POST
def add_exercise_to_workout(request):
    data = json.loads(request.body)
    exercise_name = data.get('exercise_name')
    date = data.get('date')
    print(exercise_name)

    try:
        exercise = Exercise.objects.filter(name=exercise_name).first()
        print(exercise)
        print(date)
        workout, created = Workout.objects.get_or_create(user=request.user, day=date)
        workout.chosen_exercises.add(exercise)
        workout.save()

        return JsonResponse({'success': True})
    except Exercise.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Упражнение не найдено.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@login_required
def delete_workout(request, date):
    Workout.objects.all().filter(user=request.user, day=date).get().delete()
    return redirect('workouts')


@require_http_methods(["DELETE"])
@login_required
def delete_exercise(request, date):
    index = int(request.GET.get('index', -1))
    if index == -1:
        return JsonResponse({'error': 'Invalid index'}, status=400)
    
    try:
        workout = Workout.objects.get(user=request.user, day=date)
        exercises = workout.chosen_exercises.all()
        if 0 <= index < len(exercises):
            exercise = exercises[index]
            exercise.delete()  
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Index out of range'}, status=400)
    except Workout.DoesNotExist:
        return JsonResponse({'error': 'Workout not found'}, status=404)
    

@login_required
def log_workout(request, date):
    try:
        workout = Workout.objects.get(user=request.user, day=date)
    except:
        return redirect('workouts')
    exercises = workout.chosen_exercises.all()
    exercise_names = [e.name for e in exercises]

    try:
        counter = WorkoutSession.objects.all().last().workout_counter
    except:
        counter = 0
    
    

    workout_session = WorkoutSession.objects.get_or_create(
        user=request.user,
        workout=workout,
        session_date=now.date(),
        workout_counter = counter
    )
    

    if request.method == 'POST':
        form = WorkoutForm(request.POST, exercises=exercises)
        if form.is_valid():
            exercise_name = form.cleaned_data['exercise_name']
            weight = form.cleaned_data['weight']
            repetitions = form.cleaned_data['repetitions']


            try:
                exercise = Exercise.objects.get(name=exercise_name)
            except Exercise.DoesNotExist:
                form.add_error('exercise_name', 'Exercise does not exist')
                return render(request, 'main/log_workout.html', {'form': form, 'exercises': exercise_names})

            
            exercise_performance, created = ExercisePerformance.objects.get_or_create(
                workout_session=workout_session[0],
                exercise=exercise,

            )

            
            SetPerformance.objects.create(
                exercise_performance=exercise_performance,
                repetitions=repetitions,
                weight=weight,
            )
            


            if 'next_set' in request.POST:
                form = WorkoutForm(exercises=exercises)
                return render(request, 'main/log_workout.html', {'form': form, 'exercises': exercise_names})
            elif 'finish_workout' in request.POST:
                form = WorkoutForm(exercises=exercises)
                WorkoutSession.objects.get_or_create(
                    user=request.user,
                    workout=workout,
                    session_date=now.date(),
                    workout_counter = counter + 1
                )
                return redirect('workouts')  
    else:
        form = WorkoutForm(exercises=exercises)

    return render(request, 'main/log_workout.html', {'form': form, 'exercises': exercises})


@login_required
def add_custom_meal(request):
    if request.method == 'POST':
        form = AddUsersMealForm(request.POST)
        if form.is_valid():
            UsersMeal.objects.create(
                name = request.POST.get('name'),
                proteins = request.POST.get('proteins'),
                carbohydrates = request.POST.get('carbohydrates'),
                fats = request.POST.get('fats'),
                calories = request.POST.get('calories'),
                user = request.user),
            return redirect('add_meal')
        else:
            redirect('add_meal')
    else:
        form = AddUsersMealForm()
    return render(request, 'main/add_users_meal.html', {'form': form})

@login_required
@require_http_methods(["DELETE"])
def delete_custom_meal(request, meal_name):
    meal = get_object_or_404(UsersMeal, name=meal_name, user=request.user)
    meal.delete()
    return JsonResponse({'message': 'Блюдо успешно удалено.'})

@login_required
@login_required
def log_users_meal(request):
    if request.method == 'POST':
        meal_name = request.POST.get('meal_name')
        quantity = float(request.POST.get('quantity', 0))

        try:
            meal = UsersMeal.objects.get(user=request.user, name=meal_name)
        except UsersMeal.DoesNotExist:
            return redirect('add_meal')

        total_proteins = meal.proteins * (quantity / 100)
        total_carbohydrates = meal.carbohydrates * (quantity / 100)
        total_fats = meal.fats * (quantity / 100)
        total_calories = meal.calories * (quantity / 100)

        MealLog.objects.create(
            user=request.user,
            meal_name=meal.name,
            quantity=quantity,
            meal_nutrition=f"{total_calories} ккал, Б {total_proteins} г, Ж {total_fats} г, У {total_carbohydrates} г",
            log_date=now
        )
        return redirect('add_meal')
    
@login_required
def set_parameters(request):
    if request.method == 'POST':
        try:
            weight = request.POST.get('weight')
            height = request.POST.get('height')
            bodyfat = request.POST.get('bodyfat')
            waist = request.POST.get('waist')



            UserStats.objects.update_or_create(
                user=request.user,
                defaults={
                    'weight': weight if weight else None,
                    'height': height if height else None,
                    'bodyfat': bodyfat if bodyfat else None,
                    'waist': waist if waist else None,
                }
            )

        except:
            pass
    
    return render(request, 'main/set_parameters.html')



@login_required
def profile(request):
    goals = Goal.objects.filter(user=request.user)
    for goal in goals:
        if goal.type == 'bulk':
            if goal.start_point > UserStats.objects.get(user=request.user).weight:
                goal.progress = 0
            elif goal.end_point < UserStats.objects.get(user=request.user).weight:
                goal.progress = 100
            else:
                goal.progress = int(((abs(float(UserStats.objects.get(user=request.user).weight) - float(goal.start_point))) / abs(float(goal.end_point) - float(goal.start_point))*100))
            goal.save()
        if goal.type == 'waist':
            if goal.start_point < UserStats.objects.get(user=request.user).waist:
                goal.progress = 0
            elif goal.end_point > UserStats.objects.get(user=request.user).waist:
                goal.progress = 100
            else:
                goal.progress = int(((abs(float(UserStats.objects.get(user=request.user).weight) - float(goal.start_point))) / abs(float(goal.end_point) - float(goal.start_point))*100))
            goal.save()

        

    
    
    # Получаем все уникальные упражнения, которые пользователь делал
    user_workouts = Workout.objects.filter(user=request.user).prefetch_related('chosen_exercises')
    exercises = Exercise.objects.filter(workout__in=user_workouts).distinct()

    # Если пользователь выбрал упражнение
    name = request.GET.get('name')
    scores = []

    if name:
        exercise = Exercise.objects.get(name=name)
        workouts = Workout.objects.filter(user=request.user, chosen_exercises=exercise).prefetch_related(
            'sessions', 'sessions__exercise_performances', 'sessions__exercise_performances__set_performances'
        )
        for workout in workouts:
            workout_sessions = workout.sessions.all()
            

            for session in workout_sessions:
                try:
                    exercise_performance = session.exercise_performances.get(exercise=exercise)
                except ExercisePerformance.DoesNotExist:
                    continue

                set_performances = exercise_performance.set_performances.all()
                set_scores = []

                for set_perf in set_performances:
                    M = set_perf.weight if set_perf.weight > 0 else 1
                    k = set_perf.repetitions
                    score = (M * k) / 30 + M
                    set_scores.append(score)

                if set_scores:
                    average_score = sum(set_scores) / len(set_scores)
                    scores.append(average_score)
    
    print(goals)

    return render(request, 'main/profile.html', {
        'exercises': exercises,  
        'scores': scores, 
        'selected_exercise': name if name else None,  
        'goals': goals, 
    })

@login_required
def add_goal(request):
    error = False
    if request.method == 'POST':
        if 'add_goal' in request.POST:
            goal_type = request.POST.get('type')
            end_point = request.POST.get('end_point')
            if goal_type == 'bulk' or goal_type == 'weightloss':
                print(UserStats.objects.get(user=request.user).weight)
                if (UserStats.objects.get(user=request.user).weight == None):
                    error = 'Укажите ваш текущий вес в "Общие показатели"'
                else:
                    Goal.objects.create(type=goal_type, end_point = end_point, start_point=UserStats.objects.get(user=request.user).weight, user=request.user, progress = 0)
            elif goal_type == 'cut':
                if (UserStats.objects.get(user=request.user).bodyfat == None):
                    error = 'Укажите ваш текущий процент жира в "Общие показатели"'
                else:
                    Goal.objects.create(type=goal_type, end_point = end_point, start_point=UserStats.objects.get(user=request.user).bodyfat, user=request.user, progress = 0)
            elif goal_type == 'waist':
                if (UserStats.objects.get(user=request.user).waist == None):
                    error = 'Укажите ваш текущий обхват талии в "Общие показатели"'
                else:
                    Goal.objects.create(type=goal_type, end_point = end_point, start_point=UserStats.objects.get(user=request.user).waist, user=request.user, progress = 0)


        elif 'delete_goal' in request.POST:
            goal_id = request.POST.get('goal_id')
            if goal_id:
                goal = get_object_or_404(Goal, id=goal_id, user=request.user)
                goal.delete()

    goals = Goal.objects.all().filter(user=request.user)
    return render(request, 'main/add_goal.html', {'goals': goals, 'error': error})

@login_required
@require_POST
def set_calorie_goal(request):
    calorie_goal = request.POST.get('calorie_goal')
    if calorie_goal:
        calorie_goal = float(calorie_goal)
        CalorieGoal.objects.update_or_create(
            user=request.user,
            defaults={'calories': calorie_goal}
        )
    return redirect('nutrition')  

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')