from io import StringIO
import pytest
from robot import Robot, InvalidOperationException

@pytest.mark.unit_test
class TestPlace:
    def test_place_normally(self):
        """Should correctly place a bot if the command is valid
        """
        robot = Robot()
        directions = (
            'NORTH',
            'SOUTH',
            'WEST',
            'EAST'
        )
        test_positions = (
            (0, 0),
            (0, 4),
            (4, 0),
            (4, 4),
            (2, 2)
        )
        for pos in test_positions:
            for direction in directions:
                pos_x, pos_y = pos
                robot.place(**{'action_details': f'{pos_x},{pos_y},{direction}'})
                assert robot.placed == True
                assert robot.pos == pos
                assert robot.direction == direction

    def test_incomplete_command(self):
        """Should throw an exception if incomplete command is provided
        """
        robot = Robot()
        with pytest.raises(InvalidOperationException) as invalid_operation_exception:
            robot.place(**{})
        assert invalid_operation_exception.value.args[0] == 'Expect command to be "PLACE <X>, <Y>, <Facing>", got "PLACE"'
        assert robot.placed == False
        assert robot.pos == None
        assert robot.direction == None

    def test_invalid_placing_command(self):
        """Should throw an exception if invalid placing command is provided
        """
        robot = Robot()
        with pytest.raises(InvalidOperationException) as invalid_operation_exception:
            robot.place(**{'action_details': 'invalid_command'})
        assert invalid_operation_exception.value.args[0] == 'Expect command to be "PLACE <X>, <Y>, <Facing>", got "PLACE invalid_command"'
        assert robot.placed == False
        assert robot.pos == None
        assert robot.direction == None

    def test_invalid_placing_coordinate(self):
        """Should throw an exception if invalid coordinate in placing command is provided
        """
        robot = Robot()
        invalid_coordinates = [
            (-1, -1),
            (-1, 0),
            (0, -1),
            (5, 5),
            (5, 0),
            (0, 5)
        ]

        for invalid_coordinate in invalid_coordinates:
            pos_x, pos_y = invalid_coordinate
            with pytest.raises(InvalidOperationException) as invalid_operation_exception:
                robot.place(**{'action_details': f'{pos_x},{pos_y},NORTH'})
            assert invalid_operation_exception.value.args[0] == 'Invalid position in the map, should be within 0 to 5 in X and 0 to 5 in Y.'
            assert robot.placed == False
            assert robot.pos == None
            assert robot.direction == None

    def test_invalid_placing_direction(self):
        """Should throw an exception if invalid direction in placing command is provided
        """
        robot = Robot()
        with pytest.raises(InvalidOperationException) as invalid_operation_exception:
            robot.place(**{'action_details': f'0,0,INVALID_DIRECTION'})
        assert invalid_operation_exception.value.args[0] == "Invalid direction, should be one of ('NORTH', 'EAST', 'SOUTH', 'WEST')"
        assert robot.placed == False
        assert robot.pos == None
        assert robot.direction == None


@pytest.mark.unit_test
class TestMove:
    def test_move_normally(self):
        """Should move normally to each direction if the destination is valid
        """
        robot = Robot()
        robot.placed = True
        directions = ['NORTH', 'SOUTH', 'WEST', 'EAST']
        expected_destinations = [(2, 3), (2, 1), (1, 2), (3, 2)]
        for index, direction in enumerate(directions):
            robot.pos = (2, 2)
            robot.direction = direction
            robot.move()
            assert robot.pos == expected_destinations[index]

    def test_should_not_move_before_placed(self):
        """Should raise an exception if robot has not been placed and try to move
        """
        robot = Robot()
        with pytest.raises(InvalidOperationException) as invalid_operation_exception:
            robot.move()
        assert invalid_operation_exception.value.args[0] == 'A robot must be placed before any other command can be executed. Abort.'
        assert robot.pos == None

    def test_invalid_move(self):
        """Should raise an exception and not move the robot if the destionation is out of boundary
        """
        robot = Robot()
        robot.placed = True
        positions = [(0, 4), (0, 0), (0, 0), (4, 0)]
        directions = ['NORTH', 'SOUTH', 'WEST', 'EAST']
        expected_destinations = [(0, 5), (0, -1), (-1, 0), (5, 0)]
        for index, direction in enumerate(directions):
            robot.direction = direction
            robot.pos = positions[index]
            with pytest.raises(InvalidOperationException) as invalid_operation_exception:
                robot.move()
            assert invalid_operation_exception.value.args[0] == f'Destination {expected_destinations[index]} cannot be reached.'
            assert robot.pos == positions[index]
        

@pytest.mark.unit_test
class TestTurn:
    def test_turn_normally(self):
        """Should turn normally when turning LEFT or RIGHT and back to original direction if 4 same turns are taken
        """
        robot = Robot()
        robot.placed = True
        directions = ['NORTH', 'SOUTH', 'WEST', 'EAST']
        turnings = ['LEFT', 'RIGHT']
        for turning in turnings:
            robot.direction = 'NORTH'
            for i in range(4):
                expected_directions = ['WEST', 'SOUTH', 'EAST', 'NORTH']
                robot.turn(**{'direction': 'LEFT'})
                assert robot.direction == expected_directions[i]

    def test_should_not_turn_before_placed(self):
        """Should raise an exception if robot has not been placed and try to turn
        """
        robot = Robot()
        with pytest.raises(InvalidOperationException) as invalid_operation_exception:
            robot.turn(**{'direction': 'SOME DIRECTION'})
        assert invalid_operation_exception.value.args[0] == 'A robot must be placed before any other command can be executed. Abort.'
        assert robot.direction == None

    def test_turn_invalid_direction(self):
        """Should raise an exception if the turning direction is invalid
        """
        robot = Robot()
        robot.placed = True
        robot.direction = 'NORTH'
        with pytest.raises(InvalidOperationException) as invalid_operation_exception:
            robot.turn(**{'direction': 'invalid_direction'})
        assert invalid_operation_exception.value.args[0] == 'Turning direction should be either LEFT or RIGHT, got invalid_direction'
        assert robot.direction == 'NORTH'


@pytest.mark.integration_test
def test_integration(monkeypatch, capsys):
    command_files = [
        'commands/command_2'
    ]
    expeceted_outputs = [
        'commands/expected_output_2',
    ]
    for index, command_file in enumerate(command_files):
        robot = Robot()
        monkeypatch.setattr('sys.stdin', StringIO(f'{command_file}\n'))
        robot.run()
        captured_stdout, captured_stderr = capsys.readouterr()
        with open(expeceted_outputs[index]) as expeceted_output_file:
            assert expeceted_output_file.read() == captured_stdout

    