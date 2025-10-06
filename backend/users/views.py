from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash, get_user_model
from courses.models import Enrollment, Progress, Certificate
from .serializers import (
    RegisterSerializer, UserSerializer, UserProfileSerializer, 
    LoginSerializer, PasswordChangeSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """RESTful endpoint for user profile - handles both GET and PUT"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return Response({'message': 'Password changed successfully'})
        return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    enrolled_courses = enrollments.count()
    
    # Calculate completed courses
    completed_courses = 0
    in_progress_courses = 0
    
    for enrollment in enrollments:
        total_lessons = enrollment.course.lessons.count()
        completed_lessons = Progress.objects.filter(
            enrollment=enrollment, completed=True
        ).count()
        
        if total_lessons > 0 and completed_lessons == total_lessons:
            completed_courses += 1
        elif completed_lessons > 0:
            in_progress_courses += 1
    
    certificates_earned = Certificate.objects.filter(user=request.user).count()
    
    # Recent courses
    recent_courses = []
    for enrollment in enrollments.order_by('-last_accessed')[:5]:
        course = enrollment.course
        total_lessons = course.lessons.count()
        completed_lessons = Progress.objects.filter(
            enrollment=enrollment, completed=True
        ).count()
        progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        recent_courses.append({
            'id': course.id,
            'title': course.title,
            'progress': progress,
            'last_accessed': enrollment.last_accessed,
            'instructor': course.instructor_name
        })
    
    return Response({
        'stats': {
            'enrolled_courses': enrolled_courses,
            'completed_courses': completed_courses,
            'in_progress_courses': in_progress_courses,
            'certificates_earned': certificates_earned
        },
        'recent_courses': recent_courses
    })
