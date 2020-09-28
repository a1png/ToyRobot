
import sys
from typing import Tuple
from functools import wraps

# Sequence of directions in the order of turning right. When turning left, take the reversed order
DIRECTIONS = ('NORTH', 'EAST', 'SOUTH', 'WEST')

# Position change of x and y coordinate when the robot facing each direction moves by one step
STEP_BY_DIRECTION = {
    'NORTH': (0, 1),
    'SOUTH': (0, -1),
    'EAST': (1, 0),
    'WEST': (-1, 0)
}

# Size in x and y direction of the map
MAP_SIZE = (5, 5)

class InvalidOperationException(Exception):
    """Exception to be thrown when an invalid operation is done.
    """
    def __init__(self, message):
        super().__init__(message)


class Robot:
    def __init__(self, map_size: Tuple[int, int] = MAP_SIZE):
        """init method for the Robot class

        Args:
            map_size (Tuple[int, int], optional): Map size in a 2d vector (<int>, <int>) describing the size of two dimensions. Defaults to MAP_SIZE.
        """
        self.placed = False
        self.map_size_x, self.map_size_y = map_size
        self.map = (range(self.map_size_x), range(self.map_size_y))
        self.pos = None
        self.direction = None
        self.command_map = {
            'PLACE': { 'function': self.place },
            'LEFT': { 'function': self.turn, 'addtional_parameters': {'direction': 'LEFT'} },
            'RIGHT': { 'function': self.turn, 'addtional_parameters': {'direction': 'RIGHT'} },
            'MOVE': {'function': self.move },
            'REPORT': {'function':self.report },
            'EXIT': {'function': self.terminate }
        }
    
    def run(self):
        """Run the robot by reading command file from user input
        """
        command_file_location = input('Enter the command file: \n')
        try:
            with open(command_file_location) as command_file:
                commands = command_file.read().strip().split('\n')
                for command in commands:
                    command = command.upper()
                    try:
                        self.execute_command(command)
                    except InvalidOperationException as e:
                        print(e)
        except FileNotFoundError as error:
            print(f'{command_file_location} does not exists. Failed to run.')
            sys.exit(1)

    def execute_command(self, command: str):
        """Execute one line of given command

        Args:
            command (str): The command to be executed

        Raises:
            InvalidOperationException: Throws when there is invalid command provided
        """
        command_seq = command.strip().split(' ', 1)
        action = command_seq[0]
        executor = self.command_map.get(action)
        if executor is None:
            raise InvalidOperationException('Invalid command. Abort.')
        else:
            parameters = executor.get('addtional_parameters', {})
            if len(command_seq) > 1:
                parameters['action_details'] = command_seq[1]
            executor['function'](**parameters)


    def should_have_been_placed(f):
        """A decorator to check if a robot has been placed before other command can be executed.
        """
        @wraps(f)
        def check_placed(self, *args, **kwargs):
            if not self.placed:
                raise InvalidOperationException('A robot must be placed before any other command can be executed. Abort.')
            return f(self, *args, **kwargs)
        return check_placed

    def place(self, **kwargs):
        """Place a robot in a given location to a given direction with the `action_details` provided in kwargs

        Args:
            **kwargs:
                action_details (str, Required): Action details provided by the command in the format of "<pos_x>, <pos_y>, <direction>"


        Raises:
            InvalidOperationException: Raises when no action details is provided
            InvalidOperationException: Raises when invalid action details is provided
            InvalidOperationException: Raises when an invalid position is provided in action details
            InvalidOperationException: Raise when an invalid direction is provided in action details
        """
        action_details = kwargs.get('action_details')
        if action_details is None:
            raise InvalidOperationException(f'Expect command to be "PLACE <X>, <Y>, <Facing>", got "PLACE"')
        location_details = [detail.strip() for detail in action_details.split(',')]
        if len(location_details) != 3:
            raise InvalidOperationException(f'Expect command to be "PLACE <X>, <Y>, <Facing>", got "PLACE {action_details}"')

        pos_x, pos_y, direction = location_details
        pos = (int(pos_x), int(pos_y))
        if not self.is_valid_pos(pos):
            raise InvalidOperationException(f'Invalid position in the map, should be within 0 to {self.map_size_x} in X and 0 to {self.map_size_y} in Y.')
        if not self.is_valid_direction(direction):
            raise InvalidOperationException(f'Invalid direction, should be one of {DIRECTIONS}')

        self.pos = pos
        self.direction = direction
        self.placed = True
    
    @should_have_been_placed
    def move(self):
        """Move the robot by one step on the current direction if the destination is reachable

        Raises:
            InvalidOperationException: Raises when the destination is unreachable
        """
        if self.pos is None or self.direction is None:
            is_successful = False
        step = STEP_BY_DIRECTION.get(self.direction)
        next_pos = tuple(sum(pos) for pos in zip(self.pos, step))
        if not self.is_valid_pos(next_pos):
            raise InvalidOperationException(f'Destination {next_pos} cannot be reached.')
        self.pos = next_pos

    @should_have_been_placed
    def turn(self, **kwargs):
        """Turn the robot to left or right by 90 degrees
        
        Args:
            **kwargs:
                direction (str, Required): Direction the robot is going to turn, should be either 'LEFT' or 'RIGHT'


        Raises:
            InvalidOperationException: Raises when a direction other than 'LEFT' or 'RIGHT' is provided
        """
        directions = DIRECTIONS
        turning_direction = kwargs['direction']
        current_direction_index = directions.index(self.direction)
        if turning_direction == 'RIGHT':
            self.direction = directions[(current_direction_index + 1) % 4]
        elif turning_direction == 'LEFT':
            self.direction = directions[(current_direction_index - 1) % 4]
        else:
            raise InvalidOperationException(f'Turning direction should be either LEFT or RIGHT, got {turning_direction}')

    @should_have_been_placed
    def report(self):
        """Report the current position and direction of the robot in the form of '<pos_x>, <pos_y>, <direction>'
        """
        pos_x, pos_y = self.pos
        print(f'{pos_x}, {pos_y}, {self.direction}')

    def terminate(self):
        """Terminate the running of the program
        """
        print('End of service.')
        sys.exit(0)

    def is_valid_pos(self, pos: Tuple[int, int]):
        """Check if a position is valid in current map

        Args:
            pos (Tuple[int, int]): The position to be checked with coordinate (<pos_x>, <pos_y>)

        Returns:
            [bool]: The result whether a position is valid
        """
        if len(pos) != 2:
            return False
        pos_x, pos_y = pos
        return pos_x in self.map[0] and \
            pos_y in self.map[1]

    def is_valid_direction(self, direction: str):
        """Check if a direction is a valid direction.

        Args:
            direction (str): The direction to be checked

        Returns:
            [bool]: The result whether a direction is valid
        """
        return direction in DIRECTIONS


if __name__ == '__main__':
    robot = Robot()
    robot.run()