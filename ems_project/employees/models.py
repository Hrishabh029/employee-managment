from django.db import models
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('FT', 'Full-Time'),
        ('PT', 'Part-Time'),
        ('CT', 'Contract')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    employment_type = models.CharField(max_length=2, choices=EMPLOYMENT_TYPE_CHOICES)
    
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ('ID', 'Identity Proof'),
        ('EDU', 'Educational Certificate'),
        ('EXP', 'Experience Certificate'),
        ('OTHER', 'Other')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=5, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_document_type_display()}"

class Performance(models.Model):
    PERFORMANCE_CATEGORIES = [
        ('TECHNICAL', 'Technical Skills'),
        ('COMMUNICATION', 'Communication'),
        ('TEAMWORK', 'Teamwork'),
        ('LEADERSHIP', 'Leadership'),
        ('OVERALL', 'Overall Performance')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_records')
    review_date = models.DateField()
    reviewer = models.ForeignKey(Employee, 
                                 on_delete=models.SET_NULL, 
                                 null=True, 
                                 related_name='performance_reviews_conducted')
    
    # Detailed performance scoring
    technical_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    communication_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    teamwork_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    leadership_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Calculated overall score
    overall_score = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Detailed feedback
    detailed_feedback = models.TextField(blank=True)
    
    # Performance category for targeted development
    primary_development_category = models.CharField(
        max_length=20, 
        choices=PERFORMANCE_CATEGORIES, 
        default='OVERALL'
    )
    
    # Goals and action items
    development_goals = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-review_date']
        unique_together = ['employee', 'review_date']

    def save(self, *args, **kwargs):
        # Automatically calculate overall score
        self.overall_score = (
            self.technical_score + 
            self.communication_score + 
            self.teamwork_score + 
            self.leadership_score
        ) / 4

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} Performance Review - {self.review_date}"
