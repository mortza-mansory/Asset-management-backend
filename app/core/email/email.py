import emails
from emails.template import JinjaTemplate

def send_reset_code(email: str, reset_code: str):
    message = emails.Message(
        subject="Password Reset Code",
        html=JinjaTemplate(
            """
            <p>Dear User,</p>
            <p>Your password reset code is: <strong>{{ reset_code }}</strong></p>
            <p>This code will expire in 3 minutes.</p>
            """
        ),
        mail_from=("Asset RFID Manager", "yourname@outlook.com")
    )
    
    message.render(reset_code=reset_code)

    smtp_options = {
        "host": "smtp.office365.com",
        "port": 587,
        "user": "assets_management_rfid@outlook.com",
        "password": "Handller12",  
        "tls": True
    }

    response = message.send(to=email, smtp=smtp_options)
    return response.status_code == 250
