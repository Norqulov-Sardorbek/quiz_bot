from django.contrib import admin
from .models import CustomUser, Quizes, QuizQuestion, QuizAnswers, ReadyCount


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "tg_id", "username", "role")
    search_fields = ("tg_id", "username")
    list_filter = ("role",)


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1


@admin.register(Quizes)
class QuizesAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "deadline", "share_code")
    search_fields = ("title", "share_code")
    inlines = [QuizQuestionInline]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "short_question", "correct_index")
    search_fields = ("question",)
    list_filter = ("quiz",)

    def short_question(self, obj):
        return obj.question[:50]


@admin.register(QuizAnswers)
class QuizAnswersAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "quiz",
        "correct_answers",
        "wrong_answers",
        "not_answered",
        "total_time",
    )
    list_filter = ("quiz", "user")
    search_fields = ("user__username", "quiz__title")


@admin.register(ReadyCount)
class ReadyCountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat_id",
        "quiz",
        "count",
        "is_ended",
        "quiz_starter",
    )
    list_filter = ("is_ended", "quiz")
    search_fields = ("chat_id",)