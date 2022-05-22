import string 
import random 


def generateRandomString(str_length: int = 20):

    # printing lowercase
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_length))