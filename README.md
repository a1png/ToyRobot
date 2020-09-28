# ToyRobot
The application is a simulation of a toy robot moving on a square table top, of default dimensions of 5 units x 5 units. 

## Getting started
### Setting up environment
1. __Python version__: The code is written and tested under Python 3.7
1. run `pip install -r requirements.txt` to install the necessary libraries
### Running the program
#### Run the main program:
1. Write a command file that the robot can understand. See [Command file section](##Command-File) or existing examples under `commands/`


2. Run `python robot.py` in console and enter the path to the command file as prompted
#### Run tests
1. Make sure _pytest_ is correctly installed
2. Run `pytest` in the working directory

## Command File
### Writing a command file
Write each command in one line in the order the commands are supposed to be executed. Commands can be written in upper or lower cases.
### Supported commands
1. `PLACE <pos_x>, <pos_y>, <direction>` Places the robot to the given location on coordinate (_pos_x_, _pos_y_) with given _direction_
2. `MOVE` Moves the robot by one step on its current direction. 
    - Should be done after the robot is placed with `PLACE` command, otherwise the command will not be executed.
    - The destination should be a valid position, i.e. within the current map. Otherwise the command will not be executed.
3. `LEFT`/`RIGHT` Turns the robot to its left/right by 90 degrees.
4. `REPORT` Reports the robot's current position and direction in the form of `<pos_x>, <pos_y>, <direction>`