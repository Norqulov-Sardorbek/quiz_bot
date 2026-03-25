from django.db import models
import secrets
# Create your models here.


def generate_share_code():
    return secrets.token_urlsafe(10)

class CustomUser(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    tg_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    role = models.CharField(max_length=50, default='user')

    def __str__(self):
        return self.username if self.username else str(self.tg_id)
    
    
class Quizes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='quizes')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deadline = models.PositiveIntegerField(default=15)  # seconds
    share_code = models.CharField(max_length=100, unique=True,null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.share_code:
            self.share_code = generate_share_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quizes, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    options = models.JSONField()
    correct_index = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.question[:50]
    
    
class QuizAnswers(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='quiz_answers')
    quiz = models.ForeignKey(Quizes, on_delete=models.CASCADE,related_name='answers')
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    not_answered = models.PositiveIntegerField(default=0)
    total_time = models.FloatField(default=0.0)  

    def __str__(self):
        return f"Answer by {self.user} to {self.quiz}"


class ReadyCount(models.Model):
    message_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    quiz = models.ForeignKey(Quizes, on_delete=models.CASCADE,related_name='ready_messages')
    is_ended = models.BooleanField(default=False)
    count = models.PositiveIntegerField(default=0)
    quiz_starter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='started_quizzes')
    
    def __str__(self):
        return f"{self.chat_id} ready for {self.quiz}"