import os
import time

def update_terminal(sentence):
    # Split the multiline string into a list of lines
    print(sentence)
    
    # Clear the terminal screen one last time at the end


# Example usage
for x in range(1, 10):
    sentence = f'''{x}Hello, world!
    This is a test.
    Press any key.'''
    update_terminal(sentence)

    time.sleep(1)
    