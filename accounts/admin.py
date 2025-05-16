from django.contrib import admin
from .models import Profile, Interest, Recommendation, UserRecommendation, PlannerItem

admin.site.register(Profile)
admin.site.register(Interest)
admin.site.register(Recommendation)
admin.site.register(UserRecommendation)
admin.site.register(PlannerItem)