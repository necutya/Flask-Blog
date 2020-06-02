import secrets
import os
from PIL import Image
from flask import url_for, current_app
from flaskblog import mail
from flask_mail import Message



def save_file(picture_form_data):
    random_name = secrets.token_hex(8)
    _, img_extension = os.path.splitext(picture_form_data.filename)
    picture_path = ''.join(os.path.join(current_app.root_path, 'static/profile_pictures', random_name + img_extension))

    output_size = (125, 125)
    # i = Image.open(picture_form_data)
    # i.thumbnail(output_size)
    picture_form_data.save(picture_path)

    return random_name + img_extension

def send_request_mail(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('users.reset_password', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)