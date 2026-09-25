"""Functions to recalculate bowling scores server-side.

Ported from scoring.js for use with Python files.
"""
def calculate_score(throws_array):
    """Calculate the score of the provided throws information.

    Additionally validates the game, both against bowling rules and the score from the client.

    Games must be finished, unfinished games will be rejected.

    Args:
        throws_array: The list of throws from the completed bowling game.

    Returns:
        A dict, with the following keys:
            frames: A list of 10 frame dicts with a valid game. May be None or partially filled
            when is_valid is false, depending on where the validation failed.
            is_valid: True if throws_array is a valid, finished game.
            curr_throw: The throw number that was reached in the current frame.
            curr_frame: The current frame.
            pins_left: Pins remaining in the current frame.
            total: The final score, or None if is_valid is false.
    """
    throws_iter = 0
    total_pins_this_frame = 0
    current_total = 0
    current_throw = 1
    current_frame = 1
    game_frames = initialize_frames()
    return_json = {
        "frames": None,
        "is_valid": True,
        "curr_throw": 1,
        "curr_frame": 1,
        "pins_left": 10,
        "total": None
    }

    while (throws_iter < len(throws_array)):
        next_throw = throws_array[throws_iter]
        if (not validate_throw(next_throw, 10 - total_pins_this_frame)):
            return_json["is_valid"] = False
            return return_json
        # If the current throw being processed is the first throw of a frame, is a strike, and is not in frame 10
        if (current_throw == 1 and next_throw == 10 and current_frame != 10):
            # check to see if next two throws exist to resolve strike
            # if they don't exist, we need to exit and return an invalid game response
            if (throws_iter + 2 >= len(throws_array)):
                # no need to check for next throw for display purposes here, since the game is invalid
                game_frames[current_frame - 1]["roll_1"] = next_throw
                return_json["frames"] = game_frames
                return_json["curr_throw"] = current_throw
                return_json["curr_frame"] = current_frame
                return_json["pins_left"] = 10 - total_pins_this_frame
                return_json["is_valid"] = False
                return return_json
            # if the 2 throws after the strike exist, update pin count for the frame
            total_pins_this_frame += next_throw
            # update current total, applying the next two throws to the current strike per bowling rules
            current_total += next_throw
            current_total += throws_array[throws_iter + 1]
            current_total += throws_array[throws_iter + 2]
            game_frames[current_frame - 1]["roll_1"] = next_throw
            game_frames[current_frame - 1]["current_total"] = current_total
            current_throw += 1
        # if the current throw is the second throw of a frame, is a spare, and is not in frame 10
        elif (current_throw == 2 and next_throw == (10 - total_pins_this_frame) and current_frame != 10):
            # check to see if next throw exists to resolve spare
            # if it doesn't exist, we need to exit and return an invalid game response
            if (throws_iter + 1 >= len(throws_array)):
                game_frames[current_frame - 1]["roll_2"] = next_throw
                game_frames[current_frame - 1]["current_total"] = None
                return_json["frames"] = game_frames
                return_json["curr_throw"] = current_throw
                return_json["curr_frame"] = current_frame
                return_json["pins_left"] = 10 - total_pins_this_frame
                return_json["is_valid"] = False
                return return_json
            # if the throw after the spare exists, update pin count for the frame
            total_pins_this_frame += next_throw
            # update current total, applying the next throw to the current spare per bowling rules
            current_total += next_throw
            current_total += throws_array[throws_iter + 1]
            game_frames[current_frame - 1]["roll_2"] = next_throw
            # update current total of current frame, since spare is fully resolved
            game_frames[current_frame - 1]["current_total"] = current_total
            current_throw += 1
        # if the frame is specifically frame 10
        # frame 10 is a special case, three potential throws instead of 2 if you get a strike/spare
        # additionally, strikes and spares made in frame 10 do not apply double the next throw(s)
        elif (current_frame == 10):
            # first throw
            if (current_throw == 1):
                # if the throw isn't a strike, update pin counter
                if (next_throw != 10):
                    total_pins_this_frame += next_throw
                else: total_pins_this_frame = 0
            # second throw
            elif (current_throw == 2):
                # check if the first throw was a strike, if it is we don't have to check if this is a spare
                if (game_frames[current_frame - 1]["roll_1"] == 10):
                    # if this throw is also a strike, set pin counter to 0
                    if (next_throw == 10): total_pins_this_frame = 0
                    # if this throw isn't a strike, update pin counter
                    else: total_pins_this_frame += next_throw
                # if the first throw was not a strike
                else:
                    # need to check if this throw is a spare, if it is set pin count to 0
                    if (next_throw == (10 - total_pins_this_frame)): total_pins_this_frame = 0
                    # if not, the game is over
                    else:
                        # check for extra, invalid throws
                        if (throws_iter + 1 != len(throws_array)):
                            return_json["is_valid"] = False
                            return return_json
                        # set total pins to 10, since the frame at this point is complete
                        total_pins_this_frame = 10
                        current_total += next_throw
                        game_frames[current_frame - 1]["roll_2"] = next_throw
                        game_frames[current_frame - 1]["current_total"] = current_total
                        current_throw += 1
                        # game is over, break
                        break
            # optional third throw, if strike or spare have been made in the first two throws
            elif (current_throw == 3):
                # check for extra, invalid throws
                if (throws_iter + 1 != len(throws_array)):
                    return_json["is_valid"] = False
                    return return_json
                current_total += next_throw
                game_frames[current_frame - 1]["roll_3"] = next_throw
                # update current total of current frame
                game_frames[current_frame - 1]["current_total"] = current_total
                current_throw += 1
                # game is over, break
                break
            # for any throw in frame 10 that isn't the last throw of the game
            current_total += next_throw
            game_frames[current_frame - 1][f"roll_{current_throw}"] = next_throw
            # we don't need to worry about waiting to display the current total, strikes and spares made in frame 10 don't apply bonuses
            game_frames[current_frame - 1]["current_total"] = current_total
            current_throw += 1
        # if not a strike, spare, or frame 10
        else:
            total_pins_this_frame += next_throw
            current_total += next_throw
            game_frames[current_frame - 1][f"roll_{current_throw}"] = next_throw
            # if the current throw isn't the first, frame is finished, so update the current total of the current frame
            # if the frame isn't finished, we don't display the current frame's score yet
            # this will also keep the first throw after a strike from displaying a score before the strike is resolved
            if (current_throw != 1):
                game_frames[current_frame - 1]["current_total"] = current_total
            current_throw += 1
        # if current_throw is more than 2 or pin counter is 10, frame is over
        # frame 10 is a special case, handled separately
        if ((current_throw > 2 or total_pins_this_frame == 10) and current_frame != 10):
            # reset current_throw for next frame
            current_throw = 1
            current_frame += 1
            total_pins_this_frame = 0
        throws_iter += 1
    # If current_frame is not 10, the game is not over, and is not valid.
    # If current_throw is less than 3, the game is also not over, and is not valid.
    if (current_frame != 10 or current_throw < 3):
        return_json["is_valid"] = False
    # If frame 10 ends after the second throw.
    elif (current_frame == 10 and current_throw == 3):
        # Verify that roll_1 and roll_2 added are not greater than or equal to 10.
        frame_10_sum = game_frames[9]["roll_1"] + game_frames[9]["roll_2"]
        # If they are, we are missing a bonus throw, and the game is invalid.
        if (frame_10_sum >= 10):
            return_json["is_valid"] = False
    # populate and return JSON object
    return_json["total"] = current_total
    return_json["curr_throw"] = current_throw
    return_json["curr_frame"] = current_frame
    return_json["pins_left"] = 10 - total_pins_this_frame
    return_json["frames"] = game_frames
    return return_json

def initialize_frames():
    """Create an empty set of frames for a bowling game.

    Initializes game state fields to None.

    Returns:
        A list of ten frame dicts, each with:
            frame: The frame number.
            roll_1: The first throw of the frame.
            roll_2: The second throw of the frame.
            roll_3: The third throw of the frame, only for frame 10.
            current_total: The total of the game at the end of the frame.
    """
    frames = [{"frame": x + 1, "roll_1": None, "roll_2": None, "current_total": None} for x in range(9)]
    frames.append({"frame": 10, "roll_1": None, "roll_2": None, "roll_3": None, "current_total": None})
    return frames

def validate_throw(throw_val, pins_val):
    """Verify that a specific throw is valid.
    
    Checks if the throw is an int, is not less than 0, and is not more than the current pin count.

    Args:
        throw_val: The value of the throw to be validated.
        pins_val: The current maximum number of possible pins.

    Returns:
        False if throw is invalid, True if throw is valid.
    """
    return not (type(throw_val) is not int or throw_val < 0 or throw_val > pins_val)