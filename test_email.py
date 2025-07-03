from app.core.email.email import send_reset_code

print("sending email")
send_reset_code("panelsazanpersion@gmail.com", "123456")
print("email sended")