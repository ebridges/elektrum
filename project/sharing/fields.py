from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.forms import fields


class NonValidatedTypedMultipleChoiceField(fields.TypedMultipleChoiceField):
    '''
    Example:
    items_to_share = NonValidatedTypedMultipleChoiceField(
      widget=widgets.MultipleHiddenInput(),
      coerce=uuid.UUID,
    )
    '''

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')


class MultiEmailField(fields.EmailField):
    default_validators = []

    def to_python(self, value):
        val = super().to_python(value)
        cleaned = []

        if val in self.empty_values:
            return None

        if ',' not in val:
            cleaned.append(val)
        else:
            emails = [x.strip() for x in val.split(',')]
            cleaned.extend(emails)
        return cleaned

    def validate(self, values):
        if values == self.empty_value or values in self.empty_values:
            raise ValidationError(self.error_messages['required'], code='required')

        validator = EmailValidator()
        errors = []
        for email in values:
            try:
                validator(email)
            except ValidationError as error:
                errors.append(email)
        if len(errors) > 0:
            if len(errors) == 1:
                mesg = self.error_messages['invalid_email']
                code = 'invalid_email'
                params = {'value': errors[0]}
            else:
                mesg = self.error_messages['invalid_emails']
                code = 'invalid_emails'
                params = {'value': ','.join(errors)}

            raise ValidationError(mesg, code=code, params=params)
