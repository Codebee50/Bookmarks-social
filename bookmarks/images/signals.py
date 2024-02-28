from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Image

#when the .through function is called on a many to many field, we are accessing the intermediary table created by django
@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.users_like.count()
    instance.save()
    