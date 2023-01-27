from bot import constants
from bot.entities.homework import Homework
from bot.entities.result import Result
from bot.telegram_logic.interface import messages_text
from telebot import types
from typing import Optional

# Callback codes description
# All callback codes must be different and represented by one char

# common
CALLBACK_SEPARATION_ELEMENT = "$"  # Element that divide callback data
CALLBACK_DATA_NONE = chr(0)  # Button do nothing

# other (used in handling_functions)
CALLBACK_DATA_SELECT_HOMEWORK_FOR_SEND_ANSWER = chr(1)
CALLBACK_DATA_SELECT_STUDENT_GRADE_FOR_CREATE = chr(2)
CALLBACK_DATA_SELECT_EXERCISE_GRADE_FOR_CREATE = chr(3)

# get_results_table_inline_markup
CALLBACK_DATA_FROM_LOGIN_IN_RESULTS_TABLE = chr(4)
CALLBACK_DATA_FROM_CELL_OF_TASK = chr(5)
CALLBACK_DATA_MOVE_RESULTS_TABLE = chr(6)
CALLBACK_DATA_REFRESH_RESULTS_TABLE = chr(7)

# get_student_task_list_inline_markup
CALLBACK_DATA_SELECT_EXERCISE_FOR_SEND_ANSWER = chr(8)
CALLBACK_DATA_SHOW_TASK_STATEMENT = chr(9)

# get_exercise_actions_inline_markup
CALLBACK_DATA_SHOW_RESULTS_TABLE = chr(10)
CALLBACK_DATA_SHOW_EXERCISE_DESCRIPTION = chr(11)

# get_admin_account_actions_inline_markup
# get_student_account_actions_inline_markup
CALLBACK_DATA_ACCOUNT_ACTION_SHOW_PASSWORD = chr(12)
CALLBACK_DATA_ACCOUNT_ACTION_SHOW_USER = chr(13)
CALLBACK_DATA_STUDENT_ACCOUNT_ACTION_SHOW_RESULTS = chr(14)

# get_solved_task_description_actions_inline_markup
CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SHOW_EXPLANATION = chr(15)
CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SWITCH_STUDENT_ANSWER = chr(16)


