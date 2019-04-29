from django import forms


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        fields = [
            "from_email",
            "name",
            "phone"
            "subject",
            "message",
        ]
