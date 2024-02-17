from visualizationref import *
import random 
import math
# example classification results
results = {"Hands": 0.141,
           "Inside, small room": 0.107,
           "Speech": 0.101,
           "Singing": 0.080,
           "Door":0.080}

visulization_result = {}
for sounds,score in results.items():
    visulization_result[sounds] = get_sound_label(sounds) + random.random()
    
print(visulization_result)

def getthesequence(visulization_result):
  sequence = []
  # list the keys in the dictionary based on their value in descending order
  sorted_keys = sorted(visulization_result, key=visulization_result.get, reverse=True)
  for key in sorted_keys:
    sequence.append(key)
  return sequence

print(getthesequence(visulization_result))
# Function to print a circle with a word inside

def get_sound_symbol(sound):
  # get the sound intense
  sound_intense = get_sound_intense(sound)
  if sound_intense > 6:
    return random.choice(["#","%", "@"])
  elif sound_intense > 4:
    return random.choice(["&", "$", "!"])
  else:
    return random.choice([".", "=", "*"])

def print_circle_with_word_inside(radius, word, symbol="|", indent=0):
    size = radius * 2
    width = size
    word_length = len(word)
    word_start_indx = (width - word_length) // 2

    # Calculate the center of the circle
    center_x = width // 2
    center_y = radius

    for y in range(size):
        for _ in range(indent):
            print(" ", end='')
        for x in range(width):
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            
            if y == center_y:
              #check if the word is longer than the radius
                #if the word is longer than the radius, print the word in the middle of the circle 
                if x<word_start_indx or x>word_start_indx+word_length-1:
                  print(" ", end='')
                else:
                  print(word, end='')
                  break
            elif distance < radius:
                    print(symbol, end='')
            else:
                print(" ", end='')
        print()

# Define the radius and word for the circle
# circle_radius = 7
# word = "Hellosmallroom"

# Call the function to print the circle with the word
# print_circle_with_word_inside(circle_radius, word, "*")
    
def printcircle_insequecne(visulization_result):
  # get the sounds with the highest value
  sequence = getthesequence(visulization_result)
  for sound in sequence:
    circle_radius = round(results[sound] * 100)
    word = sound
    print_circle_with_word_inside(circle_radius, word, get_sound_symbol(sound), random.randint(0, 30))
    
printcircle_insequecne(visulization_result)
  
