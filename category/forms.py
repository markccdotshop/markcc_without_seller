from django import forms
from .models import Category

# create base form
class CategoryForm(forms.Form):
    category_name = forms.CharField(
        label='Base Name',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Base Name'}),
        required=True
    )
    category_ratio = forms.ChoiceField(
        label='Base Ratio/validity (%)',
        choices=[('', 'Select'), ('50', '50%'), ('60', '60%'), ('70', '70%'), ('80', '80%'), ('90', '90%'), ('95', '95%'), ('100', '100%')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# upload cards form
class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}--Validity--{obj.quality_indicator}%"
    
class CardUploadForm(forms.Form):
    base = CustomModelChoiceField(
        queryset=Category.objects.all().order_by('-id'),
        label="Select Base",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select"
    )

    REFUND_CHOICES = [
        ('1', 'With Check Time'),
        ('2', 'Without Check Time'),
        ('7', 'No Refund'),
    ]
    

    refund = forms.ChoiceField(
        choices=REFUND_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Refund Policy"
    )

    price_choices = [(str(i), f"${i}") for i in range(5, 101, 5)]
    usprice = forms.ChoiceField(
        label="US Price", 
        choices=price_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price_choices = [(str(i), f"${i}") for i in range(10, 101, 5)]
    nonusprice = forms.ChoiceField(
        label="Non-US Price", 
        choices=price_choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    cards = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': '5178055800481243|03/2023|123|...'}),
        label="Cards"
    )


    
