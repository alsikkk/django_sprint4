from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
TEXT_LENGTH = 256


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=TEXT_LENGTH, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=TEXT_LENGTH,
                            verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=TEXT_LENGTH, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.',
        blank=True,
        null=False
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )

    def clean(self):
        super().clean()
        now = timezone.now()
        pub = self.pub_date if self.pub_date else now

        if pub > now + timedelta(seconds=10):
            raise ValidationError({
                'pub_date': 'Нельзя публиковать пост с датой из будущего.'
            })
        if pub < now - timedelta(minutes=5):
            raise ValidationError({
                'pub_date': 'Пост можно создавать только не старше 5 минут назад.'
            })

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        related_name='comments',
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        blank=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        now = timezone.now()
        created = self.created_at if self.created_at else now

        if created > now + timedelta(seconds=10):
            raise ValidationError({
                'created_at': 'Комментарий не может быть из будущего.'
            })
        if created < now - timedelta(minutes=5):
            raise ValidationError({
                'created_at': 'Комментарий можно создавать только не старше 5 минут назад.'
            })

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:50]