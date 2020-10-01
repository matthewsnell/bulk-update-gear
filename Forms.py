from wtforms import Form, StringField, SelectField, validators, BooleanField, SubmitField
from wtforms.fields.html5 import DateField
import datetime


class updateSettings(Form):
    gearselect = SelectField('Select the gear you want to add')
    only_virtual = BooleanField(label='Only update virtual activities.')
    before_date = DateField(label='Apply to all activities before')
    after_date = DateField(label='Apply to all activites after')
    confirmation = BooleanField(label='I know what I am doing and take full responsibility!',
                                validators=[validators.required()])
    submit = SubmitField('Add Gear', id="gear_submit_button")

    def validate_on_submit(self):
        if self.after_date.data is not None:
            if self.after_date.data > datetime.date.today():
                self.errormessage = "Date cannot be in the future"
                return False
        if self.before_date.data is not None:
            if self.before_date.data > datetime.date.today():
                self.errormessage = "Date cannot be in the future"
                return False
        if self.before_date.data is not None and self.after_date.data is not None:
            if self.after_date.data > self.before_date.data:
                self.errormessage = "Invalid Date range"
                return False

        return True
