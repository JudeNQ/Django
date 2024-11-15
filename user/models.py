from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

'''
# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length=200)
    user_email = models.CharField(max_length=200)
    user_password = models.CharField(max_length=200)
    
class Event(models.Model):
    event_name = models.CharField(max_length=200)
    event_time = models.TimeField("Event time")
    event_date = models.DateTimeField("Event date")
    event_desc = models.CharField(max_length=320)
'''

# Custom User model to integrate with Django's authentication system
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)  # To track if the account is verified
    profile_icon = models.ImageField(upload_to='profile_icons/', blank=True, null=True)  # For random or user-assigned icons
    location = models.CharField(max_length=255, blank=True, null=True)  # Optional user location
    biography = models.TextField(blank=True, null=True)  # User biography

    # Adding events and organizations count to the user model
    events_count = models.PositiveIntegerField(default=0)
    organizations_count = models.PositiveIntegerField(default=0)

    # Meta information for ordering in the admin
    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username


# Model to store a user's calendar schedule
class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Meta info
    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} ({self.user.username})"


# Model to manage events, including creation by organizations
class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')  # Creator of the event

    # Meta information
    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.name} on {self.date}"


# Model to track event subscriptions by users
class EventSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'event')  # Each user should only subscribe to an event once
        ordering = ['subscribed_on']

    def __str__(self):
        return f"{self.user.username} subscribed to {self.event.name}"