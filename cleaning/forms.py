"""
Forms for user interactions
"""
from django import forms
from django.contrib.auth.models import User
from .models import Review, Booking, ServiceCategory, UserProfile


class ReviewForm(forms.ModelForm):
    """Form for customers to submit reviews"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this service...'
            })
        }
        labels = {
            'rating': 'Service Rating',
            'comment': 'Your Review'
        }


class BookingForm(forms.ModelForm):
    """Form for customers to create bookings"""
    class Meta:
        model = Booking
        fields = ['date_time', 'location', 'notes']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service location (address)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions or notes for the service provider'
            })
        }
        labels = {
            'date_time': 'Preferred Date & Time',
            'location': 'Service Location',
            'notes': 'Additional Notes'
        }


class JobUpdateForm(forms.ModelForm):
    """Form for providers to update job status"""
    class Meta:
        model = Booking
        fields = ['status', 'completion_notes', 'photo']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'completion_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about work completed'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'status': 'Job Status',
            'completion_notes': 'Work Notes',
            'photo': 'Work Proof (Photo)'
        }


class BookingCancelForm(forms.Form):
    """Form for cancelling bookings"""
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for cancellation (optional)'
        }),
        label='Cancellation Reason'
    )


class ServiceCategoryForm(forms.ModelForm):
    """Form for admin to manage service categories"""
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'base_price', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ProviderVerificationForm(forms.ModelForm):
    """Form for admin to approve/reject provider verification"""
    verification_decision = forms.ChoiceField(
        choices=[('verified', 'Approve'), ('rejected', 'Reject')],
        widget=forms.RadioSelect(),
        label='Verification Decision'
    )
    
    class Meta:
        model = UserProfile
        fields = []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        decision = self.cleaned_data.get('verification_decision')
        instance.verification_status = decision
        instance.is_verified_by_admin = True
        if commit:
            instance.save()
        return instance


class UserProfileUpdateForm(forms.ModelForm):
    """Form for users to update their profile with name fields (restricted to 4 editable fields)"""
    first_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        }),
        label='First Name'
    )
    last_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        }),
        label='Last Name'
    )
    phone = forms.CharField(
        disabled=True,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone (read-only)'
        }),
        label='Phone Number (Cannot be changed)',
        help_text='Contact support to update phone number'
    )
    
    class Meta:
        model = UserProfile
        fields = ['city', 'experience_years']
        widgets = {
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
        labels = {
            'city': 'City',
            'experience_years': 'Years of Experience'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate first_name and last_name from User instance
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        
        # Pre-populate phone from UserProfile
        if self.instance and self.instance.phone:
            self.fields['phone'].initial = self.instance.phone
        
        # Hide experience_years for customers
        if self.instance and self.instance.user_type == 'customer':
            self.fields['experience_years'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save User model fields - only update if not empty
        if instance.user:
            if self.cleaned_data.get('first_name'):
                instance.user.first_name = self.cleaned_data.get('first_name', '')
            if self.cleaned_data.get('last_name'):
                instance.user.last_name = self.cleaned_data.get('last_name', '')
            if commit:
                instance.user.save()
        if commit:
            instance.save()
        return instance


class ServiceFilterForm(forms.Form):
    """Form for filtering services"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services...'
        }),
        label='Search'
    )
    
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Category'
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'step': '100',
            'min': '0',
            'placeholder': 'Min Price'
        }),
        label='Minimum Price'
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'step': '100',
            'placeholder': 'Max Price'
        }),
        label='Maximum Price'
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Default'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating_desc', 'Highest Rated'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Sort By'
    )
