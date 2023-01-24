# ----------------------------------------------------------------------------------------------------------------------
# Inline markups text
# ----------------------------------------------------------------------------------------------------------------------


# common
BUTTON_NAME_OF_CELL_OF_RIGHT_SOLVED_TASK = "✅"
BUTTON_NAME_OF_CELL_OF_WRONG_SOLVED_TASK = "❌"

# get_results_table_inline_markup
BUTTON_NAME_OF_COLUMN_OF_USER_NUMBERS = "№"
BUTTON_NAME_OF_COLUMN_OF_USER_LOGINS = "Логин"
BUTTON_NAME_OF_CELL_OF_NOT_SOLVED_TASK = " "
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

# get_user_results_table_inline_markup
BUTTON_NAME_OF_COLUMN_OF_EXERCISE_NAMES = "Работа"
BUTTON_NAME_OF_COLUMN_OF_NUMBER_RIGHT_SOLVED_TASKS = "Решено"
BUTTON_NAME_OF_COLUMN_OF_NUMBER_OF_TASKS = "Всего"

# get_exercise_actions_inline_markup
BUTTON_NAME_EXERCISE_ACTION_SHOW_RESULTS = "Результаты"
BUTTON_NAME_EXERCISE_ACTION_SHOW_DESCRIPTION = "Описание"

# get_admin_account_actions_inline_markup
# get_student_account_actions_inline_markup
BUTTON_NAME_ACCOUNT_ACTION_SHOW_PASSWORD = "Пароль"
BUTTON_NAME_ACCOUNT_ACTION_SHOW_USER = "Пользователь"
BUTTON_NAME_STUDENT_ACCOUNT_ACTION_SHOW_RESULTS = "Результаты"


# ----------------------------------------------------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------------------------------------------------


MESSAGE_ON_START_COMMAND = "Состояние сессии сброшено..."


# ----------------------------------------------------------------------------------------------------------------------
# Callbacks text
# ----------------------------------------------------------------------------------------------------------------------


# common
MESSAGE_ON_UNAUTHORIZED_USER = "Вы не авторизованы."
MESSAGE_ON_NOT_STUDENT_USER = "Выбор задания невозможен."
MESSAGE_ON_NOT_ADMIN_USER = "Вы не обладаете достаточными правами."
MESSAGE_ON_UNKNOWN_LOGIN = "Выбранный пользователь был удалён."
MESSAGE_ON_UNKNOWN_EXERCISE_NAME = "Выбранная работа недоступна."
MESSAGE_ON_INVALID_TASK = "Выбранное задание недоступно."

# compute_show_results_table_callback
MESSAGE_ON_SUCCESS_CREATION_TABLE = "Текущие результаты по работе '{exercise_name}', {grade} класс:"

# compute_show_login_in_results_table_callback
MESSAGE_ON_SHOW_LOGIN_IN_RESULTS_TABLE = "{login}\nРешено {solved_tasks_number} / {tasks_number} задач."

# compute_cell_of_solved_task_in_table_callback
MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_ADMIN = "Правильный ответ '{login}' на задание {task_id}: {answer}"
MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_ADMIN = "Правильный ответ на задание {task_id}: {correct_answer}\n" \
                                                          "Ответ '{login}' на задание: {answer}"
MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Ваш правильный ответ на задание {task_id}: {answer}"
MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Правильный ответ на задание {task_id}: {correct_answer}\n" \
                                                            "Ваш ответ на задание:  {answer}"

# compute_refresh_results_table_callback
MESSAGE_ON_ALREADY_ACTUAL_INFORMATION_IN_RESULTS_TABLE = "Информация актуальна."

# compute_select_homework_for_send_answer_callback
TOP_MESSAGE_OF_STUDENT_TASK_LIST = "Выберите задание."

# compute_select_task_id_for_send_answer_callback
MESSAGE_ON_START_WAITING_ANSWER_ON_TASK = "Введите ответ на задание {task_id}:"

# compute_select_student_grade_for_create_callback
MESSAGE_ON_START_WAITING_LOGIN_OF_NEW_STUDENT_ACCOUNT = "Введите логин для нового аккаунта " \
                                                        "(доступны латинские символы, цифры и знаки препинания):"

# compute_select_exercise_grade_for_create_callback
MESSAGE_ON_START_WAITING_EXERCISE_NAME_FOR_CREATE = "Введите название новой работы " \
                                                    "(доступны латинские символы, цифры и знаки препинания):"

# compute_show_exercise_description_callback
FIRST_MESSAGE_IN_EXERCISE_DESCRIPTION = "Класс работы: {grade}\nВсего задач: {number_tasks}\nПравильные ответы:\n"

# compute_account_action_show_password_callback
MESSAGE_WITH_PASSWORD_DESCRIPTION = "Пароль пользователя '{login}': {password}"

# compute_account_action_show_user_callback
MESSAGE_ON_UNAUTHORIZED_USER_LOGIN = "В этот аккаунт никто не вошёл."
MESSAGE_WITH_USER_TELEGRAM_INFO = "Имя: {first_name}\nФамилия: {last_name}\nХэндл: @{username}"

# compute_student_account_action_show_results_callback
TOP_MESSAGE_OF_USER_RESULTS_TABLE = "Результаты '{login}':"


# ----------------------------------------------------------------------------------------------------------------------
# Messages text
# ----------------------------------------------------------------------------------------------------------------------
