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
    """Form for users to update their profile"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'city', 'experience_years']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }


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
