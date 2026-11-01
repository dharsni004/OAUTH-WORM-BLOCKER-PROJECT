import smtplib
EMAIL="hanubug27@gmail.com"
PASSWORD="ksiftrirstqumrrg"
try:
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(EMAIL,PASSWORD)
        print("LOGIN SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")