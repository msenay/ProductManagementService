from rest_framework import serializers
from products.models import CustomUser, Product
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    This serializer handles the validation and creation of users. It ensures
    that the password meets the minimum length requirement and excludes the
    user_id field from being modified by the client.
    """

    class Meta:
        model = CustomUser
        fields = ["user_id", "first_name", "last_name", "email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}, "user_id": {"read_only": True}}

    def validate(self, data):
        """
        Validate username, email, and password. Ensure they are unique and meet the required conditions.
        """
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

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
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
            )
            return user
        except Exception as e:
            logger.error("Error creating user", exc_info=e)
            raise serializers.ValidationError("An error occurred while creating the user.")


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    This serializer converts Product model instances into JSON format
    and handles the deserialization from JSON to Product model instances
    when creating or updating records. It includes all fields of the Product model.

    Attributes:
        model (Product): The model that this serializer handles.
        fields (str): Specifies that all fields in the model should be serialized.
    """

    class Meta:
        model = Product
        fields = "__all__"


class ProductFilterSerializer(serializers.Serializer):
    """
    Serializer for product filtering parameters.

    This serializer validates and processes filtering parameters
    that are passed in the query string for filtering the list of products.
    It checks for valid conditions, gender, brand, sorting, and order values.

    Fields:
        condition (str, optional): Filter products by condition (e.g., 'new', 'used').
            It's optional and can be blank.
        gender (str, optional): Filter products by gender (e.g., 'male', 'female').
            It's optional and can be blank.
        brand (str, optional): Filter products by brand name.
            It's optional and can be blank.
        sort_by (str, optional): Defines the field by which the results will be sorted.
            Default is 'title'.
        order (str, optional): Defines the sort order, either ascending ('asc') or descending ('desc').
            Default is 'asc'.
    """

    condition = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.CharField(required=False, allow_blank=True)
    sort_by = serializers.CharField(required=False, default="title")
    order = serializers.ChoiceField(choices=["asc", "desc"], default="asc")
