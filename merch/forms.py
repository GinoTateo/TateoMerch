from django import forms
from .models import Store, Merch, WeeklyData, User

class StoreForm(forms.ModelForm):
   class Meta:
     model = Store
     fields = '__all__'

class MerchForm(forms.ModelForm):
   class Meta:
     model = Merch
     fields = '__all__'

class WeeklyDataForm(forms.ModelForm):
    class Meta:
        model = WeeklyData
        fields = '__all__'

class StoreForm2(forms.Form):
    store = forms.CharField(max_length=100)
    number = forms.IntegerField()

class MerchForm2(forms.ModelForm):
   class Meta:
       user = forms.ModelChoiceField(queryset=User.objects.all())
       store = forms.ModelChoiceField(queryset=Store.objects)
       OOS = forms.IntegerField()
       case_count = forms.IntegerField()
       upload = forms.ImageField()