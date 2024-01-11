# AI DigDug

## Description

DigDug is a game where the player digs tunnels through the ground and kills enemies by pumping them with air until they explode. The player can also drop rocks on enemies to kill them. The player wins when all enemies are dead.

This project is the implementation of an AI that plays DigDug. The AI is implemented using the A* algorithm to find the shortest path to the enemy and then it uses a state machine to decide what to do next.

## How to run

Make sure you are running Python 3.11.

`$ pip install -r requirements.txt`

`$ python3 server.py`

`$ python3 viewer.py`

`$ python3 student.py`

If you want to play the game yourself, run the following command instead of the last one:

`$ python3 client.py`

## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- MacOS 13.6

