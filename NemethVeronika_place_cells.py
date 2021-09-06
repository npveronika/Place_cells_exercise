MIN_TIME_IN_POSITIONS = 1819155
MAX_TIME_IN_POSITIONS = 2014700
UP_INDEX = 0
DOWN_INDEX = 1
TOP_INDEX = 2
BOTTOM_INDEX = 3


def conversion_of_txt_files(file_name):
    with open(file_name, "r") as file_name:
        data_list = file_name.readlines()
        string_data_list = [row.rstrip().split() for row in data_list]

    string_data_list_with_valid_data = [data for data in string_data_list if not data[1].isalpha()]
    data_list_with_numbers = [[int(float(row[0]) * 100 + 0.1), float(row[1])] for row in string_data_list_with_valid_data]
    return data_list_with_numbers


def convert_time_to_index(time_number):
    return time_number - MIN_TIME_IN_POSITIONS


def create_all_cells_timeline(spike):
    """
    Return: 120 different nested lists. Indexes: timeline. Elements: number of spikes.
    """
    all_cells_timeline = [[0 for item in range(MAX_TIME_IN_POSITIONS - MIN_TIME_IN_POSITIONS)] for item in range(121)]
    start_index = spike.index([1819196, 111])
    stop_index = spike.index([2014698, 59])
    for i in range(start_index, stop_index):
        all_cells_timeline[int(spike[i][1])][convert_time_to_index(spike[i][0])] += 1
    return all_cells_timeline


def create_pos_timeline(pos):
    """
    Return: a list. Indexes: timeline. Elements: positions of the rat.
    """
    p_timeline = [None for x in range(MAX_TIME_IN_POSITIONS - MIN_TIME_IN_POSITIONS)]
    for i in range(len(pos) - 1):
        index = convert_time_to_index(pos[i][0])
        p_timeline[index] = pos[i][1]
    for i in range(len(p_timeline)):
        if p_timeline[i] is None:
            p_timeline[i] = p_timeline[i - 1]
    return p_timeline


def mask_function_top(p_timeline):
    """
    Positions except on the top of the route are masked.
    Return: a list. Indexes: timeline. Elements: masked positions.
    """
    timeline = [0 for x in range(len(p_timeline))]
    for i in range(len(p_timeline)):
        if 1.35 <= p_timeline[i] <= 1.38:
            timeline[i] = 1
        else:
            timeline[i] = 0
    return timeline


def mask_function_bottom(p_timeline):
    """
    Positions except on the bottom of the route are masked.
    Return: a list. Indexes: timeline. Elements: masked positions.
    """
    timeline = [0 for x in range(len(p_timeline))]
    for i in range(len(p_timeline)):
        if -0.51 <= p_timeline[i] <= -0.37:
            timeline[i] = 1
        else:
            timeline[i] = 0
    return timeline


def mask_function_up_route(p_timeline):
    """
    Positions except up routes are masked.
    Return: a list. Indexes: timeline. Elements: masked positions.
    """
    timeline = [0 for x in range(len(p_timeline))]
    for i in range(1, len(p_timeline) - 30):
        if p_timeline[i] == - 0.3 and p_timeline[i] < p_timeline[i + 30]:
            while p_timeline[i] != 1.3:
                timeline[i] = 1
                i += 1
    return timeline


def mask_function_down_route(p_timeline):
    """
    Positions except down routes are masked.
    Return: a list. Indexes: timeline. Elements: masked positions.
    """
    timeline = [0 for x in range(len(p_timeline))]
    for i in range(1, len(p_timeline) - 30):
        if p_timeline[i] == 1.3 and p_timeline[i] - p_timeline[i + 30] > 0:
            while p_timeline[i] != - 0.3:
                timeline[i] = 1
                i += 1
    return timeline


def create_dict_for_different_positions_of_active_cells(p_timeline, all_cells_timeline):
    """
    Return: a dict. Keys: cell_id. Values: number of spikes [up route, down route, top, bottom]
    """
    masked_cell_up = mask_function_up_route(p_timeline)
    masked_cell_top = mask_function_top(p_timeline)
    masked_cell_bottom = mask_function_bottom(p_timeline)
    masked_cell_down = mask_function_down_route(p_timeline)
    spikes_of_cells = dict()
    for i in range(1, 121):
        sum_of_spikes_up = (sum([num1 * num2 for num1, num2 in zip(all_cells_timeline[i], masked_cell_up)]))
        sum_of_spikes_down = (sum([num1 * num2 for num1, num2 in zip(all_cells_timeline[i], masked_cell_down)]))
        sum_of_spikes_top = (sum([num1 * num2 for num1, num2 in zip(all_cells_timeline[i], masked_cell_top)]))
        sum_of_spikes_bottom = (sum([num1 * num2 for num1, num2 in zip(all_cells_timeline[i], masked_cell_bottom)]))
        sum_of_all = sum(all_cells_timeline[i])
        spikes_of_cells[i] = [sum_of_spikes_up, sum_of_spikes_down, sum_of_spikes_top, sum_of_spikes_bottom, sum_of_all]
    print(spikes_of_cells[13])
    return spikes_of_cells


