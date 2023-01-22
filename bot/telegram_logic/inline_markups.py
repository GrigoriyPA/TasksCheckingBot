from bot import constants
from telebot import types
from typing import Optional

# All callback data must be different and represented by one char

# common
CALLBACK_SEPARATION_ELEMENT = "$"  # Element that divide callback data
CALLBACK_DATA_NONE = "0"  # Button do nothing


# get_results_table_inline_markup
BUTTON_NAME_OF_COLUMN_OF_USER_NUMBERS = "№"
BUTTON_NAME_OF_COLUMN_OF_USER_LOGINS = "Логин"
BUTTON_NAME_OF_CELL_OF_NOT_SOLVED_TASK = " "
BUTTON_NAME_OF_CELL_OF_RIGHT_SOLVED_TASK = "✅"
BUTTON_NAME_OF_CELL_OF_WRONG_SOLVED_TASK = "❌"
BUTTON_NAME_OF_ROW_OF_NUMBER_OF_SOLVED_TASKS = "Σ"
BUTTON_NAME_MOVE_TABLE_LEFT_ONE_STEP_NO_ACTION = " "
BUTTON_NAME_MOVE_TABLE_LEFT_MANY_STEPS_NO_ACTION = " "
BUTTON_NAME_MOVE_TABLE_LEFT_ONE_STEP_CAN_MOVE = "<"
BUTTON_NAME_MOVE_TABLE_LEFT_MANY_STEPS_CAN_MOVE = "<<"
BUTTON_NAME_MOVE_TABLE_RIGHT_ONE_STEP_NO_ACTION = " "
BUTTON_NAME_MOVE_TABLE_RIGHT_MANY_STEPS_NO_ACTION = " "
BUTTON_NAME_MOVE_TABLE_RIGHT_ONE_STEP_CAN_MOVE = ">"
BUTTON_NAME_MOVE_TABLE_RIGHT_MANY_STEPS_CAN_MOVE = ">>"
BUTTON_NAME_REFRESH_RESULTS_TABLE = "Обновить"

CALLBACK_DATA_FROM_LOGIN_IN_RESULTS_TABLE = "J"
CALLBACK_DATA_FROM_CELL_OF_SOLVED_TASK = "E"
CALLBACK_DATA_MOVE_RESULTS_TABLE = "I"
CALLBACK_DATA_REFRESH_RESULTS_TABLE = "G"


