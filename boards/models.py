from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class List(models.Model):
    title = models.CharField(max_length=200)
    order = models.FloatField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lists',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Card(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    list = models.ForeignKey('List', on_delete=models.CASCADE, related_name='cards')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards',
        null=True,
        blank=True
    )
    order = models.IntegerField(default=0)
    members = models.ManyToManyField(User, related_name='assigned_cards', blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    due_date_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Board(models.Model):
    title = models.CharField(max_length=200)
    background = models.CharField(max_length=50, default='#0079bf')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='board_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Label(models.Model):
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='labels',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Checklist(models.Model):
    title = models.CharField(max_length=255)
    card = models.ForeignKey('Card', related_name='checklists', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChecklistItem(models.Model):
    checklist = models.ForeignKey(
        'Checklist', 
        related_name='items', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def clean(self):
        if not self.checklist:
            raise ValidationError('Checklist is required')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Attachment(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='attachments/')
    url = models.URLField(blank=True)
    card = models.ForeignKey(Card, related_name='attachments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CardLocation(models.Model):
    card = models.OneToOneField(Card, related_name='location', on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    place_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.card.title} - {self.place_name}"

class CardMember(models.Model):
    card = models.ForeignKey('Card', related_name='card_members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='card_memberships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('card', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.card.title}"

class CardDate(models.Model):
    card = models.OneToOneField('Card', related_name='card_date', on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dates for {self.card.title}"

class Comment(models.Model):
    card = models.ForeignKey('Card', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.card.title}'
