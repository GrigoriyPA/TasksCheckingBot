from telebot import types
from bot import constants


def get_all_homeworks(homework_list: list[str], callback_data: str):
    # This function returns table of buttons for list of homeworks

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


def get_results_table(results, homework_name: str, homework_size: int, first_task_id: int):
    # This function returns table of buttons for table of results

    number_tasks = min(homework_size - first_task_id + 1, constants.TASKS_ON_ONE_PAGE)  # Number of tasks that will add in table

    keyboard = []  # Final keyboard storage
    row = [types.InlineKeyboardButton(text="№", callback_data="0"), types.InlineKeyboardButton(text="Логин", callback_data="0")]  # Temporary storage for current row

    # Creating first line of the table (Number Login 1 2 ... number_tasks)
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(i + first_task_id), callback_data="0"))
    keyboard.append(row)

    amount = 0  # Number of right solved tasks
    row_id = 0  # Current row id
    rows = []  # Temporary storage for table (in final table rows can be in different order)
    rows_order = []  # Array of (number of solved tasks by user, user login, row id)
    sum_in_column = [0] * homework_size  # Number of right solved tasks in each column
    for result in results:
        # Add login button in current row
        row = [types.InlineKeyboardButton(text=result[0].login, callback_data="J" + result[0].login + "$" + homework_name)]

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
                    row.append(types.InlineKeyboardButton(text=" ", callback_data="0"))
                elif answer[0] == answer[1]:
                    # User answer is right
                    row.append(types.InlineKeyboardButton(text="✅", callback_data="E" + result[0].login + "$" + homework_name + "$" + str(task_id)))
                else:
                    # User answer is false
                    row.append(types.InlineKeyboardButton(text="❌", callback_data="E" + result[0].login + "$" + homework_name + "$" + str(task_id)))

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
        keyboard.append([types.InlineKeyboardButton(text=str(row_id), callback_data="0")] + rows[element[2]])

    # Add row there placed sums of number of right answers
    row = [types.InlineKeyboardButton(text="Σ", callback_data="0"), types.InlineKeyboardButton(text=str(amount), callback_data="0")]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(sum_in_column[i + first_task_id - 1]), callback_data="0"))
    keyboard.append(row)

    # Create buttons that can move table left
    left1 = types.InlineKeyboardButton(text=" ", callback_data="0")
    left2 = types.InlineKeyboardButton(text=" ", callback_data="0")
    if first_task_id > 1:
        left1 = types.InlineKeyboardButton(text="<", callback_data="I" + homework_name + "$" + str(first_task_id - 1))  # Go left on 1
        left2 = types.InlineKeyboardButton(text="<<", callback_data="I" + homework_name + "$" + str(max(first_task_id - constants.TASKS_ON_ONE_PAGE, 1)))  # Go left on TASKS_ON_ONE_PAGE

    # Create buttons that can move table right
    right1 = types.InlineKeyboardButton(text=" ", callback_data="0")
    right2 = types.InlineKeyboardButton(text=" ", callback_data="0")
    if first_task_id + number_tasks - 1 < homework_size:
        right1 = types.InlineKeyboardButton(text=">", callback_data="I" + homework_name + "$" + str(first_task_id + 1))  # Go right on 1
        right2 = types.InlineKeyboardButton(text=">>", callback_data="I" + homework_name + "$" + str(min(first_task_id + constants.TASKS_ON_ONE_PAGE, homework_size - constants.TASKS_ON_ONE_PAGE + 1)))  # Go right on TASKS_ON_ONE_PAGE

    # Add last row with 'refresh' button
    keyboard.append([left2, left1, types.InlineKeyboardButton(text="Обновить", callback_data="G" + homework_name + "$" + str(first_task_id)), right1, right2])

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


def get_list_of_grades(login: str, callback_data: str):
    keyboard = []  # Final keyboard storage
    row = []  # Temporary storage for current row
    for grade_id in range(1, 12):
        # Add for current grade
        row.append(types.InlineKeyboardButton(text=str(grade_id), callback_data=callback_data + login + "$" + str(grade_id)))

        # End current row on length GRADES_IN_LINE
        if len(row) == constants.TASKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

    # Add last row to table
    if len(row) > 0:
        keyboard.append(row)

    # Returns created keyboard
    return types.InlineKeyboardMarkup(keyboard)
