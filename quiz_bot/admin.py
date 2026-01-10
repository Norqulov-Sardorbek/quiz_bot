from django.contrib import admin
from quiz_bot.models import *
# Register your models here.


admin.site.register(CustomUser)
admin.site.register(Quizes)
admin.site.register(QuizQuestion)
admin.site.register(QuizAnswers)
admin.site.register(ReadyCount)