def search_cells_for_bottom_or_top(dict_of_spikes, dict_index):
    """
    Return: a list. Indexes: cell_id. Elements: (cell_id, percent of spikes on top or bottom route).
    """
    cells = list()
    for i in range(1, 121):
        spikes_percent = round((dict_of_spikes[i][dict_index] / dict_of_spikes[i][4]) * 100, 2)
        if spikes_percent > 73:
            cells.append((i, spikes_percent))
    return cells


def compare_number_of_spikes_on_up_route_with_down_route_for_one_cell(dict_of_spikes, cell_id):
    return round(dict_of_spikes[cell_id][UP_INDEX] /
                 (dict_of_spikes[cell_id][UP_INDEX] + dict_of_spikes[cell_id][DOWN_INDEX]), 3)


def compare_number_of_spikes_on_down_route_with_up_route_for_one_cell(dict_of_spikes, cell_id):
    return round(dict_of_spikes[cell_id][DOWN_INDEX] /
                 (dict_of_spikes[cell_id][UP_INDEX] + dict_of_spikes[cell_id][DOWN_INDEX]), 3)


def search_cells_more_active_on_up_route__compared_to_up_and_down_routes(dict_of_spikes):
    """
    Return: a list: Indexes: cell_id. Elements: number of spikes on up routes compared to up and down routes.
    """
    cells = list()
    for i in range(1, 121):
        relation = compare_number_of_spikes_on_up_route_with_down_route_for_one_cell(dict_of_spikes, i)
        if relation > 0.7:
            cells.append((i, relation))
    return cells


def search_cells_more_active_on_down_route__compared_to_up_and_down_routes(dict_of_spikes):
    """
    Return: a list: Indexes: cell_id. Elements: number of spikes on down routes compared to up and down routes.
    """
    cells = list()
    for i in range(1, 121):
        relation = compare_number_of_spikes_on_down_route_with_up_route_for_one_cell(dict_of_spikes, i)
        if relation > 0.7:
            cells.append((i, relation))
    return cells


if __name__ == "__main__":
    positions = conversion_of_txt_files("position.txt")
    spikes = conversion_of_txt_files("spikes.txt")
    all_cells_timelines = create_all_cells_timeline(spikes)
    pos_timeline = create_pos_timeline(positions)
    spikes_of_all_cells_at_different_positions = create_dict_for_different_positions_of_active_cells(pos_timeline, all_cells_timelines)
    mostly_active_on_the_top_cells = search_cells_for_bottom_or_top(spikes_of_all_cells_at_different_positions, TOP_INDEX)
    mostly_active_on_the_bottom_cells = search_cells_for_bottom_or_top(spikes_of_all_cells_at_different_positions, BOTTOM_INDEX)
    cells_more_active_on_up_route_than_down_route = search_cells_more_active_on_up_route__compared_to_up_and_down_routes\
        (spikes_of_all_cells_at_different_positions)
    cells_more_active_on_down_route_than_up_route = search_cells_more_active_on_down_route__compared_to_up_and_down_routes(
        spikes_of_all_cells_at_different_positions)

    print("Cells mostly active on the top of the route:")
    for k in range(len(mostly_active_on_the_top_cells)):
        print(f"\tcell_id {mostly_active_on_the_top_cells[k][0]}, "
              f"percent of spikes on the top {mostly_active_on_the_top_cells[k][1]}%.")
    print()
    print("Cells mostly active on the bottom of the route:")
    for k in range(len( mostly_active_on_the_bottom_cells)):
        print(f"\tcell_id {mostly_active_on_the_bottom_cells[k][0]}, "
              f"percent of spikes on the bottom {mostly_active_on_the_bottom_cells[k][1]}%")
    print()
    print("Cells more active on up route than down route:")
    for k in range(len(cells_more_active_on_up_route_than_down_route)):
        print(f"\tcell_id {cells_more_active_on_up_route_than_down_route[k][0]}, "
              f"ratio {cells_more_active_on_up_route_than_down_route[k][1]}")
    print()
    print("Cells more active on down route than up route:")
    for k in range(len(cells_more_active_on_down_route_than_up_route)):
        print(f"\tcell_id {cells_more_active_on_down_route_than_up_route[k][0]}, "
              f"ratio {cells_more_active_on_down_route_than_up_route[k][1]}")


