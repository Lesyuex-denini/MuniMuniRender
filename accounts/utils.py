# app/utils.py
import google.generativeai as genai
from django.conf import settings
from .models import Recommendation
from django.db.models import QuerySet
from django.db import models

def generate_personalized_recommendations(user, category='all', query=''):
    """
    Generates personalized recommendations (currently static examples) and ensures uniqueness.
    """
    if not Recommendation.objects.exists():
        Recommendation.objects.bulk_create([
            Recommendation(title="Quick Breathing Exercise", description="Inhale deeply for 4 counts, hold for 4, exhale for 6. Repeat.", category="stress_relief", reason="Helps to calm the nervous system."),
            Recommendation(title="Create a Relaxing Bedtime Routine", description="Take a warm bath, read a book, or listen to calming music before sleep.", category="sleep", reason="Signals your body it's time to wind down."),
            Recommendation(title="Break Down Tasks", description="Divide large tasks into smaller, manageable steps.", category="focus", reason="Makes goals feel less overwhelming and improves concentration."),
            Recommendation(title="Journal About Your Feelings", description="Write down your thoughts and emotions to process them.", category="anxiety_relief", reason="Provides an outlet for worries and can offer perspective."),
            Recommendation(title="Set One Small Achievable Goal for Today", description="Focus on one thing you can accomplish to build momentum.", category="motivation", reason="Small wins can boost confidence and drive."),
            Recommendation(title="Practice Mindful Observation", description="Pay attention to your surroundings using all your senses for a few minutes.", category="mindfulness", reason="Anchors you in the present moment and reduces mental clutter."),
        ])

    recommendations = Recommendation.objects.all()

    if category != 'all':
        recommendations = recommendations.filter(category=category)

    if query:
        recommendations = recommendations.filter(
            models.Q(title__icontains=query) | models.Q(description__icontains=query)
        )

    return recommendations.distinct()

def generate_ai_recommendation(user, user_input):
    """Generates a personalized recommendation using the Gemini API."""
    genai.configure(api_key=settings.GEMINI_API_KEY)

    print("--- Available Gemini Models and Methods ---")
    for model in genai.list_models():
        print(f"Model: {model.name}")
        for method in model.supported_generation_methods:
            print(f"- {method}")
    print("--- End of Available Models ---")

    model_name_to_use = 'gemini-1.5-flash'  # Keep this for now

    prompt = f"""The user is feeling: "{user_input}".
Please provide ONE self-care recommendation formatted EXACTLY as follows:

Title: [A concise title for the recommendation]
Description: [A brief, actionable description of the recommendation]
Category: [One single word category, e.g., StressRelief, Sleep, Focus, MoodBoost]
Reason: [A very short explanation of why this might help with the user's feeling.]

Do not include any introductory or concluding remarks. Just provide the recommendation in the specified format."""
    try:
        model = genai.GenerativeModel(model_name_to_use)
        response = model.generate_content(prompt)
        print(f"--- Raw Gemini Response ---")
        print(response.text)
        print("--- End of Raw Response ---")

        if response.text:
            parts = response.text.strip().split('\n')
            title = "AI Generated Suggestion"
            description = response.text.strip()
            category = "ai_generated"
            reason = "Generated based on your input."

            for part in parts:
                if part.startswith("Title:"):
                    title = part.split(': ')[1].strip()
                elif part.startswith("Description:"):
                    description = part.split(': ')[1].strip()
                elif part.startswith("Category:"):
                    category = part.split(': ')[1].strip()
                elif part.startswith("Reason:"):
                    reason = part.split(': ')[1].strip()

            recommendation = Recommendation(
                title=title,
                description=description,
                category=category,
                reason=reason
            )
            return recommendation

        return None

    except Exception as e:
        print(f"Error generating AI recommendation: {e}")
        return None