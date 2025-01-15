from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from django.core.paginator import Paginator
from users.serializers import UserRegistrationSerializer, UserLoginSerializer, ReportedUserSpamSerializer, SearchUserSerializer, RegisteredUserContactSerializer
from users.models import CustomUser, RegisteredUserContact, ReportedUserSpam

class UserRegistrationView(APIView):
    # Allow unrestricted access to this endpoint
    permission_classes = [AllowAny]
    # API Throttling applied to limit the number of requests from users
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        # Deserialize the request data
        serializer = UserRegistrationSerializer(data=request.data)
        # Check if the data is valid
        if serializer.is_valid():
            # Save the validated data
            serializer.save()
            # Return a success response with a 201 status code
            return Response({"message": "User registered successfully", 
                            }, status=status.HTTP_201_CREATED)
        # If the data is invalid return an error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    # Unrestricted access to this endpoint
    permission_classes = [AllowAny]
    # API Throttling applied to limit the number of requests from users
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        # Deserialize the data
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        # Extract username and password from validated data
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        # Authenticate the user using the provided credentials
        user_object = authenticate(username=username, password=password)
        if user_object:
            # If authentication is successful generate auth token and send the response
            token, _ = Token.objects.get_or_create(user=user_object)
            return Response({"message": f"token {token.key}"}, status=status.HTTP_201_CREATED)
        
        # If authentication fails return a 401 response 
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class MarkPhoneNumberAsSpamView(APIView):
    # Allows access only to authenticated users
    permission_classes = [IsAuthenticated]
    # API Throttling applied to limit the number of requests from users
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        # Deserialize the data
        serializer = ReportedUserSpamSerializer(data=request.data)

        if serializer.is_valid():
            # Extract the phone number from the validated data
            phone_number = serializer.validated_data.get('phone_number')
            # Get the currently authenticated user
            user = request.user

            # Check if the user has already marked this number as spam
            if ReportedUserSpam.objects.filter(phone_number=phone_number, marked_by=user.id).exists():
                return Response({
                    "message": "You have already marked this number as spam."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create a new spam entry with the current user who marked it
            spam = ReportedUserSpam.objects.create(
                phone_number=phone_number, 
                marked_by=user
            )

            # Invalidate cache
            cache.clear()

            spam_serializer = ReportedUserSpamSerializer(spam)
            # Return a success response
            return Response({
                "message": f"The number {phone_number} has been marked as spam.",
                "spam": spam_serializer.data 
            }, status=status.HTTP_201_CREATED)
        # If the incoming data is invalid, return a 400 response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SearchUserByUserNameView(APIView):
    # Only authenticated users can access this view
    permission_classes = [IsAuthenticated]
    # API Throttling applied to limit the number of requests from users
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        # Get the 'name' query parameter from the URL
        search_query = request.query_params.get('name', '').strip()
        # If 'name' is not provided, return an error
        if not search_query:
            return Response({"error": "Name query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the page number and results per page (default set to 1 and 2 respectively)
        page_number = request.query_params.get('page', 1)
        result_size = request.query_params.get('result_size', 2)

        try:
            result_size = int(result_size)
        except ValueError:
            return Response({"error": "'result_size' must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure that 'result_size' is greater than 0
        if result_size <= 0:
            return Response({"error": "'result_size' must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

        # Check cache
        cache_key = f"user_search_{search_query}_page_{page_number}_size_{result_size}"
        cached_results = cache.get(cache_key)

        if cached_results:
            return Response(cached_results, status=status.HTTP_200_OK)

        # Search for usernames that start with the query string
        results_start = CustomUser.objects.filter(username__istartswith=search_query)
        # Search for usernames that contain the query string
        results_contain = CustomUser.objects.filter(
                                                    username__icontains=search_query
                                                    ).exclude(username__istartswith=search_query)
        # Combine both result sets
        results = list(results_start) + list(results_contain)

        # Add pagination
        paginator = Paginator(results, result_size) 
        page_obj = paginator.get_page(page_number)

        response_data = []
        for user in page_obj:
            # Calculate spam likelihood based on count
            spam_count = ReportedUserSpam.objects.filter(phone_number=user.phone_number).count()
            spam_likelihood = min(1.0, spam_count / 10)  
            user_data = {
                "username": user.username,
                "phone_number": user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            }
            # email is displayed if person is a registered user and
            # user who is searching is in the person’s contact list
            if RegisteredUserContact.objects.filter(contact_of=request.user, phone_number=user.phone_number).exists():
                user_data["email"] = user.email

            # Serialize the user data
            user_serializer = SearchUserSerializer(user_data)
            response_data.append(user_serializer.data)
        
        # Cache the response for 100 seconds
        cache.set(cache_key, response_data, timeout=100)

        # Return the paginated search results
        return Response({
            "results": response_data,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_results": paginator.count,
            "results_per_page": result_size
        }, status=status.HTTP_200_OK)



class SearchUserByPhoneNumberView(APIView):
    # Only authenticated users can access this view
    permission_classes = [IsAuthenticated]
    # API Throttling applied to limit the number of requests from users
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        # Get the 'phone_number' query parameter from the request
        phone_number = request.query_params.get('phone_number', '').strip()
        
        # Return an error response if 'phone_number' is not provided
        if not phone_number:
            return Response({"error": "Phone number query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        page_number = request.query_params.get('page', 1)
        result_size = request.query_params.get('result_size', 2)

        try:
            result_size = int(result_size)
        except ValueError:
            return Response({"error": "'result_size' must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        if result_size <= 0:
            return Response({"error": "'result_size' must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

        # Check cache for exisiting data
        cache_key = f"user_phone_search_{phone_number}_page_{page_number}_size_{result_size}"
        cached_data = cache.get(cache_key)

        # If the results are cached return the cached data directly
        # if cached_data:
        #     return Response(cached_data, status=status.HTTP_200_OK)
        
        # Search for user with the given phone number in the CustomUser model
        user = CustomUser.objects.filter(phone_number=phone_number).first()

        if user:
            # Calculate spam likelihood based on spam count
            spam_count = ReportedUserSpam.objects.filter(phone_number=user.phone_number).count()
            spam_likelihood = min(1.0, spam_count / 10)  
            user_data = {
                "username": user.username,
                "phone_number": user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            }
            # email is displayed if person is a registered user and
            # user who is searching is in the person’s contact list
            if RegisteredUserContact.objects.filter(contact_of=request.user, phone_number=user.phone_number).exists():
                user_data["email"] = user.email

            # Serialize the user data and cache it
            serializer = SearchUserSerializer(user_data)
            cache.set(cache_key, serializer.data, timeout=600)

            return Response(serializer.data, status=status.HTTP_200_OK)

        # If the phone number is not in CustomUser search in RegisteredUserContact model
        contacts = RegisteredUserContact.objects.filter(phone_number=phone_number)
        # If no contacts are found, return a 404 response
        if not contacts:
            return Response({"message": "No results found for this phone number."}, status=status.HTTP_404_NOT_FOUND)
        
        # Apply pagination
        paginator = Paginator(contacts, result_size)
        page_obj = paginator.get_page(page_number)

        response_data = []
        for contact in page_obj:
            spam_count = ReportedUserSpam.objects.filter(phone_number=contact.phone_number).count()
            spam_likelihood = min(1.0, spam_count / 10)
            user_data = {
                "contact_name": contact.contact_name,
                "phone_number": contact.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            }
            response_data.append(user_data)
        
        # Cache the results
        cache.set(cache_key, response_data, timeout=100)
        # Return the paginated results in the response
        return Response({
            "results": response_data,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_results": paginator.count,
            "results_per_page": result_size
        }, status=status.HTTP_200_OK)
    


class CreateContactView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        data = request.data.copy() 
        data['contact_of'] = request.user.id
        serializer = RegisteredUserContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)