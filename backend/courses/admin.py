from django.contrib import admin
from .models import (
    Course, Lesson, Enrollment, Progress, Certificate, Assignment, 
    AssignmentSubmission, Quiz, Question, Choice, QuizResult, Note, Video,
    Article, Webinar, WebinarRegistration, ArticleLike
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor_name', 'price', 'level', 'students_count', 'rating', 'published', 'created_at']
    list_filter = ['level', 'published', 'created_at', 'category']
    search_fields = ['title', 'description', 'instructor_name']
    list_editable = ['price', 'published', 'rating']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category', 'level')
        }),
        ('Instructor', {
            'fields': ('instructor', 'instructor_name')
        }),
        ('Course Details', {
            'fields': ('price', 'duration', 'thumbnail_url', 'preview_video_url')
        }),
        ('Statistics', {
            'fields': ('students_count', 'rating', 'published'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration']
    list_filter = ['course']
    search_fields = ['title', 'content']
    list_editable = ['order']
    ordering = ['course', 'order']
    
    fieldsets = (
        ('Lesson Details', {
            'fields': ('title', 'course', 'order', 'duration')
        }),
        ('Content', {
            'fields': ('content',)
        })
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'last_accessed']
    list_filter = ['enrolled_at', 'course']
    search_fields = ['user__email', 'user__username', 'course__title']
    readonly_fields = ['enrolled_at', 'last_accessed']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'get_course', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'completed_at', 'enrollment__course']
    search_fields = ['enrollment__user__email', 'lesson__title']
    readonly_fields = ['completed_at']
    
    def get_user(self, obj):
        return obj.enrollment.user.email
    get_user.short_description = 'User'
    get_user.admin_order_field = 'enrollment__user__email'
    
    def get_course(self, obj):
        return obj.enrollment.course.title
    get_course.short_description = 'Course'
    get_course.admin_order_field = 'enrollment__course__title'

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'issued_date', 'verification_id']
    list_filter = ['issued_date', 'course']
    search_fields = ['user__email', 'course__title', 'verification_id']
    readonly_fields = ['issued_date', 'verification_id']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'status_indicator', 'created_at']
    list_filter = ['course', 'due_date', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
    
    def status_indicator(self, obj):
        from django.utils import timezone
        if obj.due_date:
            if obj.due_date < timezone.now():
                return "🔴 Overdue"
            elif obj.due_date < timezone.now() + timezone.timedelta(days=7):
                return "🟡 Due Soon"
            else:
                return "🟢 Active"
        return "📅 No Due Date"
    status_indicator.short_description = 'Status'

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'user', 'submitted_at', 'grade', 'graded_status']
    list_filter = ['submitted_at', 'assignment__course', 'grade']
    search_fields = ['user__email', 'assignment__title']
    readonly_fields = ['submitted_at']
    
    def graded_status(self, obj):
        if obj.grade is not None:
            return f"✅ {obj.grade}"
        return "⏳ Pending"
    graded_status.short_description = 'Graded'

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'question_count']
    list_filter = ['course']
    search_fields = ['title', 'description']
    list_editable = ['order']
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_preview', 'quiz', 'type', 'choice_count']
    list_filter = ['type', 'quiz__course']
    search_fields = ['question_text']
    
    def question_text_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_preview.short_description = 'Question'
    
    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = 'Choices'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__quiz__course']
    search_fields = ['choice_text', 'question__question_text']
    list_editable = ['is_correct']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'user', 'score', 'passed', 'taken_at']
    list_filter = ['passed', 'taken_at', 'quiz__course']
    search_fields = ['user__email', 'quiz__title']
    readonly_fields = ['taken_at']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'course']
    list_filter = ['course']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Note Content'

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'url_preview']
    list_filter = ['course']
    search_fields = ['title', 'url']
    
    def url_preview(self, obj):
        return f"🎥 {obj.url[:30]}..." if len(obj.url) > 30 else f"🎥 {obj.url}"
    url_preview.short_description = 'Video URL'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views_count', 'likes_count', 'created_at']
    list_filter = ['status', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'likes_count', 'created_at', 'updated_at', 'published_at']
    list_editable = ['status', 'category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image', 'tags', 'read_time')
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ['title', 'presenter', 'scheduled_date', 'status', 'registered_count', 'registration_status']
    list_filter = ['status', 'registration_status', 'scheduled_date', 'presenter']
    search_fields = ['title', 'description', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['registered_count', 'attended_count', 'created_at', 'updated_at']
    list_editable = ['status', 'registration_status']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'presenter', 'status', 'category')
        }),
        ('Content', {
            'fields': ('description', 'agenda', 'thumbnail_image', 'tags')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'duration_minutes', 'timezone')
        }),
        ('Registration', {
            'fields': ('registration_status', 'max_attendees', 'registration_deadline', 'registered_count')
        }),
        ('Meeting Details', {
            'fields': ('meeting_link', 'meeting_id', 'meeting_passcode'),
            'classes': ('collapse',)
        }),
        ('Recording', {
            'fields': ('recording_url', 'recording_available'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('attended_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.presenter = request.user
        super().save_model(request, obj, form, change)

@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    list_display = ['webinar', 'user', 'registered_at', 'attended', 'feedback_rating']
    list_filter = ['attended', 'feedback_rating', 'registered_at', 'webinar']
    search_fields = ['webinar__title', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['registered_at']

@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['article__title', 'user__email']
    readonly_fields = ['created_at']

# Customize the admin site
admin.site.site_header = "Thinktank LMS Admin"
admin.site.site_title = "Thinktank LMS"
admin.site.index_title = "Welcome to Thinktank LMS Administration"