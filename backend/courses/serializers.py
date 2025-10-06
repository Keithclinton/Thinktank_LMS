from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Enrollment, Progress, Certificate, Assignment, AssignmentSubmission, Quiz, QuizResult, Article, Webinar, WebinarRegistration, ArticleLike
from users.serializers import UserSerializer

User = get_user_model()

class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'duration', 'is_completed']
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                user=request.user, 
                course=obj.course
            ).first()
            if enrollment:
                return Progress.objects.filter(
                    enrollment=enrollment, 
                    lesson=obj, 
                    completed=True
                ).exists()
        return False

class CourseListSerializer(serializers.ModelSerializer):
    is_enrolled = serializers.SerializerMethodField()
    instructor = serializers.CharField(source='instructor_name', read_only=True)
    thumbnail = serializers.CharField(source='thumbnail_url', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'duration', 
                 'students_count', 'rating', 'level', 'thumbnail', 'price', 'is_enrolled']
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

class CourseDetailSerializer(serializers.ModelSerializer):
    is_enrolled = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    instructor = serializers.CharField(source='instructor_name', read_only=True)
    thumbnail = serializers.CharField(source='thumbnail_url', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'duration', 
                 'students_count', 'rating', 'level', 'thumbnail', 'price', 
                 'is_enrolled', 'progress', 'lessons']
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
            if enrollment:
                total_lessons = obj.lessons.count()
                completed_lessons = Progress.objects.filter(
                    enrollment=enrollment, completed=True
                ).count()
                return (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        return 0

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_thumbnail = serializers.CharField(source='course.thumbnail_url', read_only=True)
    course_instructor = serializers.CharField(source='course.instructor_name', read_only=True)
    progress = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course_id', 'course_title', 'course_thumbnail', 'course_instructor',
                 'enrolled_at', 'last_accessed', 'progress', 'status']
    
    def get_progress(self, obj):
        total_lessons = obj.course.lessons.count()
        completed_lessons = Progress.objects.filter(
            enrollment=obj, completed=True
        ).count()
        return (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    def get_status(self, obj):
        progress = self.get_progress(obj)
        return 'completed' if progress == 100 else 'in_progress'

class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Certificate
        fields = ['id', 'course_id', 'course_title', 'issued_date', 'certificate_url', 'verification_id']

class CourseSerializer(serializers.ModelSerializer):
    """General CourseSerializer - same as CourseListSerializer"""
    is_enrolled = serializers.SerializerMethodField()
    instructor = serializers.CharField(source='instructor_name', read_only=True)
    thumbnail = serializers.CharField(source='thumbnail_url', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'duration', 
                 'students_count', 'rating', 'level', 'thumbnail', 'price', 'is_enrolled']
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'created_at']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'submitted_at', 'file_url', 'grade', 'feedback']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'order']

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ['id', 'quiz', 'score', 'passed', 'taken_at']

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    is_liked = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'category', 
            'excerpt', 'content', 'featured_image', 'status', 'tags', 'tags_list',
            'read_time', 'views_count', 'likes_count', 'is_liked',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['slug', 'views_count', 'likes_count', 'published_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ArticleLike.objects.filter(article=obj, user=request.user).exists()
        return False
    
    def get_tags_list(self, obj):
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]

class WebinarSerializer(serializers.ModelSerializer):
    presenter = UserSerializer(read_only=True)
    presenter_name = serializers.CharField(source='presenter.get_full_name', read_only=True)
    is_registered = serializers.SerializerMethodField()
    can_register = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Webinar
        fields = [
            'id', 'title', 'slug', 'presenter', 'presenter_name', 'description', 
            'agenda', 'thumbnail_image', 'scheduled_date', 'duration_minutes', 'timezone',
            'registration_status', 'max_attendees', 'registration_deadline',
            'meeting_link', 'meeting_id', 'meeting_passcode', 'recording_url', 
            'recording_available', 'status', 'registered_count', 'attended_count',
            'category', 'tags', 'tags_list', 'is_registered', 'can_register',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'registered_count', 'attended_count']
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return WebinarRegistration.objects.filter(webinar=obj, user=request.user).exists()
        return False
    
    def get_can_register(self, obj):
        return obj.is_registration_open
    
    def get_tags_list(self, obj):
        return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]

class WebinarRegistrationSerializer(serializers.ModelSerializer):
    webinar = WebinarSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WebinarRegistration
        fields = ['id', 'webinar', 'user', 'registered_at', 'attended', 'feedback_rating', 'feedback_comment']
