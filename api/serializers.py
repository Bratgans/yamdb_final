from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title, User

REVIEW_EXIST = 'You have already reviewed this title.'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        exclude = ['review', ]
        read_only_fields = ('author',)
        model = Comment


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        try:
            user = User.objects.get(email=email)
            return user
        except Exception:
            raise serializers.ValidationError({'email': ['invalid email']})



class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TokenSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('email', 'username',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        exclude = ['title', ]
        read_only_fields = ('author',)
        model = Review

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        user = request.user
        my_view = self.context['view']
        title_id = my_view.kwargs['title_id']
        if Review.objects.filter(title=title_id, author=user).exists():
            raise serializers.ValidationError(REVIEW_EXIST)
        return data


class TitleSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    rating = serializers.FloatField(read_only=True)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleListSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    rating = serializers.FloatField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = '__all__'
        model = Title


class ProfileViewSetSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'role',
            'bio',
            'first_name',
            'last_name')


class ProfileUserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField()

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'bio',
                  'first_name',
                  'last_name',
                  'role')
