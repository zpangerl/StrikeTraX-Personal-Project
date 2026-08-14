def calculate_score(throws_array):
    throws_iter = 0
    total_pins_this_frame = 0
    current_total = 0
    current_throw = 1
    current_frame = 1
    game_frames = initialize_frames()
    return_JSON = {
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
            return_JSON["is_valid"] = False
            return return_JSON
        # If the current throw being processed is the first throw of a frame, is a strike, and is not in frame 10
        if (current_throw == 1 and next_throw == 10 and current_frame != 10):
            # check to see if next two throws exist to resolve strike
            # if they don't exist, we need to exit and return an invalid game response
            if (throws_iter + 2 >= len(throws_array)):
                # no need to check for next throw for display purposes here, since the game is invalid
                game_frames[current_frame - 1]["roll_1"] = next_throw
                return_JSON["frames"] = game_frames
                return_JSON["curr_throw"] = current_throw
                return_JSON["curr_frame"] = current_frame
                return_JSON["pins_left"] = 10 - total_pins_this_frame
                return_JSON["is_valid"] = False
                return return_JSON
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
                return_JSON["frames"] = game_frames
                return_JSON["curr_throw"] = current_throw
                return_JSON["curr_frame"] = current_frame
                return_JSON["pins_left"] = 10 - total_pins_this_frame
                return_JSON["is_valid"] = False
                return return_JSON
            # if the throw after the spare exists, update pin count for the frame
            total_pins_this_frame += next_throw
            # update current total, applying the next throw to the current spare per bowling rules
            current_total += next_throw
            current_total  += throws_array[throws_iter + 1]
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
                            return_JSON["is_valid"] = False
                            return return_JSON
                        # set total pins to 10, since the frame at this point is complete
                        total_pins_this_frame = 10
                        current_total += next_throw
                        game_frames[current_frame - 1]["roll_2"] = next_throw
                        game_frames[current_frame - 1]["current_total"] = current_total
                        current_throw += 1
                        #game is over, break
                        break
            # optional third throw, if strike or spare have been made in the first two throws
            elif (current_throw == 3):
                # check for extra, invalid throws
                if (throws_iter + 1 != len(throws_array)):
                    return_JSON["is_valid"] = False
                    return return_JSON
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
    # populate and return JSON object
    if (current_frame != 10 or current_throw < 3):
        return_JSON["is_valid"] = False
    elif (current_frame == 10 and current_throw == 3):
        frame_10_sum = game_frames[9]["roll_1"] + game_frames[9]["roll_2"]
        if (frame_10_sum >= 10):
            return_JSON["is_valid"] = False
    return_JSON["total"] = current_total
    return_JSON["curr_throw"] = current_throw
    return_JSON["curr_frame"] = current_frame
    return_JSON["pins_left"] = 10 - total_pins_this_frame
    return_JSON["frames"] = game_frames
    return return_JSON

def initialize_frames():
    frames = [{"frame": x + 1, "roll_1": None, "roll_2": None, "current_total": None} for x in range(0, 9)]
    frames.append({"frame": 10, "roll_1": None, "roll_2": None, "roll_3": None, "current_total": None})
    return frames

def validate_throw(throw_val, pins_val):
    if (type(throw_val) is not int or throw_val < 0 or throw_val > pins_val): return False
    else: return True