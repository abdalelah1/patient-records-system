from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from datetime import date,datetime
# Create your models here.


class Patient(models.Model):
        full_name = models.CharField(max_length=50)
        birthdate = models.CharField(max_length=30)
        national_number=models.CharField(max_length=20,unique=True)
        mobile=models.CharField(max_length=15)
        gender=models.CharField(max_length=8)
        user=models.OneToOneField(User,on_delete=models.CASCADE,null=False)
        def __str__(self) :
                return str(self.id)
class Major(models.Model):
       name = models.CharField(max_length=150) 
       def __str__(self) :
                return str(self.name)    
    
class Users(models.Model):
        full_name= models.CharField(max_length=50)
        certificate = models.ImageField()
        birthdate = models.CharField(max_length=30, null=True)
        gender=models.CharField(max_length=8,null=True)
        mobile =  models.CharField(max_length=150, null=True)
        user=models.OneToOneField(User,on_delete=models.CASCADE,null=False)
        major=models.ForeignKey(Major,on_delete=models.CASCADE,null=False)
        active = models.BooleanField(default=False)
        def __str__(self) :
                return str(self.full_name)
class Xray(models.Model):
       image = models.ImageField()
       patient = models.ForeignKey(Patient ,on_delete=models.CASCADE,null=False )
       date_taken = models.DateField(default=date.today)
       doctor = models.ForeignKey(Users ,on_delete=models.CASCADE,null=False )
       Report = models.CharField(max_length=2000 ,null=True)
       
class CategoriesAnalysis(models.Model):
       name =models.CharField(max_length=50)
       def __str__(self) :
                return str(self.name)
class BasicAnalyses(models.Model):
    name = models.CharField(max_length=50)
    natrual_range = models.CharField(max_length=50)
    measurement_unit = models.CharField(max_length=50, null=True)
    its_derivatives = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='derivatives')
    categories_analysis = models.ForeignKey(CategoriesAnalysis, on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return str(self.name)
class Result(models.Model):
       patient=models.ForeignKey(Patient,on_delete=models.CASCADE,null=False )
       analyst= models.ForeignKey( Users,on_delete=models.CASCADE,null=False )
       date = models.DateField(default=date.today)
       analysis_sequence = models.AutoField(primary_key=True)
class Result_details (models.Model):
       analysis_number = models.ForeignKey(BasicAnalyses,on_delete=models.CASCADE,null=False )
       last_value=models.CharField(max_length=100 ,null=True )
       analysis_sequence = models.ForeignKey(Result, on_delete=models.CASCADE,related_name='result_details')
       result = models.CharField(max_length=200)
class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_status = models.BooleanField(max_length=20, default=False)
    

    def __str__(self):
        return f"Request by {self.user.username}"     
