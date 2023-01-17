from telebot import types
import constants


def get_all_homeworks(homework_list: list[str], callback_data: str):
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


def get_results_table(results, homework_name, homework_size, first_task_id):
    number_tasks = min(homework_size - first_task_id + 1, constants.TASKS_ON_ONE_PAGE)

    keyboard = []
    row = [types.InlineKeyboardButton(text="№", callback_data="0"), types.InlineKeyboardButton(text="Логин", callback_data="0")]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(i + first_task_id), callback_data="0"))
    keyboard.append(row)

    amount = 0
    row_id = 0
    rows = []
    rows_order = []
    sum_in_column = [0] * homework_size
    for result in results:
        row = [types.InlineKeyboardButton(text=result[0].login, callback_data="J" + result[0].login + "$" + homework_name)]
        task_id = 0
        current_sum = 0
        for answer in result[1]:
            task_id += 1
            if answer[0] == answer[1]:
                current_sum += 1
                sum_in_column[task_id - 1] += 1

            if first_task_id <= task_id < first_task_id + number_tasks:
                if answer[0] is None or answer[0] == '':
                    row.append(types.InlineKeyboardButton(text=" ", callback_data="0"))
                elif answer[0] == answer[1]:
                    row.append(types.InlineKeyboardButton(text="✅", callback_data="E" + result[0].login + "$" + homework_name + "$" + str(task_id)))
                else:
                    row.append(types.InlineKeyboardButton(text="❌", callback_data="E" + result[0].login + "$" + homework_name + "$" + str(task_id)))

        rows_order.append((-current_sum, result[0].login, row_id))
        amount += current_sum
        row_id += 1

        rows.append(row)
    rows_order.sort()

    row_id = 0
    for element in rows_order:
        row_id += 1
        keyboard.append([types.InlineKeyboardButton(text=str(row_id), callback_data="0")] + rows[element[2]])

    row = [types.InlineKeyboardButton(text="Σ", callback_data="0"), types.InlineKeyboardButton(text=str(amount), callback_data="0")]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(sum_in_column[i + first_task_id - 1]), callback_data="0"))
    keyboard.append(row)

    left1 = types.InlineKeyboardButton(text=" ", callback_data="0")
    left2 = types.InlineKeyboardButton(text=" ", callback_data="0")
    if first_task_id > 1:
        left1 = types.InlineKeyboardButton(text="<", callback_data="I" + homework_name + "$" + str(first_task_id - 1))
        left2 = types.InlineKeyboardButton(text="<<", callback_data="I" + homework_name + "$" + str(max(first_task_id - constants.TASKS_ON_ONE_PAGE, 1)))

    right1 = types.InlineKeyboardButton(text=" ", callback_data="0")
    right2 = types.InlineKeyboardButton(text=" ", callback_data="0")
    if first_task_id + number_tasks - 1 < homework_size:
        right1 = types.InlineKeyboardButton(text=">", callback_data="I" + homework_name + "$" + str(first_task_id + 1))
        right2 = types.InlineKeyboardButton(text=">>", callback_data="I" + homework_name + "$" + str(min(first_task_id + constants.TASKS_ON_ONE_PAGE, homework_size - constants.TASKS_ON_ONE_PAGE + 1)))

    keyboard.append([left2, left1, types.InlineKeyboardButton(text="Обновить", callback_data="G" + homework_name + "$" + str(first_task_id)), right1, right2])

    return types.InlineKeyboardMarkup(keyboard)


def get_task_list(login: str, homework_size: int, homework_name: str, check_task):
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