def get_results_table_inline_markup(results, homework_name: str, homework_size: int,
                                    first_task_id: int) -> types.InlineKeyboardMarkup:
    # This function returns table of buttons for table of results

    # Number of tasks that will add in table
    number_tasks = min(homework_size - first_task_id + 1, constants.TASKS_ON_ONE_PAGE)

    # Final keyboard storage
    keyboard = []

    # Temporary storage for current row
    row = [types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_COLUMN_OF_USER_NUMBERS, callback_data=CALLBACK_DATA_NONE),
           types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_COLUMN_OF_USER_LOGINS, callback_data=CALLBACK_DATA_NONE)]

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
            if answer is not None and answer:
                current_sum += 1
                sum_in_column[task_id - 1] += 1

            # If current task is visible (his id in [first_task_id, first_task_id + number_tasks)) add button for him
            if first_task_id <= task_id < first_task_id + number_tasks:
                if answer is None:
                    # There is no answer from user on this task
                    row.append(types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_CELL_OF_NOT_SOLVED_TASK,
                                                          callback_data=CALLBACK_DATA_FROM_CELL_OF_TASK +
                                                                        result[0].login + CALLBACK_SEPARATION_ELEMENT +
                                                                        homework_name + CALLBACK_SEPARATION_ELEMENT + str(task_id)))
                elif answer:
                    # User answer is right
                    row.append(types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_CELL_OF_RIGHT_SOLVED_TASK,
                                                          callback_data=CALLBACK_DATA_FROM_CELL_OF_TASK +
                                                                        result[0].login + CALLBACK_SEPARATION_ELEMENT +
                                                                        homework_name + CALLBACK_SEPARATION_ELEMENT + str(task_id)))
                else:
                    # User answer is false
                    row.append(types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_CELL_OF_WRONG_SOLVED_TASK,
                                                          callback_data=CALLBACK_DATA_FROM_CELL_OF_TASK +
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
    row = [types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_ROW_OF_NUMBER_OF_SOLVED_TASKS,
                                      callback_data=CALLBACK_DATA_NONE),
           types.InlineKeyboardButton(text=str(amount), callback_data=CALLBACK_DATA_NONE)]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(sum_in_column[i + first_task_id - 1]),
                                              callback_data=CALLBACK_DATA_NONE))
    keyboard.append(row)

    # Create buttons that can move table left
    left1 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_LEFT_ONE_STEP_NO_ACTION,
                                       callback_data=CALLBACK_DATA_NONE)
    left2 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_LEFT_MANY_STEPS_NO_ACTION,
                                       callback_data=CALLBACK_DATA_NONE)
    if first_task_id > 1:
        # Go left on 1
        left1 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_LEFT_ONE_STEP_CAN_MOVE,
                                           callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                         CALLBACK_SEPARATION_ELEMENT + str(first_task_id - 1))

        # Go left on TASKS_ON_ONE_PAGE
        left2 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_LEFT_MANY_STEPS_CAN_MOVE,
                                           callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                         CALLBACK_SEPARATION_ELEMENT +
                                                         str(max(first_task_id - constants.TASKS_ON_ONE_PAGE, 1)))

    # Create buttons that can move table right
    right1 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_RIGHT_ONE_STEP_NO_ACTION,
                                        callback_data=CALLBACK_DATA_NONE)
    right2 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_RIGHT_MANY_STEPS_NO_ACTION,
                                        callback_data=CALLBACK_DATA_NONE)
    if first_task_id + number_tasks - 1 < homework_size:
        # Go right on 1
        right1 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_RIGHT_ONE_STEP_CAN_MOVE,
                                            callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                          CALLBACK_SEPARATION_ELEMENT + str(first_task_id + 1))

        # Go right on TASKS_ON_ONE_PAGE
        right2 = types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_MOVE_TABLE_RIGHT_MANY_STEPS_CAN_MOVE,
                                            callback_data=CALLBACK_DATA_MOVE_RESULTS_TABLE + homework_name +
                                                          CALLBACK_SEPARATION_ELEMENT +
                                                          str(min(first_task_id + constants.TASKS_ON_ONE_PAGE, homework_size - constants.TASKS_ON_ONE_PAGE + 1)))

    # Add last row with 'refresh' button
    keyboard.append([left2, left1,
                     types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_REFRESH_RESULTS_TABLE,
                                                callback_data=CALLBACK_DATA_REFRESH_RESULTS_TABLE + homework_name +
                                                              CALLBACK_SEPARATION_ELEMENT + str(first_task_id)),
                     right1, right2])

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_user_results_table_inline_markup(homework_list: list[str], user_results):
    # This function returns table of buttons for table of one user results

    homework_list.sort()

    keyboard = [[types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_COLUMN_OF_EXERCISE_NAMES,
                                            callback_data=CALLBACK_DATA_NONE),
                 types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_COLUMN_OF_NUMBER_RIGHT_SOLVED_TASKS,
                                            callback_data=CALLBACK_DATA_NONE),
                 types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_OF_COLUMN_OF_NUMBER_OF_TASKS,
                                            callback_data=CALLBACK_DATA_NONE)]]  # Final keyboard storage
    for row_id in range(len(homework_list)):
        # Add buttons on current row
        keyboard.append([types.InlineKeyboardButton(text=homework_list[row_id],
                                                    callback_data=CALLBACK_DATA_SHOW_RESULTS_TABLE +
                                                                  homework_list[row_id]),
                         types.InlineKeyboardButton(text=str(user_results[row_id][0]),
                                                    callback_data=CALLBACK_DATA_NONE),
                         types.InlineKeyboardButton(text=str(user_results[row_id][1]),
                                                    callback_data=CALLBACK_DATA_NONE)])

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_student_task_list_inline_markup(login: str, homework: Homework, check_task):
    # This function returns table of buttons for tasks list

    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for task_id in range(1, len(homework.tasks) + 1):
        # None - there is no user answer, True - user answer is right, False otherwise
        task_state = check_task(login, homework.name, task_id)

        # Add button depend on task state
        if task_state is None:
            row.append(types.InlineKeyboardButton(text=str(task_id),
                                                  callback_data=CALLBACK_DATA_SELECT_EXERCISE_FOR_SEND_ANSWER +
                                                                homework.name +
                                                                CALLBACK_SEPARATION_ELEMENT + str(task_id)))
        elif task_state:
            row.append(types.InlineKeyboardButton(text=str(task_id) + " " + messages_text.BUTTON_NAME_OF_CELL_OF_RIGHT_SOLVED_TASK,
                                                  callback_data=CALLBACK_DATA_FROM_CELL_OF_TASK + login +
                                                                CALLBACK_SEPARATION_ELEMENT + homework.name +
                                                                CALLBACK_SEPARATION_ELEMENT + str(task_id)))
        else:
            row.append(types.InlineKeyboardButton(text=str(task_id) + " " + messages_text.BUTTON_NAME_OF_CELL_OF_WRONG_SOLVED_TASK,
                                                  callback_data=CALLBACK_DATA_FROM_CELL_OF_TASK + login +
                                                                CALLBACK_SEPARATION_ELEMENT + homework.name +
                                                                CALLBACK_SEPARATION_ELEMENT + str(task_id)))

        if homework.tasks[task_id - 1].text_statement != "" or homework.tasks[task_id - 1].file_statement[0] != bytes():
            row.append(
                types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_SHOW_TASK_STATEMENT,
                                           callback_data=CALLBACK_DATA_SHOW_TASK_STATEMENT + homework.name +
                                                         CALLBACK_SEPARATION_ELEMENT + str(task_id)))
        else:
            row.append(types.InlineKeyboardButton(text=" ", callback_data=CALLBACK_DATA_NONE))

        keyboard.append(row)
        row = []

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)


