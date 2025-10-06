from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings  # Add this missing import

User = get_user_model()

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('business', 'Business'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('technology', 'Technology'),
        ('other', 'Other'),
    ]
    
    # Existing fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    instructor_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add missing fields for admin
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    published = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0, help_text="Rating out of 5")
    students_count = models.IntegerField(default=0)
    thumbnail_url = models.URLField(blank=True, null=True)
    preview_video_url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Lesson(models.Model):
    course = models.ForeignKey('Course', related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    duration = models.CharField(max_length=20, blank=True)  # e.g., "45 minutes"
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issued_date = models.DateTimeField(auto_now_add=True)
    verification_id = models.CharField(max_length=50, unique=True)
    certificate_url = models.URLField(blank=True)

class Assignment(models.Model):
    course = models.ForeignKey('Course', related_name='assignments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='submissions', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(blank=True, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

class Quiz(models.Model):
    course = models.ForeignKey('Course', related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    QUESTION_TYPE_CHOICES = (('mcq', 'Multiple Choice'), ('short', 'Short Answer'))
    type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='mcq')

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField(default=False)
    taken_at = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    course = models.ForeignKey(Course, related_name='notes', on_delete=models.CASCADE)
    content = models.TextField()

class Video(models.Model):
    course = models.ForeignKey(Course, related_name='videos', on_delete=models.CASCADE)
    url = models.URLField()
    title = models.CharField(max_length=255)

class Article(models.Model):
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('business', 'Business'),
        ('education', 'Education'),
        ('health', 'Health'),
        ('lifestyle', 'Lifestyle'),
        ('finance', 'Finance'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    excerpt = models.TextField(max_length=300, help_text="Brief description of the article")
    content = models.TextField()
    featured_image = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    read_time = models.IntegerField(default=5, help_text="Estimated read time in minutes")
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)

class Webinar(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    REGISTRATION_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('full', 'Full'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    presenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webinars')
    description = models.TextField()
    agenda = models.TextField(blank=True, help_text="Webinar agenda/outline")
    thumbnail_image = models.URLField(blank=True, null=True)
    
    # Date and time
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Registration
    registration_status = models.CharField(max_length=20, choices=REGISTRATION_STATUS_CHOICES, default='open')
    max_attendees = models.IntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Meeting details
    meeting_link = models.URLField(blank=True, help_text="Zoom/Teams/Meet link")
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_passcode = models.CharField(max_length=50, blank=True)
    
    # Recording
    recording_url = models.URLField(blank=True, null=True)
    recording_available = models.BooleanField(default=False)
    
    # Status and stats
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    registered_count = models.IntegerField(default=0)
    attended_count = models.IntegerField(default=0)
    
    # Tags and category
    category = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_registration_open(self):
        now = timezone.now()
        if self.registration_deadline and now > self.registration_deadline:
            return False
        if self.max_attendees and self.registered_count >= self.max_attendees:
            return False
        return self.registration_status == 'open'

class WebinarRegistration(models.Model):
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webinar_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    feedback_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    feedback_comment = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('webinar', 'user')
        
    def __str__(self):
        return f"{self.user.email} - {self.webinar.title}"

class ArticleLike(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('article', 'user')
        
    def __str__(self):
        return f"{self.user.email} likes {self.article.title}"
