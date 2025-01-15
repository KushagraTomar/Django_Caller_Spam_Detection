from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


##############################################################################
# CustomUser model that extends the AbstractUser
# Adds phone_number field as unique identifier along with an optional 'email'
##############################################################################
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True) # optional field

    REQUIRED_FIELDS = ['phone_number'] 
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username    


###################################################################################  
# RegisteredUserContact model that links a registered user to their contacts
# Stores information about contacts including contact name, phone number, and email
###################################################################################
class RegisteredUserContact(models.Model):
    id = models.AutoField(primary_key=True)
    contact_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True) # optional
    contact_of = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.contact_name} - {self.phone_number}"    


########################################################################
# ReportedUserSpam model to track phone numbers marked as spam by users
# Stores the phone number and the user who reported phonenumber as spam
########################################################################
class ReportedUserSpam(models.Model):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} marked as spam by {self.marked_by.username}"
    
