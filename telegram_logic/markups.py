from telebot import types
import constants


def get_all_homeworks(homework_list, callback_data):
    keyboard = []
    row = []
    for name in homework_list:
        row.append(types.InlineKeyboardButton(text=name, callback_data=callback_data + "$" + name))
        if len(row) == constants.HOMEWORKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

    if len(row) > 0:
        keyboard.append(row)

    if len(keyboard) == 0:
        return None
    return types.InlineKeyboardMarkup(keyboard)


def get_results_table(results, homework_name, homework_size, first_task_id):
    number_tasks = min(homework_size - first_task_id + 1, constants.TASKS_ON_ONE_PAGE)

    keyboard = []
    row = [types.InlineKeyboardButton(text=" ", callback_data="NONE"), types.InlineKeyboardButton(text="Σ", callback_data="NONE")]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(i + first_task_id), callback_data="NONE"))
    keyboard.append(row)

    amount = 0
    row_id = 0
    rows = []
    rows_order = []
    sum_in_column = [0] * homework_size
    for result in results:
        row = [types.InlineKeyboardButton(text=result[0].login, callback_data="NONE")]
        task_id = 0
        current_sum = 0
        for answer in result[1]:
            task_id += 1
            if answer[0] == answer[1]:
                current_sum += 1
                sum_in_column[task_id - 1] += 1

            if first_task_id <= task_id < first_task_id + number_tasks:
                if answer[0] is None or answer[0] == '':
                    row.append(types.InlineKeyboardButton(text=" ", callback_data="NONE"))
                elif answer[0] == answer[1]:
                    row.append(types.InlineKeyboardButton(text="✅", callback_data="SHOW_TASK_IN_TABLE$" + result[0].login + "$" + homework_name + "$" + str(task_id)))
                else:
                    row.append(types.InlineKeyboardButton(text="❌", callback_data="SHOW_TASK_IN_TABLE$" + result[0].login + "$" + homework_name + "$" + str(task_id)))

        row = row[:1] + [types.InlineKeyboardButton(text=str(current_sum), callback_data="NONE")] + row[1:]
        rows_order.append((-current_sum, result[0].login, row_id))
        amount += current_sum
        row_id += 1

        rows.append(row)
    rows_order.sort()

    for element in rows_order:
        keyboard.append(rows[element[2]])

    row = [types.InlineKeyboardButton(text="Σ", callback_data="NONE"), types.InlineKeyboardButton(text=str(amount), callback_data="NONE")]
    for i in range(number_tasks):
        row.append(types.InlineKeyboardButton(text=str(sum_in_column[i + first_task_id - 1]), callback_data="NONE"))
    keyboard.append(row)

    left1 = types.InlineKeyboardButton(text=" ", callback_data="NONE")
    left2 = types.InlineKeyboardButton(text=" ", callback_data="NONE")
    if first_task_id > 1:
        left1 = types.InlineKeyboardButton(text="<", callback_data="CHANGE_RESULTS_TABLE$" + homework_name + "$" + str(first_task_id - 1))
        left2 = types.InlineKeyboardButton(text="<<", callback_data="CHANGE_RESULTS_TABLE$" + homework_name + "$" + str(max(first_task_id - constants.TASKS_ON_ONE_PAGE, 1)))

    right1 = types.InlineKeyboardButton(text=" ", callback_data="NONE")
    right2 = types.InlineKeyboardButton(text=" ", callback_data="NONE")
    if first_task_id + number_tasks - 1 < homework_size:
        right1 = types.InlineKeyboardButton(text=">", callback_data="CHANGE_RESULTS_TABLE$" + homework_name + "$" + str(first_task_id + 1))
        right2 = types.InlineKeyboardButton(text=">>", callback_data="CHANGE_RESULTS_TABLE$" + homework_name + "$" + str(min(first_task_id + constants.TASKS_ON_ONE_PAGE, homework_size - constants.TASKS_ON_ONE_PAGE + 1)))

    keyboard.append([left2, left1, types.InlineKeyboardButton(text="Обновить", callback_data="REFRESH_RESULTS_TABLE$" + homework_name + "$" + str(first_task_id)), right1, right2])

    return types.InlineKeyboardMarkup(keyboard)


def get_task_list(login, homework_size, homework_name, check_task):
    keyboard = []
    row = []
    for task_id in range(1, homework_size + 1):
        task_state = check_task(login, homework_name, task_id)

        if task_state is None:
            row.append(types.InlineKeyboardButton(text=str(task_id), callback_data="SELECT_TASK$" + homework_name + "$" + str(task_id)))
        elif task_state:
            row.append(types.InlineKeyboardButton(text=str(task_id) + " ✅", callback_data="SHOW_TASK$" + homework_name + "$" + str(task_id)))
        else:
            row.append(types.InlineKeyboardButton(text=str(task_id) + " ❌", callback_data="SHOW_TASK$" + homework_name + "$" + str(task_id)))

        if len(row) == constants.TASKS_NUMBER_IN_LINE:
            keyboard.append(row)
            row = []

    if len(row) > 0:
        keyboard.append(row)

    return types.InlineKeyboardMarkup(keyboard)
