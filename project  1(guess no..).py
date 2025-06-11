import random

while True:
    choice = input("Enter any number(1-50) OR Q for quit the game: ")
    a = random.randint(0,5)
    if(choice == 'Q' or choice == 'q'):
        print("Exit Successfully")
        break
    choice = int(choice)

    if(a == choice):
        print("congratulation ! you win the game")
    else:
        print("Better luck next time!!")

