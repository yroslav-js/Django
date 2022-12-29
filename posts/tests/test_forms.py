import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

from posts.models import Post, Country


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostsForms(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        small_gif_edited = (
            b'\x47\x49\x46\x38\x37\x61\x01\x00'
            b'\x01\x00\x80\x01\x00\x00\x00\x00'
            b'\xff\xff\xff\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x4c'
            b'\x01\x00\x3b'
        )
        cls.uploaded_image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        cls.uploaded_image_edited = SimpleUploadedFile(
            name='small_edited.gif',
            content=small_gif_edited,
            content_type='image/gif',
        )
        cls.user = User.objects.create_user(username='UserCls')
        cls.country = Country.objects.create(
            title='Country Name',
            slug='country-name',
            description='Country description',
        )
        cls.country_changed = Country.objects.create(
            title='Another country Name',
            slug='another-country-name',
            description='Another country description',
        )
        cls.form_create_data = {
            'text': 'Some post text',
            'country': TestPostsForms.country.pk,
            'author': TestPostsForms.user,
            'image': cls.uploaded_image,
        }
        cls.form_edit_data = {
            'text': 'Edited post text',
            'country': TestPostsForms.country_changed.pk,
            'author': TestPostsForms.user,
            'image': cls.uploaded_image_edited,
        }
        cls.post_urls_for_guest_clients = (
            reverse('travel_posts:main'),
            reverse(
                'travel_posts:country_posts',
                kwargs={'slug': cls.country.slug},
            ),
            reverse(
                'travel_posts:profile',
                kwargs={'user_name': cls.user},
            ),
            reverse(
                'travel_posts:post_detail',
                kwargs={'post_id': 1},
            ),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.auth_client = Client()
        self.auth_client.force_login(TestPostsForms.user)

        self.not_author = User.objects.create_user(username='TestNotAuthor')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_auth_user_create_post(self):
        posts_count = Post.objects.count()
        form_data = TestPostsForms.form_create_data

        res = self.auth_client.post(
            reverse('travel_posts:post_create'),
            data=form_data,
            follow=True,
        )

        created_post = Post.objects.last()

        self.assertRedirects(
            res,
            reverse(
                'travel_posts:profile',
                kwargs={'user_name': TestPostsForms.user}
            )
        )
        self.assertEquals(Post.objects.count(), posts_count + 1)
        self.assertEquals(created_post.text, form_data['text'])
        self.assertEquals(created_post.country, TestPostsForms.country)
        self.assertEquals(created_post.author, TestPostsForms.user)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/small.gif',
            ).exists()
        )

    def test_guest_user_cant_create_post(self):
        post_count_before = Post.objects.count()

        create_url = reverse('travel_posts:post_create')
        expected_url = f'{reverse("users:login")}?next={create_url}'

        res = self.guest_client.post(
            create_url,
            data=TestPostsForms.form_create_data,
            follow=True,
        )
        post_count_after = Post.objects.count()

        self.assertEquals(post_count_before, post_count_after)
        self.assertRedirects(res, expected_url)

    def test_author_can_edit_post(self):
        post = Post.objects.create(
            text='Not edited post',
            pub_date='2022-06-18 15:35:33.561887',
            author=TestPostsForms.user,
            country=TestPostsForms.country,
            image=TestPostsForms.uploaded_image,
        )

        form_edited_data = TestPostsForms.form_edit_data
        self.auth_client.post(
            reverse(
                'travel_posts:post_edit',
                kwargs={'post_id': post.pk}
            ),
            data=form_edited_data,
            follow=True,
        )

        edited_post = Post.objects.filter(pk=post.pk)[0]

        self.assertEquals(edited_post.text, form_edited_data['text'])
        self.assertEquals(edited_post.country.pk, form_edited_data['country'])
        self.assertTrue(
            Post.objects.filter(
                text=form_edited_data['text'],
                image='posts/small_edited.gif',
            ).exists()
        )

    def test_guest_or_not_author_cant_edit_post(self):
        post = Post.objects.create(
            text='Not edited post',
            pub_date='2022-06-18 15:35:33.561887',
            author=TestPostsForms.user,
            country=TestPostsForms.country,
        )

        edit_url = reverse(
            'travel_posts:post_edit',
            kwargs={'post_id': post.pk},
        )
        expected_login_url = f'{reverse("users:login")}?next={edit_url}'

        form_edited_data = TestPostsForms.form_edit_data
        res = self.guest_client.post(
            edit_url,
            data=form_edited_data,
            follow=True,
        )

        edited_post = Post.objects.filter(pk=post.pk)[0]

        self.assertEquals(edited_post.text, post.text)
        self.assertEquals(edited_post.country.pk, post.country.pk)
        self.assertRedirects(res, expected_login_url)

        res = self.not_author_client.post(
            edit_url,
            data=form_edited_data,
            follow=True,
        )

        edited_post = Post.objects.filter(pk=post.pk)[0]

        self.assertEquals(edited_post.text, post.text)
        self.assertEquals(edited_post.country.pk, post.country.pk)
        self.assertRedirects(res, reverse("travel_posts:main"))

    def test_image_exists_on_pages_after_creation(self):
        Post.objects.create(
            text='check posts image',
            pub_date='2022-06-18 15:35:33.561887',
            author=TestPostsForms.user,
            country=TestPostsForms.country,
            image=TestPostsForms.uploaded_image,
        )

        for page in TestPostsForms.post_urls_for_guest_clients:
            with self.subTest(page=page):
                res = self.guest_client.get(page)

                if 'post' in res.context:
                    res_context_post = res.context.get('post')
                else:
                    res_context_post = res.context.get('page_posts')[0]

                self.assertTrue(
                    res_context_post.image
                )
                self.assertEquals(res.status_code, HTTPStatus.OK)
