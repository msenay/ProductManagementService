from rest_framework import serializers
from products.models import CustomUser, Product

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

    @staticmethod
    def validate_password(value):
        """
        Ensure that the password is at least 8 characters long.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password should have a minimum of 8 characters.")
        return value

    def create(self, validated_data):
        """
        Create a new user with the provided validated data.
        """
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
