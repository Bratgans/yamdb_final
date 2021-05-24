from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class RoleUser(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=RoleUser.choices,
        default=RoleUser.USER
    )

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == RoleUser.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == RoleUser.MODERATOR


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Жанр',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=50,
        unique=True,
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        verbose_name='Категория',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=50,
        unique=True
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Произведение'
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(datetime.now().year),
            MinValueValidator(0)
        ]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='titles',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        blank=True
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)

        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
