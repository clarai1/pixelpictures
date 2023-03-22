from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import json
import os
from django.core.files.uploadedfile import SimpleUploadedFile

from pixelpictures.models import User, Picture, Tag
from pixelpictures.views import update_tags, PATH_PICTURES

class APITestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(username='creator', email='creator@example.com', password='pssSre!1')
        self.creator.save()
        self.notCreator = User.objects.create_user(username='notCreator', email='notcreator@example.com', password='somePass123')
        self.notCreator.save()
        self.picture = Picture.objects.create(
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
        self.picture.save()
        Tag.objects.create(picture=self.picture, tag='tag1')
        self.sample_image = [[[0,0,0], [0,0,0], [255,255,255]], [[255,255,255], [1,2,3], [0,0,0]]]
        self.sample_palette = [[0,0,0], [255,255,255]]
        self.sample_tags = ['tag1', 'tag2']
        self.test_img = open('pixelpictures/tests/manda.jpg', 'rb')

    # Tests update_tags

    def test_update_tags_add(self):
        tags = ['tag1', 'tag2', 'tag3']
        picture = Picture.objects.get(pk=1)
        update_tags(picture, tags)
        new_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=picture)]
        
        self.assertEqual(set(tags), set(new_tags))
        self.assertEqual(len(new_tags), 3)

    def test_update_tags_delete(self):
        tags = ['tag3']
        picture = Picture.objects.get(pk=1)
        update_tags(picture, tags)
        new_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=picture)]
        
        self.assertEqual(tags, new_tags)

    # Tests save_image

    def test_save_image_anonymous_create_new_one(self):
        body={
            'image': self.sample_image,
            'public': True,
            'tags': self.sample_tags,
            'palette': self.sample_palette
        }
        response = self.client.post(reverse('save'), json.dumps(body), content_type="application/json")

        self.assertFalse(Picture.objects.filter(image=self.sample_image))
        self.assertEqual(json.loads(response.content)['message'], 'You have to log in to save a picture.')

    def test_save_image_creator_create_new_one(self):
        self.client.login(username='creator', password='pssSre!1')
        body={
            'image': self.sample_image,
            'public': True,
            'tags': self.sample_tags,
            'palette': self.sample_palette
        }
        response = self.client.post(reverse('save'), json.dumps(body), content_type="application/json")
        new_picture = Picture.objects.get(image=self.sample_image)
        new_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=new_picture)]

        self.assertEqual(json.loads(response.content)['message'], 'Picture saved correctly.')
        self.assertEqual(json.loads(response.content)['key'], new_picture.pk)
        self.assertEqual(new_picture.user, self.creator)
        self.assertTrue(new_picture.public)
        self.assertEqual(new_picture.palette, self.sample_palette)
        self.assertEqual(new_tags, self.sample_tags)
        self.assertTrue(os.path.isfile(f"{PATH_PICTURES}/{new_picture.pk}_{new_picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png"))

        # Delete created file
        os.remove(f"{PATH_PICTURES}/{new_picture.pk}_{new_picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png")

    def test_save_image_anonymous_modify_existing_picture(self):
        body={
            'image': self.sample_image,
            'public': False,
            'tags': self.sample_tags,
            'palette': self.sample_palette,
            'key': 1
        }
        response = self.client.put(reverse('save'), json.dumps(body), content_type="application/json")
        modified_picture = Picture.objects.get(pk=1)
        new_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=modified_picture)]
        old_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=self.picture)]

        self.assertEqual(json.loads(response.content)['error'], 'Cannot modify a picture not created by you.')
        self.assertEqual(modified_picture.user, self.creator)
        self.assertTrue(modified_picture.public)
        self.assertEqual(modified_picture.palette, self.picture.palette)
        self.assertEqual(modified_picture.image, self.picture.image)
        self.assertEqual(new_tags, old_tags)

    def test_save_image_notCreator_modify_existing_picture(self):
        self.client.login(username='notCreator', password='somePass123')
        body={
            'image': self.sample_image,
            'public': False,
            'tags': self.sample_tags,
            'palette': self.sample_palette,
            'key': 1
        }
        response = self.client.put(reverse('save'), json.dumps(body), content_type="application/json")
        modified_picture = Picture.objects.get(pk=1)
        new_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=modified_picture)]
        old_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=self.picture)]

        self.assertEqual(json.loads(response.content)['error'], 'Cannot modify a picture not created by you.')
        self.assertEqual(modified_picture.user, self.creator)
        self.assertTrue(modified_picture.public)
        self.assertEqual(modified_picture.palette, self.picture.palette)
        self.assertEqual(modified_picture.image, self.picture.image)
        self.assertEqual(new_tags, old_tags)

    def test_save_image_creator_modify_existing_picture(self):
        self.client.login(username='creator', password='pssSre!1')
        body={
            'image': self.sample_image,
            'public': False,
            'tags': self.sample_tags,
            'palette': self.sample_palette,
            'key': 1
        }
        response = self.client.put(reverse('save'), json.dumps(body), content_type="application/json")
        modified_picture = Picture.objects.get(pk=1)
        new_tags = [tag_object.tag for tag_object in Tag.objects.filter(picture=modified_picture)]
       
        self.assertEqual(json.loads(response.content)['message'], 'Picture saved correctly.')
        self.assertEqual(json.loads(response.content)['key'], 1)
        self.assertEqual(modified_picture.user, self.creator)
        self.assertFalse(modified_picture.public)
        self.assertEqual(modified_picture.palette, self.sample_palette)
        self.assertEqual(modified_picture.image, self.sample_image)
        self.assertEqual(new_tags, self.sample_tags)

        # Delete create file
        os.remove(f"{PATH_PICTURES}/{modified_picture.pk}_{modified_picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png")

    def test_save_image_anonymous_modify_non_existing_picture(self):
        body={
            'image': self.sample_image,
            'public': False,
            'tags': self.sample_tags,
            'palette': self.sample_palette,
            'key': 3
        }
        response = self.client.put(reverse('save'), json.dumps(body), content_type="application/json")

        self.assertFalse(Picture.objects.filter(pk=3))
        self.assertEqual(json.loads(response.content)['error'], 'Picture with primary key 3 does not exists.')

    def test_save_image_user_modify_non_existing_picture(self):
        self.client.login(username='notCreator', password='somePass123')
        body={
            'image': self.sample_image,
            'public': False,
            'tags': self.sample_tags,
            'palette': self.sample_palette,
            'key': 3
        }
        response = self.client.put(reverse('save'), json.dumps(body), content_type="application/json")

        self.assertFalse(Picture.objects.filter(pk=3))
        self.assertEqual(json.loads(response.content)['error'], 'Picture with primary key 3 does not exists.')

    # Tests delete_picture

    def test_delete_existing_picture(self):
        self.client.login(username='creator', password='pssSre!1')
        body_new_picture={
            'image': self.sample_image,
            'public': True,
            'tags': self.sample_tags,
            'palette': self.sample_palette,
            'key': 2
        }
        response = self.client.post(reverse('save'), json.dumps(body_new_picture), content_type="application/json")
        new_picture = Picture.objects.get(pk=2)
        self.client.logout()

        body={'key': 2}

        # Anonymous User
        response_anonymous = self.client.post(reverse('delete_picture'), json.dumps(body), content_type="application/json")

        self.assertEqual(json.loads(response_anonymous.content)['message'], 'You cannot delete a picture that is not yours!')
        self.assertTrue(Picture.objects.filter(pk=2))
        self.assertTrue(os.path.isfile(f"{PATH_PICTURES}/{new_picture.pk}_{new_picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png"))

        # NotCreator User
        self.client.login(username='notCreator', password='somePass123')
        response_notCreator = self.client.post(reverse('delete_picture'), json.dumps(body), content_type="application/json")

        self.assertEqual(json.loads(response_notCreator.content)['message'], 'You cannot delete a picture that is not yours!')
        self.assertTrue(Picture.objects.filter(pk=2))
        self.assertTrue(os.path.isfile(f"{PATH_PICTURES}/{new_picture.pk}_{new_picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png"))

        # Creator User
        self.client.login(username='creator', password='pssSre!1')
        response_creator = self.client.post(reverse('delete_picture'), json.dumps(body), content_type="application/json")

        self.assertEqual(json.loads(response_creator.content)['message'], 'Picture deleted successfully.')
        self.assertFalse(Picture.objects.filter(pk=2))
        self.assertFalse(os.path.isfile(f"{PATH_PICTURES}/{new_picture.pk}_{new_picture.timestamp.strftime('%Y%m%d_%H%M%S')}.png"))

    def test_delete_anonymous_not_existing_picture(self):
        body={'key': 3}
        response = self.client.post(reverse('delete_picture'), json.dumps(body), content_type="application/json")

        self.assertEqual(json.loads(response.content)['message'], 'This picture does not exists.')

    def test_delete_user_not_existing_picture(self):
        self.client.login(username='creator', password='pssSre!1')
        body={'key': 3}
        response = self.client.post(reverse('delete_picture'), json.dumps(body), content_type="application/json")

        self.assertEqual(json.loads(response.content)['message'], 'This picture does not exists.')

    # Tests resize_image

    def test_resize_non_post_request(self):
        response = self.client.get(reverse('resize_image'))
        self.assertRedirects(response, reverse('create'))

    def test_resize_negative_values(self):
        response = self.client.post(reverse('resize_image'), data={'img': self.test_img, 'height': -10, 'width': 10})
        self.assertEqual(json.loads(response.content)['error'], 'Height and width cannot be negative.')

        response = self.client.post(reverse('resize_image'), data={'img': self.test_img, 'height': -10, 'width': -10})
        self.assertEqual(json.loads(response.content)['error'], 'Height and width cannot be negative.')

        response = self.client.post(reverse('resize_image'), data={'img': self.test_img, 'height': 10, 'width': -10})
        self.assertEqual(json.loads(response.content)['error'], 'Height and width cannot be negative.')

    def test_resize_error_with_file(self):
        img = open('pixelpictures/tests/manda.pdf', 'rb')
        response = self.client.post(reverse('resize_image'), data={'img': img, 'height': 30, 'width': 10})

        self.assertEqual(json.loads(response.content)['error'], 'Not supported file format.')

    def test_resize_correct_input(self):
        response = self.client.post(reverse('resize_image'), data={'img': self.test_img, 'height': 30, 'width': 10})

        self.assertEqual(len(json.loads(response.content)['sample_image']), 30)
        self.assertEqual(len(json.loads(response.content)['sample_image'][0]), 10)

    # Tests image_to_pixels

    def test_image_to_pixels_non_post_request(self):
        response = self.client.get(reverse('image_to_pixels'))
        self.assertEqual(json.loads(response.content)['error'], 'POST request required.')

    def test_image_to_pixels(self):
        body={
            'image': self.sample_image,
            'palette': self.sample_palette
        }
        response = self.client.post(reverse('image_to_pixels'), json.dumps(body), content_type="application/json")
        self.assertEqual(len(json.loads(response.content)['pixels_image']), 2)
        self.assertEqual(len(json.loads(response.content)['pixels_image'][0]), 3)