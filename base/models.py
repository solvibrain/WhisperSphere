from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    """
    Represents a topic or category in the platform.

    Attributes:
        name (str): The name of the topic.
        description (str): A brief description of the topic.

    Example:
        >>> topic = Topic(name="Python", description="All things Python")
        >>> topic.save()
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    """
    Represents a chat room or discussion forum.

    Attributes:
        host (User): The user who created the room.
        topic (Topic): The topic associated with the room.
        name (str): The name of the room.
        description (str): A brief description of the room.
        participants (ManyToManyField): Users who are participating in the room.
        followers (ManyToManyField): Users who are following the room.
        is_private (bool): Whether the room is private or public.
        updated (DateTimeField): The last time the room was updated.
        created (DateTimeField): The time the room was created.

    Example:
        >>> room = Room(host=User.objects.get(id=1), topic=Topic.objects.get(id=1), name="Python Discussion")
        >>> room.save()
    """
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participated_rooms', blank=True)
    followers = models.ManyToManyField(User, related_name='followed_rooms', blank=True)
    is_private = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    Represents a tag or keyword.

    Attributes:
        name (str): The name of the tag.

    Example:
        >>> tag = Tag(name="machine learning")
        >>> tag.save()
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    """
    Represents a message or post in a room.

    Attributes:
        user (User): The user who sent the message.
        room (Room): The room where the message was sent.
        body (str): The content of the message.
        updated (DateTimeField): The last time the message was updated.
        created (DateTimeField): The time the message was created.
        upvotes (ManyToManyField): Users who upvoted the message.
        parent (Message): The parent message (for replies).
        tags (ManyToManyField): Tags associated with the message.
        mentions (ManyToManyField): Users mentioned in the message.
        is_pinned (bool): Whether the message is pinned.

    Example:
        >>> message = Message(user=User.objects.get(id=1), room=Room.objects.get(id=1), body="Hello, world!")
        >>> message.save()
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    upvotes = models.ManyToManyField(User, related_name='upvoted_messages', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    tags = models.ManyToManyField(Tag, related_name='messages', blank=True)
    mentions = models.ManyToManyField(User, related_name='mentioned_in', blank=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[:50]

class UserProfile(models.Model):
    """
    Represents a user's profile.

    Attributes:
        user (User): The associated user.
        bio (str): A brief bio of the user.
        interests (ManyToManyField): Topics the user is interested in.
        followers (ManyToManyField): Users who are following the user.
        points (int): The user's points.
        level (int): The user's level.

    Example:
        >>> user_profile = UserProfile(user=User.objects.get(id=1), bio="I love Python!")
        >>> user_profile.save()
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    interests = models.ManyToManyField(Topic, related_name='interested_users', blank=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return self.user.username

class Badge(models.Model):
    """
    Represents a badge or achievement.

    Attributes:
        name (str): The name of the badge.
        description (str): A brief description of the badge.
        icon (ImageField): The icon associated with the badge.
        users (ManyToManyField): Users who have earned the badge.

    Example:
        >>> badge = Badge(name="Python Expert", description="Awarded to users who have demonstrated expertise in Python")
        >>> badge.save()
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    users = models.ManyToManyField(User, related_name='badges', blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Represents an event or meeting.

    Attributes:
        title (str): The title of the event.
        description (str): A brief description of the event.
        room (Room): The room where the event will take place.
        start_time (DateTimeField): The start time of the event.
        end_time (DateTimeField): The end time of the event.
        participants (ManyToManyField): Users who are participating in the event.

    Example:
        >>> event = Event(title="Python Meetup", description="A meetup for Python enthusiasts", room=Room.objects.get(id=1), start_time=datetime.datetime(2023, 3, 15, 18, 0), end_time=datetime.datetime(2023, 3, 15, 20, 0))
        >>> event.save()
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(User, related_name='events', blank=True)

    def __str__(self):
        return self.title

class Notification(models.Model):
    """
    Represents a notification or alert.

    Attributes:
        recipient (User): The user who received the notification.
        notification_type (str): The type of notification (e.g. mention, reply, upvote, etc.).
        actor (User): The user who triggered the notification.
        target (Message or Event): The message or event associated with the notification.
        read (bool): Whether the notification has been read.
        created (DateTimeField): The time the notification was created.

    Example:
        >>> notification = Notification(recipient=User.objects.get(id=1), notification_type='mention', actor=User.objects.get(id=2), target=Message.objects.get(id=1))
        >>> notification.save()
    """
    NOTIFICATION_TYPES = (
        ('mention', 'Mention'),
        ('reply', 'Reply'),
        ('upvote', 'Upvote'),
        ('new_message', 'New Message'),
        ('event', 'Event'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    target = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.actor.username} {self.get_notification_type_display()} {self.recipient.username}"