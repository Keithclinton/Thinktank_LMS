from rest_framework import viewsets, generics, permissions, status, filters
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, Lesson, Assignment, AssignmentSubmission, Quiz, Question, QuizResult, Progress, Certificate, Article, Webinar, WebinarRegistration, ArticleLike
from .serializers import CourseSerializer, EnrollmentSerializer, LessonSerializer, AssignmentSerializer, AssignmentSubmissionSerializer, QuizSerializer, QuizResultSerializer, CourseListSerializer, CourseDetailSerializer, CertificateSerializer, ArticleSerializer, WebinarSerializer, WebinarRegistrationSerializer
from users.serializers import UserSerializer
from rest_framework.response import Response
from .permissions import IsInstructorOrAdmin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

User = get_user_model()

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class EnrollView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(enrollments__user=self.request.user)

class CourseEnrolledUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['pk']
        return User.objects.filter(enrollments__course_id=course_id)

class UnenrollView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
        if enrollment:
            enrollment.delete()
            return Response({'detail': 'Unenrolled successfully.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuizResultViewSet(viewsets.ModelViewSet):
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'instructor_name']
    
    def get_queryset(self):
        queryset = Course.objects.filter(published=True)
        level = self.request.query_params.get('level')
        instructor = self.request.query_params.get('instructor')
        
        if level:
            queryset = queryset.filter(level__icontains=level)
        if instructor:
            queryset = queryset.filter(instructor_name__icontains=instructor)
        
        return queryset

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(published=True)
    serializer_class = CourseDetailSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id, published=True)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, 
        course=course
    )
    
    if created:
        course.students_count += 1
        course.save()
        
        return Response({
            'message': 'Successfully enrolled in course',
            'enrollment': {
                'id': enrollment.id,
                'course_id': course.id,
                'user_id': request.user.id,
                'enrolled_at': enrollment.enrolled_at,
                'progress': 0
            }
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_progress(request, course_id):
    try:
        course = Course.objects.get(id=course_id, published=True)
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except (Course.DoesNotExist, Enrollment.DoesNotExist):
        return Response({'error': 'Course or enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    lesson_id = request.data.get('lesson_id')
    completed = request.data.get('completed', True)
    
    try:
        lesson = Lesson.objects.get(id=lesson_id, course=course)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
    
    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={'completed': completed}
    )
    
    if not created:
        progress.completed = completed
        if completed:
            progress.completed_at = timezone.now()
        progress.save()
    
    # Update enrollment last_accessed
    enrollment.last_accessed = timezone.now()
    enrollment.save()
    
    # Calculate overall course progress
    total_lessons = course.lessons.count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment, completed=True
    ).count()
    course_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Check if course is completed and issue certificate
    if course_progress == 100:
        certificate, cert_created = Certificate.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'verification_id': f'CERT-{timezone.now().year}-{course.id:03d}',
                'certificate_url': f'/api/certificates/{course.id}/download/'
            }
        )
    
    return Response({
        'message': 'Progress updated',
        'course_progress': course_progress,
        'lesson_completed': completed
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    enrolled = []
    completed = []
    
    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = course.lessons.count()
        completed_lessons = Progress.objects.filter(
            enrollment=enrollment, completed=True
        ).count()
        progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        course_data = {
            'id': course.id,
            'title': course.title,
            'progress': progress,
            'enrolled_at': enrollment.enrolled_at,
            'last_accessed': enrollment.last_accessed,
            'instructor': course.instructor_name,
            'thumbnail': course.thumbnail_url
        }
        
        if progress == 100:
            course_data['status'] = 'completed'
            certificate = Certificate.objects.filter(user=request.user, course=course).first()
            if certificate:
                course_data['completed_at'] = certificate.issued_date
                course_data['certificate_id'] = certificate.id
            completed.append(course_data)
        else:
            course_data['status'] = 'in_progress'
            enrolled.append(course_data)
    
    return Response({
        'enrolled': enrolled,
        'completed': completed
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_certificates(request):
    certificates = Certificate.objects.filter(user=request.user)
    serializer = CertificateSerializer(certificates, many=True)
    return Response({'certificates': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_certificate(request, certificate_id):
    try:
        certificate = Certificate.objects.get(id=certificate_id, user=request.user)
        return Response({
            'certificate_url': certificate.certificate_url,
            'download_url': f'/api/courses/certificates/{certificate_id}/pdf/'
        })
    except Certificate.DoesNotExist:
        return Response({'error': 'Certificate not found'}, status=status.HTTP_404_NOT_FOUND)

class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.filter(status='published')
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'excerpt', 'content', 'tags']
    ordering_fields = ['created_at', 'views_count', 'likes_count']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_article(request, slug):
    try:
        article = Article.objects.get(slug=slug)
        like, created = ArticleLike.objects.get_or_create(
            article=article, 
            user=request.user
        )
        
        if not created:
            like.delete()
            article.likes_count -= 1
            liked = False
        else:
            article.likes_count += 1
            liked = True
        
        article.save(update_fields=['likes_count'])
        
        return Response({
            'liked': liked,
            'likes_count': article.likes_count
        })
    except Article.DoesNotExist:
        return Response({'error': 'Article not found'}, status=404)

class WebinarListCreateView(generics.ListCreateAPIView):
    queryset = Webinar.objects.all()
    serializer_class = WebinarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'presenter']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['scheduled_date']
    
    def perform_create(self, serializer):
        serializer.save(presenter=self.request.user)

class WebinarDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Webinar.objects.all()
    serializer_class = WebinarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_webinar(request, slug):
    try:
        webinar = Webinar.objects.get(slug=slug)
        
        if not webinar.is_registration_open:
            return Response({'error': 'Registration is closed'}, status=400)
        
        registration, created = WebinarRegistration.objects.get_or_create(
            webinar=webinar,
            user=request.user
        )
        
        if created:
            webinar.registered_count += 1
            webinar.save(update_fields=['registered_count'])
            return Response({'message': 'Successfully registered for webinar'})
        else:
            return Response({'error': 'Already registered'}, status=400)
            
    except Webinar.DoesNotExist:
        return Response({'error': 'Webinar not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unregister_webinar(request, slug):
    try:
        webinar = Webinar.objects.get(slug=slug)
        registration = WebinarRegistration.objects.get(webinar=webinar, user=request.user)
        registration.delete()
        
        webinar.registered_count -= 1
        webinar.save(update_fields=['registered_count'])
        
        return Response({'message': 'Successfully unregistered from webinar'})
        
    except (Webinar.DoesNotExist, WebinarRegistration.DoesNotExist):
        return Response({'error': 'Registration not found'}, status=404)