def get_list_of_all_homeworks_inline_markup(homework_list: list[Homework],
                                            callback_data: str) -> Optional[types.InlineKeyboardMarkup]:
    # This function returns table of buttons for list of homeworks

    homework_list.sort(key=lambda cur_homework: cur_homework.name)

    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for homework in homework_list:
        # Add button with name of current homework to table
        row.append(types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_CELL_WITH_EXERCISE_NAME.format(
            exercise_name=homework.name,
            grade=homework.grade),
                                              callback_data=callback_data + homework.name))

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
    # This function returns list of all grades inline markup

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


def get_exercise_actions_inline_markup(exercise_name: str) -> types.InlineKeyboardMarkup:
    # This function returns list of exercise actions inline markup

    keyboard = [[types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_EXERCISE_ACTION_SHOW_RESULTS,
                                            callback_data=CALLBACK_DATA_SHOW_RESULTS_TABLE + exercise_name),
                 types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_EXERCISE_ACTION_SHOW_DESCRIPTION,
                                            callback_data=CALLBACK_DATA_SHOW_EXERCISE_DESCRIPTION + exercise_name)]]
    return types.InlineKeyboardMarkup(keyboard)


def get_admin_account_actions_inline_markup(login: str) -> types.InlineKeyboardMarkup:
    # This function returns list of admin account actions inline markup

    keyboard = [[types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_ACCOUNT_ACTION_SHOW_PASSWORD,
                                            callback_data=CALLBACK_DATA_ACCOUNT_ACTION_SHOW_PASSWORD + login),
                 types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_ACCOUNT_ACTION_SHOW_USER,
                                            callback_data=CALLBACK_DATA_ACCOUNT_ACTION_SHOW_USER + login)]]
    return types.InlineKeyboardMarkup(keyboard)


