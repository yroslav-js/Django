from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from http import HTTPStatus

from posts.models import Post, Country, Comments, Follow


User = get_user_model()


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestClsUser')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.country = Country.objects.create(
            title='New Zealand',
            slug='New-Zealand',
            description='NZ description',
        )
        cls.post = Post.objects.create(
            text='Some post about NZ',
            pub_date='2022-06-18 15:35:33.561887',
            author=cls.user,
            country=cls.country,
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'country': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        cls.form_comments = {
            'post': cls.post,
            'author': cls.user,
            'created': '2022-06-18 15:39:33.561887',
            'text': 'Comment test text',
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(TestViews.user)

        self.guest_client = Client()

        self.follower_client = Client()
        self.user = User.objects.create_user(username='TestFollower')
        self.follower_client.force_login(self.user)

    def test_context_main_page(self):
        res = self.auth_client.get(reverse('travel_posts:main'))
        res_context = res.context.get('page_posts')[0]
        self.assertEquals(TestViews.post, res_context)

    def test_context_country_list(self):
        res = self.auth_client.get(
            reverse(
                'travel_posts:country_posts',
                kwargs={'slug': TestViews.country.slug}
            ),
        )
        res_context_country = res.context.get('country')
        res_context_post = res.context.get('page_posts')[0]
        self.assertEquals(TestViews.post.country, res_context_country)
        self.assertEquals(TestViews.post, res_context_post)

    def test_context_profile(self):
        res = self.auth_client.get(
            reverse(
                'travel_posts:profile',
                kwargs={'user_name': TestViews.user.username}
            )
        )
        res_context = res.context.get('page_posts')[0]
        self.assertEquals(TestViews.post, res_context)

    def test_context_post_detail(self):
        res = self.auth_client.get(
            reverse(
                'travel_posts:post_detail',
                kwargs={'post_id': TestViews.post.pk}
            )
        )
        res_context = res.context.get('post')
        self.assertEquals(TestViews.post, res_context)

    def test_context_edit_post(self):
        res = self.auth_client.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={
                    'post_id': TestViews.post.pk,
                }
            )
        )
        form_fields = TestViews.form_fields
        for field, expected_field in form_fields.items():
            with self.subTest(field=field):
                form_field = res.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_field)

    def test_context_create_post(self):
        res = self.auth_client.get(
            reverse('travel_posts:post_create')
        )
        form_fields = TestViews.form_fields
        for field, expected_field in form_fields.items():
            with self.subTest(field=field):
                form_field = res.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected_field)

    def test_check_country_page_with_correct_country_posts(self):
        wrong_country = Country.objects.create(
            title='UnnamedCountry',
            slug='UnnamedCountrySlug',
            description="We mustn't see this country on a page"
        )
        res = self.auth_client.get(
            reverse(
                'travel_posts:country_posts',
                kwargs={'slug': wrong_country.slug}
            )
        )
        posts_amount = res.context.get('page_posts').paginator.count
        self.assertEquals(posts_amount, 0)

    def test_auth_user_can_add_comment(self):
        comment_count = Comments.objects.count()

        res = self.auth_client.post(
            reverse(
                'travel_posts:add_comment',
                kwargs={'post_id': TestViews.post.pk}
            ),
            data=TestViews.form_comments,
            follow=True,
        )

        res_comment_text = res.context.get('comments')[0]

        self.assertEquals(Comments.objects.count(), comment_count + 1)
        self.assertEquals(TestViews.form_comments['text'],
                          res_comment_text.text)
        self.assertIn('post', res.context)
        self.assertIn('comments', res.context)
        self.assertIn('form', res.context)

    def test_guest_cant_add_comment(self):
        comment_count_before = Comments.objects.count()

        add_url = reverse(
            'travel_posts:add_comment',
            kwargs={'post_id': TestViews.post.pk}
        )
        expected_url = f'{reverse("users:login")}?next={add_url}'

        res = self.guest_client.post(
            add_url,
            data=TestViews.form_comments,
            follow=True,
        )
        comment_count_after = Comments.objects.count()

        self.assertEquals(comment_count_before, comment_count_after)
        self.assertRedirects(res, expected_url)

    def test_auth_user_can_follow(self):
        follow_count = Follow.objects.count()

        res = self.auth_client.get(
            reverse(
                'travel_posts:profile_follow',
                kwargs={'user_name': TestViews.author}
            ),
            follow=True
        )

        follow = Follow.objects.last()

        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertIn('following', res.context)
        self.assertEquals(follow.author, TestViews.author)
        self.assertEquals(follow.user, TestViews.user)

    def test_guest_user_cant_follow(self):
        follow_count = Follow.objects.count()

        follow_url = reverse(
                'travel_posts:profile_follow',
                kwargs={'user_name': TestViews.author}
            )
        expected_url = f'{reverse("users:login")}?next={follow_url}'

        res = self.guest_client.get(follow_url)

        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertRedirects(res, expected_url)
        self.assertEquals(res.status_code, HTTPStatus.FOUND)

    def test_auth_user_can_unfollow(self):
        Follow.objects.create(user=TestViews.user, author=TestViews.author)

        follow_count = Follow.objects.count()

        self.auth_client.get(
            reverse(
                'travel_posts:profile_unfollow',
                kwargs={'user_name': TestViews.author}
            ),
            follow=True
        )

        self.assertEquals(Follow.objects.count(), follow_count - 1)

    def test_author_post_showing_for_followers(self):
        Follow.objects.create(user=self.user, author=TestViews.user)

        res = self.follower_client.get(reverse('travel_posts:follow_index'))

        res_contexts = res.context.get('page_posts')[0]
        self.assertEquals(TestViews.post, res_contexts)

    def test_author_post_not_showing_if_unfollow(self):
        Follow.objects.create(user=TestViews.user, author=self.user)

        res = self.follower_client.get(reverse('travel_posts:follow_index'))

        count_of_posts = res.context.get("page_posts").paginator.count
        self.assertEqual(count_of_posts, 0)
