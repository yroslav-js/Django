from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, Country


User = get_user_model()


class PostURLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserCls')
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
        cls.post_urls_templates_for_all = {
            reverse('travel_posts:main'): 'posts/index.html',
            reverse(
                'travel_posts:country_posts',
                kwargs={'slug': PostURLsTests.country.slug},
            ): 'posts/country_posts.html',
            reverse(
                'travel_posts:profile',
                kwargs={'user_name': PostURLsTests.user},
            ): 'posts/profile.html',
            reverse(
                'travel_posts:post_detail',
                kwargs={'post_id': PostURLsTests.post.pk},
            ): 'posts/post_detail.html',
        }

    def setUp(self):
        self.web_client_guest = Client()

        self.user = User.objects.create_user(username='UserAuth')
        self.web_client_auth = Client()
        self.web_client_auth.force_login(self.user)

        self.web_client_author = Client()
        self.web_client_author.force_login(PostURLsTests.user)

    def test_page_status_ok(self):
        """Test pages statuses for all users, including unauthorized"""
        for post_url in PostURLsTests.post_urls_templates_for_all:
            with self.subTest(post_url=post_url):
                response = self.web_client_guest.get(post_url)
                self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_page_templates(self):
        """Test templates pages for all users, including unauthorized"""
        for (
            post_url,
            template,
        ) in PostURLsTests.post_urls_templates_for_all.items():
            with self.subTest(post_url=post_url):
                response = self.web_client_guest.get(post_url)
                self.assertTemplateUsed(response, template)

    def test_post_create_redirect_to_login_unauthorized(self):
        """create post redirect to login page unauthorized user"""
        create_url = reverse('travel_posts:post_create')
        expected_url = f'{reverse("users:login")}?next={create_url}'
        response = self.web_client_guest.get(
            create_url,
            follow=True
        )
        self.assertRedirects(response, expected_url)

    def test_post_create_return_302_for_unauthorized(self):
        """create post return code 302 for unauthorized user"""
        response = self.web_client_guest.get(
            reverse('travel_posts:post_create')
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    def test_post_create_return_200_for_authorized(self):
        """create post return code 200 for authorized user"""
        response = self.web_client_auth.get(
            reverse('travel_posts:post_create')
        )
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_post_create_correct_template_for_authorized(self):
        """create post return correct template for authorized user"""
        response = self.web_client_auth.get(
            reverse('travel_posts:post_create')
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_edit_post_return_404_if_post_doesnt_exist(self):
        """if editing post doesn't exist, a 404 will be returned"""
        response = self.web_client_auth.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': '999'}
            )
        )
        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_post_return_302_for_unauthorized(self):
        """if user unauthorized edit post return 302 to login"""
        response = self.web_client_guest.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': PostURLsTests.post.pk}
            )
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_redirect_to_login_unauthorized(self):
        """if user unauthorized edit post redirect to login page"""
        edit_url = reverse(
            'travel_posts:post_edit',
            kwargs={'post_id': PostURLsTests.post.pk}
        )
        expected_url = f'{reverse("users:login")}?next={edit_url}'
        response = self.web_client_guest.get(
            edit_url,
            follow=True
        )
        self.assertRedirects(response, expected_url)

    def test_edit_post_return_302_if_not_author(self):
        """if not author try to edit post return 302 to main page"""
        response = self.web_client_auth.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': PostURLsTests.post.pk}
            )
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_redirect_to_main_if_not_author(self):
        """if not author try to edit post redirect to main page"""
        response = self.web_client_auth.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': PostURLsTests.post.pk}
            ),
            follow=True
        )
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_edit_post_return_200_for_authorized_author(self):
        """if author try to edit post return code 200"""
        response = self.web_client_author.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': PostURLsTests.post.pk}
            )
        )
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_edit_post_correct_template_for_author(self):
        """if author try to edit post check correct template for it"""
        response = self.web_client_author.get(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': PostURLsTests.post.pk}
            ),
            follow=True
        )
        self.assertTemplateUsed(response, 'posts/update_post.html')

    def test_unexisting_page_return_404(self):
        """if user use unexisting url the app will be returned 404"""
        response = self.web_client_guest.get('/unexisting_page_999/')
        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)
