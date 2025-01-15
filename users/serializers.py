from rest_framework import serializers
from users.models import CustomUser, RegisteredUserContact, ReportedUserSpam

######################################
# Serializer for user registration
# Handles validation and user creation
######################################
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'phone_number', 'email']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', None),
        )
        return user


#############################################
# Serializer for user login 
# Handles validation of username and password
#############################################  
class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    
    

##############################################################
# Serializer for RegisteredUserContact model
# Handles validation and serialization of user contact details  
##############################################################  
class RegisteredUserContactSerializer(serializers.ModelSerializer):
    contact_of = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    
    class Meta:
        model = RegisteredUserContact 
        fields = ["contact_name", "phone_number", "email", "contact_of"]


###########################################################################
# Serializer for ReportedUserSpam model
# Handles validation and serialization for reporting a phone number as spam
###########################################################################
class ReportedUserSpamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedUserSpam 
        fields = ["phone_number", "marked_by", "created_at"]
        read_only_fields = ["marked_by", "created_at"]


############################################################
# Serializer for user search using username and phonenumber
############################################################
class SearchUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=15)
    spam_likelihood = serializers.FloatField()
    email = serializers.EmailField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'spam_likelihood', 'email']

