from django import forms


class ScrapeForm(forms.Form):
    group_id = forms.CharField(label="", required=False,
                           widget= forms.TextInput
                           (attrs={
                               'class': 'form-control me-2',
                               'name': 'group_id',
                               'placeholder':'Group ID',
                               'required': 'True',
                               'minlength': 15,
                               'maxlength': 15,
                               'type': 'number'
                            }))
    