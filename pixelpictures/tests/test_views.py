from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from pixelpictures.models import User, Picture, Tag

class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(username='creator', email='creator@example.com', password='pssSre!1')
        self.creator.save()
        self.notCreator = User.objects.create_user(username='notCreator', email='notcreator@example.com', password='somePass123')
        self.notCreator.save()
        self.public_picture = Picture.objects.create(
            image=[
                [[0,0,0], [0,0,0], [255,255,255]],
                [[255,255,255], [1,2,3], [0,0,0]],
                [[0,0,0], [123,123,123], [33,25,23]],
                [[255,255,255], [123,123,123], [0,0,0]]],
            palette=[[0,0,0], [255,255,255], [1,2,3], [123,123,123], [33,25,23]],
            user=self.creator,
            public=True,
            timestamp = timezone.now(),
            pk=1
        )
        self.public_picture.save()
        self.private_picture = Picture.objects.create(
            image=[
                [[0,0,0], [0,0,0], [255,255,255]],
                [[255,255,255], [1,2,3], [0,0,0]],
                [[0,0,0], [123,123,123], [33,25,23]],
                [[255,255,255], [123,123,123], [0,0,0]]],
            palette=[[0,0,0], [255,255,255], [1,2,3], [123,123,123], [33,25,23]],
            user=self.creator,
            timestamp = timezone.now(),
            pk=2
        )
        self.private_picture.save()
        self.public_picture_with_tag = Picture.objects.create(
            image=[
                [[0,0,0], [0,0,0], [255,255,255]],
                [[255,255,255], [1,2,3], [0,0,0]],
                [[0,0,0], [123,123,123], [33,25,23]],
                [[255,255,255], [123,123,123], [0,0,0]]],
            palette=[[0,0,0], [255,255,255], [1,2,3], [123,123,123], [33,25,23]],
            user=self.creator,
            public=True,
            timestamp = timezone.now(),
            pk=3
        )
        self.public_picture_with_tag.save()
        Tag.objects.create(picture=self.public_picture_with_tag, tag='someTag')

    # Tests index

    def test_index_plain(self):
        response = self.client.get(reverse('index'))

        self.assertTemplateUsed(response, 'pixelpictures/index.html')
        self.assertQuerysetEqual(response.context['pictures'].object_list, Picture.objects.filter(pk__in=[1,3]).order_by('-pk'))
        self.assertEqual(response.context['search_value'], '')
        self.assertEqual(response.context['sort_value'], 'new')

    def test_index_search(self):
        response = self.client.get(reverse('index') + '/?search=someTag')

        self.assertTemplateUsed(response, 'pixelpictures/index.html')
        self.assertQuerysetEqual(response.context['pictures'].object_list, Picture.objects.filter(pk=3))
        self.assertEqual(response.context['search_value'], 'someTag')
        self.assertEqual(response.context['sort_value'], 'new')

    def test_index_sort(self):
        self.client.get(reverse('view_picture', args=['1']))
        response = self.client.get(reverse('index') + '/?sort=views')

        self.assertTemplateUsed(response, 'pixelpictures/index.html')
        self.assertQuerysetEqual(response.context['pictures'].object_list, Picture.objects.filter(pk__in=[1,3]).order_by('pk'))
        self.assertEqual(response.context['search_value'], '')
        self.assertEqual(response.context['sort_value'], 'views')

    # Tests create

    def test_create(self):
        response = self.client.get(reverse('create'))
        self.assertTemplateUsed(response, 'pixelpictures/create.html')

    # Tests view_picture

    def test_view_picture_not_existing_picture(self):
        response_anonymous = self.client.get(reverse('view_picture', args=['100']))
        self.assertEqual(response_anonymous.context, None)

        self.client.login(username='creator', password='pssSre!1')
        response_user = self.client.get(reverse('view_picture', args=['100']))
        self.assertEqual(response_user.context, None)

    def test_view_picture_anonymousUser(self):
        # Public picture
        response = self.client.get(reverse('view_picture', args=['1']))
        public_picture = Picture.objects.get(pk=1)
        self.assertEqual(public_picture.views, 1)
        self.assertTemplateUsed(response, 'pixelpictures/view_picture.html')
        self.assertEqual(response.context['picture'], public_picture)

        # Private picture
        response = self.client.get(reverse('view_picture', args=['2']))
        private_picture = Picture.objects.get(pk=2)
        self.assertEqual(private_picture.views, 0)
        self.assertEqual(response.context, None)

    def test_view_picture_creator(self):
        self.client.login(username='creator', password='pssSre!1')

        # Public picture
        response = self.client.get(reverse('view_picture', args=['1']))
        public_picture = Picture.objects.get(pk=1)
        self.assertEqual(public_picture.views, 0)
        self.assertTemplateUsed(response, 'pixelpictures/view_picture.html')
        self.assertEqual(response.context['picture'], public_picture)

        # Private picture
        response = self.client.get(reverse('view_picture', args=['2']))
        private_picture = Picture.objects.get(pk=2)
        self.assertEqual(private_picture.views, 0)
        self.assertTemplateUsed(response, 'pixelpictures/view_picture.html')
        self.assertEqual(response.context['picture'], private_picture)

    def test_view_picture_notCreator(self):
        self.client.login(username='notCreator', password='somePass123')

        # Public picture
        response = self.client.get(reverse('view_picture', args=['1']))
        public_picture = Picture.objects.get(pk=1)
        self.assertEqual(public_picture.views, 1)
        self.assertTemplateUsed(response, 'pixelpictures/view_picture.html')
        self.assertEqual(response.context['picture'], public_picture)

        # Private picture
        response = self.client.get(reverse('view_picture', args=['2']))
        private_picture = Picture.objects.get(pk=2)
        self.assertEqual(private_picture.views, 0)
        self.assertEqual(response.context, None)

    # Tests modify

    def test_modify_not_existing_picture(self):
        response_anonymous = self.client.get(reverse('modify_picture', args=['100']))
        self.assertEqual(response_anonymous.context, None)

        self.client.login(username='creator', password='pssSre!1')
        response_user = self.client.get(reverse('modify_picture', args=['100']))
        self.assertEqual(response_user.context, None)

    def test_modify_anonymousUser(self):
        response = self.client.get(reverse('modify_picture', args=['1']))
        self.assertEqual(response.context, None)

    def test_modify_creator(self):
        self.client.login(username='creator', password='pssSre!1')
        
        response = self.client.get(reverse('modify_picture', args=['1']))
        public_picture = Picture.objects.get(pk=1)
        self.assertTemplateUsed(response, 'pixelpictures/create.html')
        self.assertEqual(response.context['picture'], public_picture)

    def test_modify_notCreator(self):
        self.client.login(username='notCreator', password='somePass123')

        response = self.client.get(reverse('modify_picture', args=['1']))
        self.assertEqual(response.context, None)

    # Tests user_pictures

    def test_user_pictures_anonymous(self):
        response = self.client.get(reverse('user_pictures'))
        self.assertEqual(response.context, None)

    def test_user_pictures_creator(self):
        self.client.login(username='creator', password='pssSre!1')
        response = response = self.client.get(reverse('user_pictures'))

        self.assertTemplateUsed(response, 'pixelpictures/user_pictures.html')
        self.assertQuerysetEqual(response.context['private'], Picture.objects.filter(pk=2))
        self.assertQuerysetEqual(response.context['public'], Picture.objects.filter(pk__in=[1,3]), ordered=False)

    def test_user_pictures_notCreator(self):
        self.client.login(username='notCreator', password='somePass123')
        response = response = self.client.get(reverse('user_pictures'))

        self.assertTemplateUsed(response, 'pixelpictures/user_pictures.html')
        self.assertFalse(response.context['private'])
        self.assertFalse(response.context['public'])