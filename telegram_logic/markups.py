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


def get_results_table(results, homework_name, homework_size):
    keyboard = []
    row = [types.InlineKeyboardButton(text=" ", callback_data="NONE"), types.InlineKeyboardButton(text="Σ", callback_data="NONE")]
    for i in range(1, homework_size + 1):
        row.append(types.InlineKeyboardButton(text=str(i), callback_data="NONE"))
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
            if answer[0] is None or answer[0] == '':
                row.append(types.InlineKeyboardButton(text=" ", callback_data="NONE"))
            elif answer[0] == answer[1]:
                current_sum += 1
                sum_in_column[task_id - 1] += 1
                row.append(types.InlineKeyboardButton(text="✅", callback_data="SHOW_TASK_FOR_ADMIN$" + result[0].login + "$" + homework_name + "$" + str(task_id)))
            else:
                row.append(types.InlineKeyboardButton(text="❌", callback_data="SHOW_TASK_FOR_ADMIN$" + result[0].login + "$" + homework_name + "$" + str(task_id)))

        row = row[:1] + [types.InlineKeyboardButton(text=str(current_sum), callback_data="NONE")] + row[1:]
        rows_order.append((-current_sum, result[0].login, row_id))
        amount += current_sum
        row_id += 1

        rows.append(row)
    rows_order.sort()

    for element in rows_order:
        keyboard.append(rows[element[2]])

    row = [types.InlineKeyboardButton(text="Σ", callback_data="NONE"), types.InlineKeyboardButton(text=str(amount), callback_data="NONE")]
    for i in range(homework_size):
        row.append(types.InlineKeyboardButton(text=str(sum_in_column[i]), callback_data="NONE"))
    keyboard.append(row)

    keyboard.append([types.InlineKeyboardButton(text="Обновить", callback_data="REFRESH_RESULTS_TABLE$" + homework_name)])

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
