from scoring import validate_throw, calculate_score, initialize_frames

# validate_throw
def test_returns_false_for_a_non_number_value():
    assert(not validate_throw('5', 10))
def test_returns_false_for_a_negative_value():
    assert(not validate_throw(-1, 10))
def test_returns_false_for_a_value_greater_than_the_pins_available():
    assert(not validate_throw(6, 5))
def test_returns_true_for_a_value_within_range():
    assert(validate_throw(4, 10))
def test_returns_true_at_the_lower_boundary():
    assert(validate_throw(0, 10))
def test_returns_true_at_the_upper_boundary():
    assert(validate_throw(7, 7))

# initialize_frames

def test_returns_10_frames():
    frames = initialize_frames()
    assert(len(frames) == 10)
def test_numbers_each_frame_1_to_10():
    frames = initialize_frames()
    frame_num = 1
    for frame in frames:
        assert(frame["frame"] == frame_num)
        frame_num += 1
def test_initializes_rolls_and_current_total_to_None_for_frames_1_to_9():
    frames = initialize_frames()
    for frame in frames:
        assert(frame["roll_1"] is None)
        assert(frame["roll_2"] is None)
        assert(frame["current_total"] is None)
def test_initializes_rolls_and_current_total_to_None_for_frame_10():
    frames = initialize_frames()
    frame10 = frames[9]
    assert(frame10["roll_1"] is None)
    assert(frame10["roll_2"] is None)
    assert(frame10["roll_3"] is None)
    assert(frame10["current_total"] is None)

# calculate_score validation
def test_flags_the_game_invalid_when_a_throw_is_negative():
    result = calculate_score([-1])
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_a_throw_exceeds_the_pins_remaining():
    result = calculate_score([6, 5])
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_a_throw_is_not_a_number():
    result = calculate_score(['strike'])
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_there_are_extra_throws_after_an_open_10th_frame():
    throws = [0 for i in range(18)]
    throws.extend([6, 3, 5])
    result = calculate_score(throws)
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_there_are_extra_throws_after_a_completed_bonus_throw_in_the_10th_frame():
    throws = [0 for i in range(18)]
    throws.extend([10, 10, 10, 5])
    result = calculate_score(throws)
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_there_are_no_throws_after_a_frame_1_to_9_strike():
    throws = [10]
    result = calculate_score(throws)
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_there_is_one_throw_after_a_frame_1_to_9_strike():
    throws = [10, 4]
    result = calculate_score(throws)
    assert(not result["is_valid"])
def test_flags_the_game_invalid_when_there_is_an_unresolved_frame_1_to_9_spare():
    throws = [6, 4]
    result = calculate_score(throws)
    assert(not result["is_valid"])

# calculate_score strikes in frames 1-9
def test_resolves_the_strike_and_reveals_the_total_once_both_bonus_throws_are_available():
    throws = [10, 3, 4]
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][0]["roll_1"] == 10)
    assert(result["frames"][0]["current_total"] == 17)
    assert(result["curr_frame"] == 3)
    return

# calculate_score spares in frames 1-9
def test_resolves_the_spare_and_reveals_the_total_once_bonus_throw_is_available():
    throws = [6, 4, 5]
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][0]["current_total"] == 15)
    assert(result["curr_frame"] == 2)
    return

# calculate_score open frames in frames 1-9
def test_reveals_the_total_once_both_throws_of_an_open_frame_are_complete():
    throws = [3, 4]
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][0]["roll_1"] == 3)
    assert(result["frames"][0]["roll_2"] == 4)
    assert(result["frames"][0]["current_total"] == 7)
    assert(result["curr_frame"] == 2)
    assert(result["curr_throw"] == 1)
    return

# calculate_score frame 10
def test_tracks_a_non_strike_first_throw():
    throws = [0 for i in range(18)]
    throws.append(5)
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["curr_frame"] == 10)
    assert(result["curr_throw"] == 2)
    assert(result["frames"][9]["roll_1"] == 5)
    return
def test_tracks_a_strike_first_throw():
    throws = [0 for i in range(18)]
    throws.append(10)
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["curr_throw"] == 2)
    assert(result["frames"][9]["roll_1"] == 10)
    return
def test_tracks_a_second_throw_strike_after_a_first_throw_strike():
    throws = [0 for i in range(18)]
    throws.extend([10, 10])
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][9]["roll_1"] == 10)
    assert(result["frames"][9]["roll_2"] == 10)
    assert(result["curr_throw"] == 3)
    return
def test_tracks_a_non_strike_second_throw_after_a_first_throw_strike():
    throws = [0 for i in range(18)]
    throws.extend([10, 4])
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][9]["roll_2"] == 4)
    assert(result["curr_throw"] == 3)
    return
def test_tracks_a_second_throw_that_completes_a_spare():
    throws = [0 for i in range(18)]
    throws.extend([6, 4])
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][9]["roll_1"] == 6)
    assert(result["frames"][9]["roll_2"] == 4)
    assert(result["curr_throw"] == 3)
    return
def test_records_an_open_10th_frame_that_does_not_earn_a_bonus_throw():
    throws = [0 for i in range(18)]
    throws.extend([6, 3])
    result = calculate_score(throws)
    assert(result["is_valid"] == True)
    assert(result["frames"][9]["roll_1"] == 6)
    assert(result["frames"][9]["roll_2"] == 3)
    assert(result["total"] == 9)
    return
def test_records_a_third_throw_following_an_earned_bonus_and_reveals_the_total_immediately():
    throws = [0 for i in range(18)]
    throws.extend([10, 10, 10])
    result = calculate_score(throws)
    assert(result["is_valid"])
    assert(result["frames"][9]["roll_1"] == 10)
    assert(result["frames"][9]["roll_2"] == 10)
    assert(result["frames"][9]["roll_3"] == 10)
    assert(result["total"] == 30)
    return
def test_reveals_frame_10_totals_progressively():
    throws = [0 for i in range(18)]
    throws.extend([10, 4])
    result = calculate_score(throws)
    assert(not result["is_valid"])
    assert(result["frames"][9]["current_total"] == 14)
    return

# calculate_score full games
def test_scores_a_perfect_game_as_300():
    throws = [10 for i in range(12)]
    result = calculate_score(throws)
    assert(result["is_valid"] == True)
    assert(result["total"] == 300)
    assert(result["frames"][9]["current_total"] == 300)
    return
def test_scores_an_all_gutter_game_as_0():
    throws = [0 for i in range(20)]
    result = calculate_score(throws)
    assert(result["is_valid"] == True)
    assert(result["total"] == 0)
    assert(result["frames"][9]["current_total"] == 0)
    return
def test_scores_a_realistic_mixed_game_correctly():
    throws = [5, 3, 3, 5, 10, 10, 1, 3, 4, 4, 5, 5, 6, 3, 6, 3, 5, 4]
    result = calculate_score(throws)
    assert(result["is_valid"] == True)
    assert(result["frames"][0]["current_total"] == 8)
    assert(result["frames"][1]["current_total"] == 16)
    assert(result["frames"][9]["current_total"] == result["total"])
    return