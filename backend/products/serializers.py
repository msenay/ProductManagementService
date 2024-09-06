from rest_framework import serializers
from products.models import CustomUser, Product
from tasks.product import logger


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    This serializer handles the validation and creation of users. It ensures
    that the password meets the minimum length requirement and excludes the
    user_id field from being modified by the client.
    """
    class Meta:
        model = CustomUser
        fields = ['user_id', 'first_name', 'last_name', 'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}, 'user_id': {'read_only': True}}


    def validate(self, data):
        """
        Validate username, email, and password. Ensure they are unique and meet the required conditions.
        """
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        # Check password validity
        if len(password) < 4:
            raise serializers.ValidationError({"password": "Password should have a minimum of 4 characters."})

        return data

    def create(self, validated_data):
        """
        Create a new user with the provided validated data.
        """
        try:
            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            return user
        except Exception as e:
            logger.error(f"Error creating user", exc_info=e)
            raise serializers.ValidationError("An error occurred while creating the user.")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
