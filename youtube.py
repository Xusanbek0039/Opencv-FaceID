while True:
    yosh = int(input("Yoshingizni kiriting (Dastur toxtashi uchun 0 kiriting): "))

    if yosh == 0:
        print("dastur tugadi.")
        break
    elif yosh < 18:
        print("hali kichkina ekansiz.")
    else:
        print("Xush kelibsiz.")