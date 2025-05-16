from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import Recommendation, UserRecommendation, PlannerItem, Profile 
from .forms import RecommendationFilterForm, AddToPlannerForm, CustomUserCreationForm 
from .utils import generate_personalized_recommendations, generate_ai_recommendation
from datetime import datetime
import logging

# Get a logger instance
logger = logging.getLogger(__name__)

# Configure the logger
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('signup_debug.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Home Page
class Home(TemplateView):
    template_name = 'accounts/home.html'


# Login Page
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'account/login.html')


# Signup Page
def signup_view(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        print("POST request received in signup_view")  
        form = CustomUserCreationForm(request.POST)
        logger.info(f"Is form valid? {form.is_valid()}")
        if form.is_valid():
            logger.info("Form is valid - proceeding with signup and redirect.")
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            print("About to redirect to account_login")
            return redirect('login')
        else:
            logger.info("Form is NOT valid - printing errors:")
            for field, errors in form.errors.items():
                logger.info(f"Field: {field}, Errors: {errors}")
            for error in form.errors.values():
                for msg in error:
                    messages.error(request, msg)
    else:
        print("Form fields:", form.fields.keys())
    return render(request, 'account/signup.html', {'form': form})

# Dashboard
@login_required
def dashboard(request):
    return render(request, 'app/dashboard.html')


# Recommendations Page
@login_required
def recommendations_view(request):
    form = RecommendationFilterForm(request.GET)
    category = form.cleaned_data.get('category', 'all') if form.is_valid() else 'all'
    query = form.cleaned_data.get('query', '') if form.is_valid() else ''

    user = request.user
    all_recommendations = generate_personalized_recommendations(user, category=category, query=query)

    # --- Uniqueness Logic ---
    unique_recommendations = []
    seen_titles = set()
    for rec in all_recommendations:
        if rec.title not in seen_titles:
            unique_recommendations.append(rec)
            seen_titles.add(rec.title)

    recommendations_with_status = []
    user_recommendations = UserRecommendation.objects.filter(
        user=user,
        recommendation__in=unique_recommendations
    ).values_list('recommendation_id', 'liked', 'done', 'saved')

    interaction_status = {
        rec_id: {'liked': liked, 'done': done, 'saved': saved}
        for rec_id, liked, done, saved in user_recommendations
    }

    for rec in unique_recommendations:
        status = interaction_status.get(rec.id, {'liked': False, 'done': False, 'saved': False})
        recommendations_with_status.append({
            'recommendation': rec,
            'liked': status['liked'],
            'done': status['done'],
            'saved': status['saved'],
        })

    ai_recommendation = None 
    ai_recommendation_obj = None 

    if request.method == 'POST' and 'ai_input' in request.POST:
        user_input = request.POST['ai_input']
        ai_recommendation_obj = generate_ai_recommendation(request.user, user_input)
        if ai_recommendation_obj:
            existing_recommendation = Recommendation.objects.filter(title=ai_recommendation_obj.title, description=ai_recommendation_obj.description).first()
            if existing_recommendation:
                ai_recommendation_obj = existing_recommendation
            else:
                ai_recommendation_obj.save()

            user_recommendation, created = UserRecommendation.objects.get_or_create(
                user=request.user,
                recommendation=ai_recommendation_obj
            )
            ai_recommendation = {
                'recommendation': ai_recommendation_obj,
                'liked': user_recommendation.liked,
                'done': user_recommendation.done,
                'saved': user_recommendation.saved,
            }
        else:
            ai_recommendation = None 

    context = {
        'recommendations': recommendations_with_status,
        'filter_form': form,
        'ai_recommendation': ai_recommendation,
    }
    return render(request, 'app/recommendations.html', context)


@login_required
def like_recommendation(request, recommendation_id):
    if request.method == 'POST':
        recommendation = Recommendation.objects.get(pk=recommendation_id)
        user_recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            recommendation=recommendation
        )
        user_recommendation.liked = not user_recommendation.liked
        user_recommendation.save()
    return redirect('recommendations')


