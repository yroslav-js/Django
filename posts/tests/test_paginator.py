from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Country


User = get_user_model()


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_per_page = 12
        cls.amount_of_posts = 13
        cls.user = User.objects.create_user(username='TestClsUser')
        cls.country = Country.objects.create(
            title='New Zealand',
            slug='New-Zealand',
            description='NZ description',
        )
        for i in range(cls.amount_of_posts):
            cls.post = Post.objects.create(
                text=f'Post N{i}',
                pub_date='2022-06-18 15:35:33.561887',
                author=cls.user,
                country=cls.country,
            )
        cls.page_with_paginator = {
            'travel_posts:main': {},
            'travel_posts:country_posts': {'slug': TestPaginator.country.slug},
            'travel_posts:profile': {'user_name': TestPaginator.user.username},
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(TestPaginator.user)

    def test_first_page_contain_correct_records_amount(self):
        for page, kwargs in TestPaginator.page_with_paginator.items():
            with self.subTest(page=page):
                res = self.auth_client.get(
                    reverse(
                        page,
                        kwargs=kwargs,
                    )
                )
                post_amount = len(res.context.get('page_posts'))
                self.assertEquals(post_amount, TestPaginator.posts_per_page)

    def test_second_page_contain_correct_record_amount(self):
        for page, kwargs in TestPaginator.page_with_paginator.items():
            with self.subTest(page=page):
                res = self.auth_client.get(
                    reverse(
                        page,
                        kwargs=kwargs,
                    )+'?page=2'
                )
                post_amount = len(res.context.get('page_posts'))
                self.assertEquals(
                    post_amount,
                    TestPaginator.amount_of_posts-TestPaginator.posts_per_page
                )
