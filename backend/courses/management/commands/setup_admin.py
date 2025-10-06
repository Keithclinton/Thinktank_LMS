from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course

class Command(BaseCommand):
    help = 'Setup permanent admin and production-ready course catalog'

    def handle(self, *args, **options):
        User = get_user_model()
        
        self.stdout.write('🚀 Setting up Thinktank LMS Production Environment...')
        
        # Create permanent admin user with YOUR custom credentials
        admin_user, created = User.objects.get_or_create(
            email='keithnyaburi@gmail.com',
            defaults={
                'username': 'Superuser',  # CHANGED from 'Admin' to 'Superuser'
                'first_name': 'Keith',
                'last_name': 'Nyaburi',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created or not admin_user.check_password('ThinktankAdmin2025!'):  # CHANGE THIS to your preferred password
            admin_user.set_password('ThinktankAdmin2025!')  # CHANGE THIS to your preferred password
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✅ Production admin user ready'))
        
        # Create instructor accounts with your preferred credentials
        instructors_data = [
            {
                'username': 'instructor1',  # CHANGE THESE if you want
                'email': 'instructor1@yourdomain.com',  # CHANGE THESE if you want
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'bio': 'PhD in Computer Science, 15+ years industry experience'
            },
            {
                'username': 'instructor2',
                'email': 'instructor2@yourdomain.com',
                'first_name': 'Michael',
                'last_name': 'Davis',
                'bio': 'Former Google engineer, Stanford lecturer'
            },
            {
                'username': 'instructor3',
                'email': 'instructor3@yourdomain.com',
                'first_name': 'Emma',
                'last_name': 'Rodriguez',
                'bio': 'Digital marketing strategist, 10+ years experience'
            }
        ]
        
        instructors = {}
        for instructor_data in instructors_data:
            instructor, created = User.objects.get_or_create(
                email=instructor_data['email'],
                defaults={
                    'username': instructor_data['username'],
                    'first_name': instructor_data['first_name'],
                    'last_name': instructor_data['last_name'],
                    'is_staff': True
                }
            )
            if created:
                instructor.set_password('InstructorPass123!')  # CHANGE THIS if you want
                instructor.save()
            instructors[instructor_data['username']] = instructor
        
        self.stdout.write('✅ Production instructor accounts ready')
        
        # Create permanent, production-ready course catalog
        production_courses = [
            {
                'title': 'Complete Python Programming Bootcamp',
                'description': '''Comprehensive Python programming course designed for professionals and career changers.

**What You'll Master:**
• Python fundamentals and advanced concepts
• Object-oriented programming principles
• Web development with Django framework
• Database integration with PostgreSQL
• API development and testing
• Data analysis with pandas and numpy
• Automated testing and debugging
• Version control with Git
• Cloud deployment strategies

**Career Outcomes:**
This course prepares you for roles as Python Developer, Backend Engineer, or Data Analyst. Graduates have been hired by companies like Google, Microsoft, and Netflix.

**Prerequisites:** Basic computer literacy (no programming experience required)
**Certificate:** Professional completion certificate included''',
                'instructor': 'instructor1',  # Update these to match your instructor usernames
                'price': 299.99,
                'duration': '60 hours',
                'category': 'programming',
                'level': 'beginner',
                'rating': 4.9,
                'students_count': 4892,
                'published': True
            },
            {
                'title': 'Full Stack Web Development Professional',
                'description': '''Industry-standard web development course covering modern frontend and backend technologies.

**Technology Stack:**
• Frontend: React.js, TypeScript, Tailwind CSS
• Backend: Django REST Framework, Node.js
• Database: PostgreSQL, MongoDB
• Cloud: AWS, Google Cloud Platform
• Tools: Docker, CI/CD, Testing frameworks

**Real Projects Included:**
• E-commerce platform with payment integration
• Social media application with real-time features
• Task management system with team collaboration
• Portfolio website with CMS integration

**Career Support:**
• Resume and portfolio review
• Mock interview preparation
• Job placement assistance
• Access to exclusive job board

**Prerequisites:** Basic HTML/CSS knowledge recommended
**Duration:** 12 weeks intensive or 24 weeks part-time''',
                'instructor': 'instructor2',
                'price': 599.99,
                'duration': '120 hours',
                'category': 'programming',
                'level': 'intermediate',
                'rating': 4.8,
                'students_count': 3247,
                'published': True
            },
            {
                'title': 'Digital Marketing Mastery 2025',
                'description': '''Complete digital marketing certification program aligned with industry standards.

**Core Modules:**
• Search Engine Optimization (SEO) - Technical and content optimization
• Pay-Per-Click Advertising (Google Ads, Facebook Ads, LinkedIn Ads)
• Social Media Marketing - Strategy, content creation, community management
• Content Marketing - Blogging, video marketing, podcast marketing
• Email Marketing - Automation, segmentation, conversion optimization
• Analytics & Data - Google Analytics, data interpretation, ROI measurement
• Conversion Rate Optimization - A/B testing, user experience
• Marketing Automation - HubSpot, Marketo, customer journey mapping

**Industry Certifications:**
• Google Analytics certified
• Google Ads certified
• Facebook Blueprint certified
• HubSpot certified

**Real Campaign Management:**
Work on live campaigns with budget allocation and performance tracking.

**Job Placement Rate:** 94% of graduates employed within 6 months
**Average Salary Increase:** 45% for career changers''',
                'instructor': 'instructor3',
                'price': 399.99,
                'duration': '80 hours',
                'category': 'marketing',
                'level': 'beginner',
                'rating': 4.7,
                'students_count': 6183,
                'published': True
            },
            {
                'title': 'Data Science & Machine Learning Professional',
                'description': '''Advanced data science program covering statistical analysis, machine learning, and AI implementation.

**Technical Curriculum:**
• Statistical Analysis - Hypothesis testing, regression analysis, probability
• Data Processing - Python pandas, NumPy, data cleaning techniques
• Machine Learning - Supervised and unsupervised learning algorithms
• Deep Learning - Neural networks, TensorFlow, PyTorch
• Data Visualization - Matplotlib, Seaborn, Plotly, Tableau
• Big Data - Apache Spark, Hadoop, cloud data processing
• MLOps - Model deployment, monitoring, version control
• Natural Language Processing - Text analysis, sentiment analysis
• Computer Vision - Image processing, object detection

**Industry Projects:**
• Predictive analytics for customer churn
• Recommendation system development
• Financial fraud detection system
• Healthcare data analysis project
• Real estate price prediction model

**Career Tracks:**
• Data Scientist
• Machine Learning Engineer
• AI Research Scientist
• Business Intelligence Analyst

**Prerequisites:** Basic Python knowledge and statistics background''',
                'instructor': 'instructor1',
                'price': 799.99,
                'duration': '150 hours',
                'category': 'programming',
                'level': 'advanced',
                'rating': 4.9,
                'students_count': 2156,
                'published': True
            },
            {
                'title': 'UI/UX Design Professional Certification',
                'description': '''Comprehensive design program covering user research, interface design, and prototyping.

**Design Process:**
• User Research - Interviews, surveys, persona development
• Information Architecture - Sitemaps, user flows, wireframing
• Visual Design - Typography, color theory, design systems
• Prototyping - Figma, Adobe XD, InVision, interactive prototypes
• Usability Testing - A/B testing, user feedback, iteration
• Accessibility Design - WCAG guidelines, inclusive design
• Mobile Design - iOS and Android design patterns
• Design Systems - Component libraries, style guides

**Software Mastery:**
• Figma (primary tool)
• Adobe Creative Suite (Photoshop, Illustrator, XD)
• Sketch and InVision
• Principle for animations
• Zeplin for developer handoff

**Portfolio Development:**
• Mobile app redesign project
• E-commerce website design
• Dashboard and data visualization
• Branding and identity project
• Case study presentation skills

**Industry Recognition:**
Course aligned with Google UX Design Certificate standards''',
                'instructor': 'instructor2',
                'price': 499.99,
                'duration': '100 hours',
                'category': 'design',
                'level': 'intermediate',
                'rating': 4.6,
                'students_count': 3891,
                'published': True
            },
            {
                'title': 'Cloud Computing & DevOps Engineering',
                'description': '''Professional-level cloud infrastructure and DevOps practices course.

**Cloud Platforms:**
• Amazon Web Services (AWS) - EC2, S3, RDS, Lambda, CloudFormation
• Google Cloud Platform - Compute Engine, Cloud Storage, BigQuery
• Microsoft Azure - Virtual Machines, Storage, SQL Database
• Multi-cloud strategies and vendor comparison

**DevOps Tools & Practices:**
• Infrastructure as Code - Terraform, CloudFormation, ARM templates
• Containerization - Docker, Kubernetes, container orchestration
• CI/CD Pipelines - Jenkins, GitHub Actions, GitLab CI, Azure DevOps
• Monitoring & Logging - Prometheus, Grafana, ELK stack, CloudWatch
• Configuration Management - Ansible, Chef, Puppet
• Version Control - Git workflows, branching strategies
• Security - IAM, secrets management, compliance frameworks

**Certification Preparation:**
• AWS Solutions Architect Associate
• Google Cloud Professional Cloud Architect  
• Azure Fundamentals and Associate level
• Kubernetes Certified Administrator (CKA)

**Hands-on Labs:**
• Build and deploy scalable web applications
• Implement automated CI/CD pipelines
• Set up monitoring and alerting systems
• Design disaster recovery solutions

**Career Outcomes:**
• DevOps Engineer ($95k-$140k average salary)
• Cloud Solutions Architect ($110k-$160k average salary)
• Site Reliability Engineer ($100k-$150k average salary)''',
                'instructor': 'instructor2',
                'price': 699.99,
                'duration': '130 hours',
                'category': 'programming',
                'level': 'advanced',
                'rating': 4.8,
                'students_count': 1874,
                'published': True
            }
        ]
        
        courses_created = 0
        for course_data in production_courses:
            instructor = instructors[course_data.pop('instructor')]
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={**course_data, 'instructor': instructor}
            )
            if created:
                courses_created += 1
                self.stdout.write(f"✅ Created: {course.title}")
        
        # Display setup completion with YOUR credentials (FIX THIS SECTION)
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('🎉 THINKTANK LMS PRODUCTION READY! 🎉'))
        self.stdout.write('='*70)
        self.stdout.write(f'📚 {courses_created} professional courses available')
        self.stdout.write(f'👨‍🏫 3 expert instructors with industry credentials')
        self.stdout.write(f'💼 Career-focused curriculum with job placement support')
        self.stdout.write('\n🔐 YOUR ADMIN ACCESS (EMAIL LOGIN):')
        self.stdout.write(f'🌐 URL: https://thinktank-lms-backend-536444006215.africa-south1.run.app/admin/')
        self.stdout.write(f'📧 Email: keithnyaburi@gmail.com')  # CHANGED to match your email
        self.stdout.write(f'🔑 Password: ThinktankAdmin2025!')     # CHANGED to match your password
        self.stdout.write('\n💡 INSTRUCTOR EMAIL LOGINS:')
        self.stdout.write(f'👩‍💻 instructor1@yourdomain.com / InstructorPass123!')
        self.stdout.write(f'👨‍💼 instructor2@yourdomain.com / InstructorPass123!')
        self.stdout.write(f'👩‍💼 instructor3@yourdomain.com / InstructorPass123!')
        self.stdout.write('\n🚀 Production environment ready for real users!')
        self.stdout.write('='*70)