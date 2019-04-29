from django.db import models


class Booking(models.Model):
    Name = models.CharField(null=False,max_length=200)
    Time = models.TimeField(null=False)
    Mail = models.EmailField(null=False)
    ContactNumber = models.CharField(null=False,max_length=200)
    Date = models.DateField(null=False)
    photographers_needed = models.IntegerField(null=True)
    hours = models.IntegerField(null=True)
    Description = models.TextField(null=False)
    Mark_Completed = models.BooleanField()

    def __str__(self):
        return self.Name


