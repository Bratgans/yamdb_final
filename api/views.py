from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb import settings

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import IsAdmin, IsAuthor, IsModerator, IsReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ProfileUserSerializer,
                          ProfileViewSetSerializer, ReviewSerializer,
                          TitleListSerializer, TitleSerializer,
                          TokenSerializer, UserCreateSerializer)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
    }


class CLDViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    pass


class CategoryViewSet(CLDViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | IsReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsReadOnly | IsModerator | IsAuthor]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title=self.kwargs['title_id'],
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title=self.kwargs['title_id'],
        )
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(CLDViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin | IsReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class TokenCreate(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, _ = User.objects.get_or_create(
            email=request.data['email'], username=request.data['username']
        )
        token = default_token_generator.make_token(obj)
        email = request.data['email']
        subject = 'registration'
        message = f'Для активации аккаунта воспользайтесь токеном: {token}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return Response({'success': 'check you email'})


class UserCreate(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': ['invalid confirmation_code']})
        response = get_tokens_for_user(user)
        return Response(response, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsReadOnly | IsModerator | IsAuthor]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    permission_classes = [IsAdmin | IsReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleListSerializer
        return TitleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdmin, )
    serializer_class = ProfileViewSetSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('email', )
    lookup_field = 'username'

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[
        IsAuthenticated,
    ])
    def me(self, request, username=None):
        post = get_object_or_404(User, email=request.user)
        serializer = ProfileUserSerializer(
            post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_403_FORBIDDEN)


class UserProfileDetail(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = get_object_or_404(User, email=request.user)
        serializer = ProfileUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        post = get_object_or_404(User, email=request.user)
        serializer = ProfileUserSerializer(
            post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)
