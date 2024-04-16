from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    class Meta():
        app_label = 'example'
        db_table = 'User'


class Catalog(models.IntegerChoices):
    Grocery = 0, 'Grocery'
    Entertainment = 1, 'Entertainment'
    Transportation = 2, 'Transportation'
    Housing = 3, 'Housing'
    Medical = 4, 'Medical'
    Education = 5, 'Education'
    Investment = 6, 'Investment'
    Other = 7, 'Other'

    def __str__(self):
        return self.name


class Record_Type(models.IntegerChoices):
    In = 0, 'In'
    Out = 1, 'Out'
class Record(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    Date = models.DateField()
    Category = models.IntegerField(choices=Catalog.choices)
    description = models.TextField()
    type = models.IntegerField(choices=Record_Type.choices)
    Amount = models.DecimalField(max_digits=10, decimal_places=2,  validators=[MinValueValidator(0.00)])

    class Meta():
        app_label = 'example'
        db_table = 'Record'

class Fund(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    Budget = models.DecimalField(max_digits=10, decimal_places=2)
    Rest = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta():
        app_label = 'example'
        db_table = 'Fund'

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    report_detail = models.CharField(max_length=255)
    class Meta():
        app_label = 'example'
        db_table = 'Report'
