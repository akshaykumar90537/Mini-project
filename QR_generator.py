import qrcode

data = ("https://mail.google.com/mail/u/0/#inbox")

qr = qrcode.QRCode(
    version=1,
    error_correction= qrcode.constants.ERROR_CORRECT_H,
    border=4,
    box_size=10,
)

qr.add_data(data)

qr.make(fit = True)


img =  qr.make_image(fill_color = "green", back_color = "white")

img.save("demo qrcode.png")

print("QR code generated successfully ")