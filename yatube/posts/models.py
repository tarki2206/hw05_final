from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

SYMBOLS_LIMIT = 15


class Group(models.Model):
    title = models.CharField(verbose_name='title', max_length=200)
    slug = models.SlugField(verbose_name='slug', unique=True)
    description = models.TextField(verbose_name='description')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='content', help_text='just text')
    pub_date = models.DateTimeField(verbose_name='date', auto_now_add=True)
    author = models.ForeignKey(User,
                               verbose_name='author',
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group,
                              verbose_name='group',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              help_text='foreign key field')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:SYMBOLS_LIMIT]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               verbose_name='author',
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.text[50]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')
