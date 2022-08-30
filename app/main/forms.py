"""
Contains forms related to creating blog posts.
"""

from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, FieldList, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    """
    A form for the post editor, used on the new_post and edit pages.

    Extends the FlaskForm class from flask_wtf. Contains fields for the post title,
    post, body, and tags as well as a submit field. The body field is a CKEditor post
    editor. The tags field is a string field that is parsed elsewhere as a comma-separated
    list of tags. The title and body fields cannot be empty.

    Attributes
    -----------
    title : StringField(label='Title', validators=[DataRequired())
        A field for the post title.
    body : CKEditorField(label='Body', validators=[DataRequired())
        A field for editing the body of the text.
    tags : StringField(label='Tags')
        A field for the post's tags.
    submit : SubmitField(label='Submit')
        A field for submitting the post.
    """

    title = StringField('Title', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])
    tags = StringField('Tags')
    submit = SubmitField('Submit')