@login_required
def mark_done_recommendation(request, recommendation_id):
    if request.method == 'POST':
        recommendation = Recommendation.objects.get(pk=recommendation_id)
        user_recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            recommendation=recommendation
        )
        user_recommendation.done = not user_recommendation.done
        user_recommendation.save()
    return redirect('recommendations')


@login_required
def save_recommendation(request, recommendation_id):
    if request.method == 'POST':
        recommendation = Recommendation.objects.get(pk=recommendation_id)
        user_recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            recommendation=recommendation
        )
        user_recommendation.saved = not user_recommendation.saved
        user_recommendation.save()
    return redirect('recommendations')


@login_required
def like_ai_recommendation(request, recommendation_id):
    if request.method == 'POST':
        recommendation = get_object_or_404(Recommendation, pk=recommendation_id)
        user_recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            recommendation=recommendation
        )
        user_recommendation.liked = not user_recommendation.liked
        user_recommendation.save()
    return redirect('recommendations')

@login_required
def mark_done_ai_recommendation(request, recommendation_id):
    if request.method == 'POST':
        recommendation = get_object_or_404(Recommendation, pk=recommendation_id)
        user_recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            recommendation=recommendation
        )
        user_recommendation.done = not user_recommendation.done
        user_recommendation.save()
    return redirect('recommendations')

@login_required
def save_ai_recommendation(request, recommendation_id):
    if request.method == 'POST':
        recommendation = get_object_or_404(Recommendation, pk=recommendation_id)
        user_recommendation, created = UserRecommendation.objects.get_or_create(
            user=request.user,
            recommendation=recommendation
        )
        user_recommendation.saved = not user_recommendation.saved
        user_recommendation.save()
    return redirect('recommendations')


# Articles Page
def articles_view(request):
    return render(request, 'app/articles.html')


# Profile Page
@login_required
def profile_view(request):
    profile = request.user.profile  
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        profile.profile_pic = request.FILES['profile_photo']
        profile.save()
        messages.success(request, 'Profile picture updated successfully!')
        return redirect('profile') 
    context = {'profile': profile}
    return render(request, 'app/profile.html', context)


# Home Page View
def home(request):
    return render(request, 'accounts/home.html', {'user': request.user})


def custom_logout(request):
    logout(request)
    return redirect('account_login')


def regenerate_recommendation(request):
    return redirect('recommendations')


@login_required
def planner_view(request):
    planner_items = PlannerItem.objects.filter(user=request.user).order_by(
        'scheduled_date', 'scheduled_time')
    context = {'planner_items': planner_items}
    return render(request, 'app/planner.html', context)


# Saved Recommendations View
@login_required
def saved_recommendations_view(request):
    saved_recommendations = UserRecommendation.objects.filter(user=request.user, saved=True).select_related(
        'recommendation').order_by('-created_at')
    context = {'saved_recommendations': saved_recommendations}
    return render(request, 'app/saved_recommendations.html', context)


@login_required
def add_to_planner_view(request, recommendation_id):
    recommendation = get_object_or_404(Recommendation, pk=recommendation_id)
    if request.method == 'POST':
        scheduled_date_str = request.POST.get('scheduled_date')
        scheduled_time_str = request.POST.get('scheduled_time')

        try:
            scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
            scheduled_time = None
            if scheduled_time_str:
                scheduled_time = datetime.strptime(scheduled_time_str, '%H:%M').time()

            PlannerItem.objects.get_or_create(
                user=request.user,
                recommendation=recommendation,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
            )
            messages.success(request, f"'{recommendation.title}' added to your planner.")
            return redirect('planner')
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('recommendations')

    form = AddToPlannerForm()
    context = {'recommendation': recommendation, 'form': form}
    return render(request, 'app/add_to_planner.html', context)


def home_view(request):
    return render(request, 'accounts/home.html', {'user': request.user})

def redirect_to_profile(request):
    return redirect('profile')

def logout_view(request):
    logout(request)
    return redirect('account_login')

def root_view(request):
    return redirect('home')