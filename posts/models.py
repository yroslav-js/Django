from django.db import models
from django.contrib.auth import get_user_model
from crum import get_current_user


User = get_user_model()


class Country(models.Model):
    title = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Posts text',
        help_text="Write what's on your mind?"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Posts date and time'
    )
    author = models.ForeignKey(User,
                               null=False,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Author')
    country = models.ForeignKey(Country,
                                null=True,
                                blank=False,
                                on_delete=models.SET_NULL,
                                related_name='posts',
                                verbose_name='Country about which post',
                                help_text='Choose a country')
    image = models.ImageField(upload_to='posts/',
                              null=True,
                              blank=True,
                              verbose_name='Image',
                              help_text='Choose image for your post')

    def comments_count(self):
        return self.comments.count()

    def likes(self):
        return self.post_likes.all()

    def already_like(self):
        current_user = get_current_user()
        return self.post_likes.filter(user=current_user).exists()

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.pk} | {self.author} | {self.text[:15]}'


class Comments(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='comments')
    text = models.TextField(verbose_name='Write a comment...',
                            null=False,
                            blank=False)
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Comment date and time')

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE,
                             blank=False,
                             null=False)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE,
                               blank=False,
                               null=False)

    def __str__(self):
        return f'Follower: {self.user}, Following: {self.author}'

    class Meta:
        unique_together = [['user', 'author']]


class Like(models.Model):
    user = models.ForeignKey(User,
                             related_name='likers',
                             on_delete=models.CASCADE,
                             blank=False,
                             null=False)
    post = models.ForeignKey(Post,
                             related_name='post_likes',
                             blank=False,
                             null=False,
                             on_delete=models.CASCADE)

    class Meta:
        unique_together = [['user', 'post']]
