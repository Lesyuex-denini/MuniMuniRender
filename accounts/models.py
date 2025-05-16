from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined = models.DateField(auto_now_add=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    status = models.CharField(max_length=20, default='Active')
    timezone = models.CharField(max_length=50, blank=True, null=True, default='UTC')
    preferred_self_care_hours = models.CharField(max_length=100, blank=True, null=True)
    interests = models.ManyToManyField('Interest', blank=True)
    notification_preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    CATEGORY_CHOICES = [
        ('all', 'All'),
        ('stress_relief', 'Stress Relief'),
        ('sleep', 'Sleep'),
        ('focus', 'Focus'),
        
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    reason = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='all',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recommendation')

    def __str__(self):
        return f"{self.user.username} - {self.recommendation.title}"


class PlannerItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recommendation', 'scheduled_date', 'scheduled_time')

    def __str__(self):
        return f"{self.user.username} - {self.recommendation.title} ({self.scheduled_date})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print("create_user_profile signal triggered!")  
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    print("save_user_profile signal triggered!") 
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)