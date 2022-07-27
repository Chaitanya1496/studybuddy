from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True, unique=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# Create your models here.
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # A topic can have multiple rooms, but a room can have only one topic
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) # blank = True specifies that when a user saves data, the form could be empty
    # We used related_name, because the User has already been referenced and linked with host
    # Thus, we can't use it, hence we created another name
    # blank = True, to submit a form if its blank without checking
    # The below step also created a new table in the db with name - base_room_participants
    # The columns there are - id (default comes), room_id, user_id
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # auto_now saves the latest date time field of the instance
    # auto_now_add saves the date time when the instance was created

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
        
class Message(models.Model):
    # one to many relationship between room and message

    # One to many relationship
    # A user can have many messages, but a message will be linked to only one User
    user = models.ForeignKey(User, on_delete=models.CASCADE) 

    # Here we are specifying that this room will be the foreign key to the parent Room
    # on_delete = models.SET_NULL - when the room is deleted, set all the instances of room to NULL
    # on_delete = models.CASCADE - when the room is deleted, delete all the room
    # room = models.ForeignKey(Room, on_delete=models.SET_NULL)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]