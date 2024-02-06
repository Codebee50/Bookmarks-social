from django import forms
from .models import Image
from django.core.files.base import ContentFile
from django.utils.text import slugify
import requests

class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput
        }
    
    def save(self, force_update=False, force_insert=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f"{name}.{extension}"
        #download image from the given url
        response = requests.get(image_url)

        #save the downloaded image to the images model image field
        image.image.save(image_name, ContentFile(response.content), save=False)
    
        if commit:
            image.save()

    """
    he rsplit method splits the string from the right
    (end) based on the specified delimiter ('.' in this case). 
    The second argument (1) indicates that the splitting 
    should be done at most once,
    considering only the last occurrence of the delimiter.
    """
    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png']
        extension = url.rsplit('.', 1)[1].lower()

        if extension not in valid_extensions:
            raise forms.ValidationError('The given url does not match valid image extensions.')
        
        return url