def get_student_account_actions_inline_markup(login: str) -> types.InlineKeyboardMarkup:
    # This function returns list of account actions inline markup

    keyboard = [[types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_ACCOUNT_ACTION_SHOW_PASSWORD,
                                            callback_data=CALLBACK_DATA_ACCOUNT_ACTION_SHOW_PASSWORD + login),
                 types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_ACCOUNT_ACTION_SHOW_USER,
                                            callback_data=CALLBACK_DATA_ACCOUNT_ACTION_SHOW_USER + login),
                 types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_STUDENT_ACCOUNT_ACTION_SHOW_RESULTS,
                                            callback_data=CALLBACK_DATA_STUDENT_ACCOUNT_ACTION_SHOW_RESULTS + login)]]
    return types.InlineKeyboardMarkup(keyboard)


def get_solved_task_description_actions_inline_markup(login: str, homework: Homework, task_id: int,
                                                      user_answer: Optional[Result], correct_answers: list[str],
                                                      is_admin: str) -> types.InlineKeyboardMarkup:
    # This function returns list of solved task description actions inline markup

    row = []
    if homework.tasks[task_id - 1].text_statement != "" or homework.tasks[task_id - 1].file_statement[0] != bytes():
        row.append(
            types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_SHOW_TASK_STATEMENT,
                                       callback_data=CALLBACK_DATA_SHOW_TASK_STATEMENT + homework.name +
                                                     CALLBACK_SEPARATION_ELEMENT + str(task_id)))

    if user_answer is not None and (user_answer.text_clarification != "" or user_answer.file_answer[0] != bytes()):
        row.append(types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_SOLVED_TASK_DESCRIPTION_ACTION_SHOW_EXPLANATION,
                                              callback_data=CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SHOW_EXPLANATION + login +
                                                            CALLBACK_SEPARATION_ELEMENT + homework.name +
                                                            CALLBACK_SEPARATION_ELEMENT + str(task_id)))
    if is_admin:
        if user_answer is None or user_answer.text_answer not in correct_answers:
            row.append(types.InlineKeyboardButton(
                text=messages_text.BUTTON_NAME_SOLVED_TASK_DESCRIPTION_ACTION_ACCEPT_ANSWER,
                callback_data=CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SWITCH_STUDENT_ANSWER + login +
                              CALLBACK_SEPARATION_ELEMENT + homework.name +
                              CALLBACK_SEPARATION_ELEMENT + str(task_id)))
        else:
            row.append(types.InlineKeyboardButton(
                text=messages_text.BUTTON_NAME_SOLVED_TASK_DESCRIPTION_ACTION_REJECT_ANSWER,
                callback_data=CALLBACK_DATA_SOLVED_TASK_DESCRIPTION_ACTION_SWITCH_STUDENT_ANSWER + login +
                              CALLBACK_SEPARATION_ELEMENT + homework.name +
                              CALLBACK_SEPARATION_ELEMENT + str(task_id)))

    if len(row) == 0:
        return types.InlineKeyboardMarkup()
    return types.InlineKeyboardMarkup([row])


def get_exercise_description_in_list_of_exercises_inline_markup(homework: Homework):
    # This function returns description table of exercise (in list of exercises)

    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for task_id in range(1, len(homework.tasks) + 1):
        row.append(types.InlineKeyboardButton(text=str(task_id), callback_data=CALLBACK_DATA_NONE))

        if homework.tasks[task_id - 1].text_statement != "" or homework.tasks[task_id - 1].file_statement[0] != bytes():
            row.append(
                types.InlineKeyboardButton(text=messages_text.BUTTON_NAME_SHOW_TASK_STATEMENT,
                                           callback_data=CALLBACK_DATA_SHOW_TASK_STATEMENT + homework.name +
                                                         CALLBACK_SEPARATION_ELEMENT + str(task_id)))
        else:
            row.append(types.InlineKeyboardButton(text=" ", callback_data=CALLBACK_DATA_NONE))

        keyboard.append(row)
        row = []

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)
