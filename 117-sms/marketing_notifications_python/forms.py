from flask_wtf import Form
#from flask import Flask, render_template, flash, request
#from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from werkzeug.datastructures import MultiDict
from wtforms import TextField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired


class SendMessageForm(Form):
    zipCode = SelectMultipleField('zipCode', choices=[('All', 'All'),('92606', '92606'), ('92612', '92612'), ('92614', '92614'), ('92617', '92617'), ('92618', '92618'),
             ('92627', '92627'), ('92704', '92704'), ('92805', '92805'), ('92780', '92780'), ('92782', '92782'), ('92801', '92801'),
             ('92805', '92805'), ('92807', '92807'), ('92808', '92808'), ('92877', '92877')])
    interest = SelectMultipleField('interest', choices=[('All', 'All'),  ('Science/Tech', 'Science/Tech') , ('Arts', 'Arts'), ('Sports', 'Sports')])
    childAge = TextField('childAge',validators=[])
    language = TextField('language',validators=[])
    message = TextField('message', validators=[DataRequired(message="Message is required")])
    

    def reset(self):
        blankData = MultiDict([('message', ''), ('childAge',  ''), ('zipCode',  ''), ('interest',  '')])
        self.process(blankData)




