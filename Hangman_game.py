import random

data = [
    "python", "hello", "akshay", "java", "flower", "mango",
    "guitar", "school", "planet", "rocket", "coffee", "mobile",
    "window", "castle", "orange", "banana", "sunset", "silver",
    "bottle", "camera", "forest", "island", "market", "pencil",
    "engine", "button", "bridge", "jungle", "dragon", "circle"
]

word = random.choice(data)

guess = ["_"] * len(word)

attempt = len(word) + 3

guessed_letters = []


print("Welcome to simple Hnagman game :")
print("Guess the letter of word ")

print(" ".join(guess))


while attempt > 0 and "_" in guess:

    inp = input("Enter a letter: ").lower()

    if len(inp) != 1 or not inp.isalpha():
        print("Invalid input. Please enter only one alphabet letter.")


    if inp in guessed_letters:
        print("You have already gussed that letter!!")
        continue

    guessed_letters.append(inp)

    if inp in word:
        print("correct")
        for i in range(len(word)):
            if word[i] == inp:
                guess[i] = inp
    else:
        attempt -= 1
        print("Wrong!! Number of attempt left : ",attempt)
    
    print(" ".join(guess))  # join the string or letters of any list.

if "_" not in guess:
    print("Congaratalation")
    print("Enterd word is :",word)
else:
    print("Better luck next time!!")
    print("The word was : ",word)


 


    



