from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Country


User = get_user_model()


class TestPostModel(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.country = Country.objects.create(
            title='New Zealand',
            slug='New-Zealand',
            description='NZ description',
        )
        cls.post = Post.objects.create(
            text='Text about NZ',
            pub_date='2022-06-18 15:35:33.561887',
            author=cls.user,
            country=cls.country,
        )

    def test_models_have_correct_str(self):
        """check __str__ is filled correctly"""
        post = TestPostModel.post
        post_str_expected = f'{post.pk} | {post.author} | {post.text[:15]}'
        self.assertEquals(post_str_expected, str(post))

        country = TestPostModel.country
        country_str_expected = country.title
        self.assertEquals(country_str_expected, str(country))

    def test_verbose_names(self):
        """check verbose name for post model"""
        post = TestPostModel.post
        verbose_names = {
            'text': "Posts text",
            'pub_date': 'Posts date and time',
            'author': 'Author',
            'country': 'Country about which post',
        }

        for field, expected_value in verbose_names.items():
            with self.subTest(field=field):
                self.assertEquals(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_texts(self):
        """check help texts for post model"""
        post = TestPostModel.post
        help_texts = {
            'text': "Write what's on your mind?",
            'pub_date': '',
            'author': '',
            'country': 'Choose a country',
        }

        for field, expected_value in help_texts.items():
            with self.subTest(field=field):
                self.assertEquals(
                    post._meta.get_field(field).help_text, expected_value
                )
