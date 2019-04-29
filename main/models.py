from django.db import models
from django.urls import reverse
from django.db.models.aggregates import Count
from random import randint
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete


def upload_location(instance, filename):
    return "%s/%s" %(instance.id, filename)


class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(editable=False,blank=True)
    imageForSpecialties = models.ImageField(upload_to=upload_location, help_text="Image size should be 500X650")
    imageForSlider = models.ImageField(upload_to=upload_location, help_text="Image for slider/coursel")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return '%s' % self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("main:category", kwargs={"slug": self.slug})


class PortfolioImages(models.Model):
    title = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="portfolio")
    large_image = models.ImageField(upload_to=upload_location, help_text="kindly upload the images having same size")
    thumbnail_image = models.ImageField(upload_to=upload_location, help_text="upload small size images")
    class Meta:
        verbose_name = 'Portfolio_Images'
        verbose_name_plural = 'Portfolio_Images'

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


class AboutMe(models.Model):

    image = models.ImageField(upload_to=upload_location, help_text="upload ypur image", default='wao')

    name = models.CharField(max_length=200)
    detail = models.TextField( help_text="introduce yourself")

    skill1Name = models.CharField(max_length=200,null=False, help_text="Photoshop")
    skill1Percentage = models.IntegerField()

    skill2Name = models.CharField(max_length=200,null=False, help_text="Final Cut")
    skill2Percentage = models.IntegerField()

    skill3Name = models.CharField(max_length=200,null=False, help_text="Studio Photography")
    skill3Percentage = models.IntegerField()

    skill4Name = models.CharField(max_length=200,null=False, help_text="Motion Video")
    skill4Percentage = models.IntegerField()

    ShotsTaken = models.IntegerField()
    CupsOfCoffe = models.IntegerField()
    VideosEdited = models.IntegerField()
    AwardsWon = models.IntegerField()

    FacebookLink = models.CharField(max_length=200,null=True, help_text="Link of facebook profile")
    VimeoLink = models.CharField(max_length=200,null=True, help_text="Link of vimeo profile")
    InstagramLink = models.CharField(max_length=200,null=True, help_text="Link of instagram profile")
    PinterestLink = models.CharField(max_length=200,null=True, help_text="Link of pinterest profile")
    FlickLink = models.CharField(max_length=200,null=True, help_text="Link of pinterest profile")

    Address = models.TextField(max_length=200,null=True, help_text="Address")
    Mobile_number = models.CharField(max_length=200, null=True, help_text="Enter your phone/mobile number")
    email = models.CharField(max_length=200, null=True, help_text="Address")

    class Meta:
        verbose_name = 'AboutMe'
        verbose_name_plural = 'AboutMe'

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.name


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Category.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_Category_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

@receiver(post_delete, sender=PortfolioImages)
def photo_post_delete_handler(sender, **kwargs):
    listingImage = kwargs['instance']
    storage, path = listingImage.image.storage, listingImage.image.path
    storage.delete(path)


pre_save.connect(pre_save_Category_receiver, sender=Category)
