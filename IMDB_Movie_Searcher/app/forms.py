from flask_wtf import Form
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

#Created Search Form
class SearchForm(Form):
    search = StringField('search', [DataRequired()])
    submit = SubmitField('Search',render_kw={'class': 'btn btn-success btn-block'})