def get_results_table_inline_markup(results, homework_name: str, homework_size: int,
                                    first_task_id: int) -> types.InlineKeyboardMarkup:
    # This function returns table of buttons for table of results

    # Number of tasks that will add in table
    number_tasks = min(homework_size - first_task_id + 1, constants.TASKS_ON_ONE_PAGE)

    # Final keyboard storage
    keyboard = []

    # Temporary storage for current row
    row = [types.InlineKeyboardButton(text=BUTTON_NAME_OF_COLUMN_OF_USER_NUMBERS, callback_data=CALLBACK_DATA_NONE),
           types.InlineKeyboardButton(text=BUTTON_NAME_OF_COLUMN_OF_USER_LOGINS, callback_data=CALLBACK_DATA_NONE)]

    # Creating first line of the table (Number Login 1 2 ... number_tasks)
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(i + first_task_id), callback_data=CALLBACK_DATA_NONE))
    keyboard.append(row)

    amount = 0  # Number of right solved tasks
    row_id = 0  # Current row id
    rows = []  # Temporary storage for table (in final table rows can be in different order)
    rows_order = []  # Array of (number of solved tasks by user, user login, row id)
    sum_in_column = [0] * homework_size  # Number of right solved tasks in each column
    for result in results:
        # Add login button in current row
        row = [types.InlineKeyboardButton(text=result[0].login,
                                          callback_data=CALLBACK_DATA_FROM_LOGIN_IN_RESULTS_TABLE + result[0].login +
                                                       CALLBACK_SEPARATION_ELEMENT + homework_name)]

        task_id = 0  # Current task id
        current_sum = 0  # Number of right solved tasks by current user
        for answer in result[1]:
            # Update current task id
            task_id += 1

            # If user answer is correct, update sum of right answers
            if answer[0] == answer[1]:
                current_sum += 1
                sum_in_column[task_id - 1] += 1

            # If current task is visible (his id in [first_task_id, first_task_id + number_tasks)) add button for him
            if first_task_id <= task_id < first_task_id + number_tasks:
                if answer[0] is None or answer[0] == '':
                    # There is no answer from user on this task
                    row.append(types.InlineKeyboardButton(text=BUTTON_NAME_OF_CELL_OF_NOT_SOLVED_TASK,
                                                          callback_data=CALLBACK_DATA_NONE))
                elif answer[0] == answer[1]:
                    # User answer is right
                    row.append(types.InlineKeyboardButton(text=BUTTON_NAME_OF_CELL_OF_RIGHT_SOLVED_TASK,
                                                          callback_data=CALLBACK_DATA_FROM_CELL_OF_SOLVED_TASK +
                                                                       result[0].login + CALLBACK_SEPARATION_ELEMENT +
                                                                       homework_name + CALLBACK_SEPARATION_ELEMENT + str(task_id)))
                else:
                    # User answer is false
                    row.append(types.InlineKeyboardButton(text=BUTTON_NAME_OF_CELL_OF_WRONG_SOLVED_TASK,
                                                          callback_data=CALLBACK_DATA_FROM_CELL_OF_SOLVED_TASK +
                                                                       result[0].login + CALLBACK_SEPARATION_ELEMENT +
                                                                       homework_name + CALLBACK_SEPARATION_ELEMENT + str(task_id)))

        rows_order.append((-current_sum, result[0].login, row_id))  # Update rows order by current row
        amount += current_sum  # Update number of right solved tasks
        row_id += 1  # Update current row id

        # Add current row to table
        rows.append(row)
    rows_order.sort()  # Getting rows order

    # Add rows to final table in order rows_order
    row_id = 0
    for element in rows_order:
        row_id += 1

        # Add 'id' button in begin of the row
        keyboard.append([types.InlineKeyboardButton(text=str(row_id), callback_data=CALLBACK_DATA_NONE)] +
                        rows[element[2]])

    # Add row there placed sums of number of right answers
    row = [types.InlineKeyboardButton(text=BUTTON_NAME_OF_ROW_OF_NUMBER_OF_SOLVED_TASKS,
                                      callback_data=CALLBACK_DATA_NONE),
           types.InlineKeyboardButton(text=str(amount), callback_data=CALLBACK_DATA_NONE)]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(sum_in_column[i + first_task_id - 1]),
                                              callback_data=CALLBACK_DATA_NONE))
    keyboard.append(row)

    # Create buttons that can move table left
    left1 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_LEFT_ONE_STEP_NO_ACTION,
                                       callback_data=CALLBACK_DATA_NONE)
    left2 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_LEFT_MANY_STEPS_NO_ACTION,
                                       callback_data=CALLBACK_DATA_NONE)
    if first_task_id > 1:
        # Go left on 1
        left1 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_LEFT_ONE_STEP_CAN_MOVE,
                                           callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                         CALLBACK_SEPARATION_ELEMENT + str(first_task_id - 1))

        # Go left on TASKS_ON_ONE_PAGE
        left2 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_LEFT_MANY_STEPS_CAN_MOVE,
                                           callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                         CALLBACK_SEPARATION_ELEMENT +
                                                         str(max(first_task_id - constants.TASKS_ON_ONE_PAGE, 1)))

    # Create buttons that can move table right
    right1 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_RIGHT_ONE_STEP_NO_ACTION,
                                        callback_data=CALLBACK_DATA_NONE)
    right2 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_RIGHT_MANY_STEPS_NO_ACTION,
                                        callback_data=CALLBACK_DATA_NONE)
    if first_task_id + number_tasks - 1 < homework_size:
        # Go right on 1
        right1 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_RIGHT_ONE_STEP_CAN_MOVE,
                                            callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                          CALLBACK_SEPARATION_ELEMENT + str(first_task_id + 1))

        # Go right on TASKS_ON_ONE_PAGE
        right2 = types.InlineKeyboardButton(text=BUTTON_NAME_MOVE_TABLE_RIGHT_MANY_STEPS_CAN_MOVE,
                                            callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                          CALLBACK_SEPARATION_ELEMENT +
                                                          str(min(first_task_id + constants.TASKS_ON_ONE_PAGE, homework_size - constants.TASKS_ON_ONE_PAGE + 1)))

    # Add last row with 'refresh' button
    keyboard.append([left2, left1,
                     types.InlineKeyboardButton(text=BUTTON_NAME_REFRESH_RESULTS_TABLE,
                                                callback_data=CALLBACK_DATA_REFRESH_RESULTS_TABLE + homework_name +
                                                              CALLBACK_SEPARATION_ELEMENT + str(first_task_id)),
                     right1, right2])

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_all_homeworks_list_inline_markup(homework_list: list[str],
                                         callback_data: str) -> Optional[types.InlineKeyboardMarkup]:
    # This function returns table of buttons for list of homeworks

    homework_list.sort()

    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for name in homework_list:
        # Add button with name of current homework to table
        row.append(types.InlineKeyboardButton(text=name, callback_data=callback_data + name))

        # End current row on length HOMEWORKS_NUMBER_IN_LINE
        if len(row) == constants.HOMEWORKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

    # Add last row to table
    if len(row) > 0:
        keyboard.append(row)

    # If there is no homeworks created, just returns None
    if len(keyboard) == 0:
        return None

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_list_of_all_grades_inline_markup(callback_data: str) -> types.InlineKeyboardMarkup:
    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for grade_id in range(1, 12):
        # Add for current grade
        row.append(types.InlineKeyboardButton(text=str(grade_id), callback_data=callback_data + str(grade_id)))

        # End current row on length GRADES_IN_LINE
        if len(row) == constants.GRADES_IN_LINE:
            keyboard.append(row)
            row = []

    # Add last row to table
    if len(row) > 0:
        keyboard.append(row)

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_user_results_table(homework_list: list[str], user_results):
    # This function returns table of buttons for table of one user results

    keyboard = [[types.InlineKeyboardButton(text="Работа", callback_data="0"),
                 types.InlineKeyboardButton(text="Решено", callback_data="0"),
                 types.InlineKeyboardButton(text="Всего", callback_data="0")]]  # Final keyboard storage
    for row_id in range(len(homework_list)):
        # Add buttons on current row
        keyboard.append([types.InlineKeyboardButton(text=homework_list[row_id], callback_data="C" + homework_list[row_id]),
                    types.InlineKeyboardButton(text=str(user_results[row_id][0]), callback_data="0"),
                    types.InlineKeyboardButton(text=str(user_results[row_id][1]), callback_data="0")])

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_task_list(login: str, homework_size: int, homework_name: str, check_task):
    # This function returns table of buttons for tasks list

    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for task_id in range(1, homework_size + 1):
        task_state = check_task(login, homework_name, task_id)  # None - there is no user answer, True - user answer is right, False otherwise

        # Add button depend on task state
        if task_state is None:
            row.append(types.InlineKeyboardButton(text=str(task_id), callback_data="B" + homework_name + "$" + str(task_id)))
        elif task_state:
            row.append(types.InlineKeyboardButton(text=str(task_id) + " ✅", callback_data="D" + homework_name + "$" + str(task_id)))
        else:
            row.append(types.InlineKeyboardButton(text=str(task_id) + " ❌", callback_data="D" + homework_name + "$" + str(task_id)))

        # End current row on length TASKS_NUMBER_IN_LINE
        if len(row) == constants.TASKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

    # Add last row to table
    if len(row) > 0:
        keyboard.append(row)

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)
