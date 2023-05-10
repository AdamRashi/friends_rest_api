from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ManyToManyField


class User(AbstractUser):
    friends = ManyToManyField("self")


class FriendRequest(models.Model):
    PENDING = "P"
    ACCEPTED = "A"
    REJECTED = "R"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    )

    sender = models.ForeignKey(
        User, related_name="friend_requests_sent", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="friend_requests_received", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
