from django import forms

class Upload(forms.Form):
    csv_file = forms.FileField()

    def check_csv(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.lower().endswith('.csv'):
                raise forms.ValidationError("Only CSV files allowed.")
            
        return csv_file