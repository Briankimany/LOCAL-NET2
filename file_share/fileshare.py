import main
from server import app
import re


while True:
    print("Welome to local share .....")
    choice = input("Enter 1 to serve or to 2 recieve: ")
    choice =re.sub("\t", "",choice)
    [re.sub(i , '' , choice) for i in ["'" , "'" , " "]]
    print(choice)
    print("hrre is your choice," , choice)
    choice= choice.strip()
    if choice != "":
        choice = int(choice)
        if choice == 1 or choice == 2:
            break
        else:
            print(f"Invalid choice !!!!: {choice}")


if choice == 1:
    app.run("0.0.0.0" , port = 5000)

elif choice == 2:
    main.multirun()


