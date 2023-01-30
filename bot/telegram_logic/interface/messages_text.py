# ----------------------------------------------------------------------------------------------------------------------
# Inline markups names
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

# get_student_task_list_inline_markup
BUTTON_NAME_SHOW_TASK_STATEMENT = "Условие"
BUTTON_NAME_SHOW_RIGHT_ANSWERS_ON_TASK = "Ответы"

# get_list_of_all_homeworks_inline_markup
BUTTON_NAME_CELL_WITH_EXERCISE_NAME = "{exercise_name}, {grade} класс"
BUTTON_NAME_CELL_WITH_QUEST_NAME = "{exercise_name}, {grade} класс"

# get_exercise_actions_inline_markup
BUTTON_NAME_EXERCISE_ACTION_SHOW_RESULTS = "Результаты"
BUTTON_NAME_EXERCISE_ACTION_SHOW_DESCRIPTION = "Описание"

# get_admin_account_actions_inline_markup
# get_student_account_actions_inline_markup
BUTTON_NAME_ACCOUNT_ACTION_SHOW_PASSWORD = "Пароль"
BUTTON_NAME_ACCOUNT_ACTION_SHOW_MANA = "Мана"
BUTTON_NAME_ACCOUNT_ACTION_SHOW_USER = "Пользователь"
BUTTON_NAME_STUDENT_ACCOUNT_ACTION_SHOW_RESULTS = "Результаты"

# get_solved_task_description_actions_inline_markup
BUTTON_NAME_SOLVED_TASK_DESCRIPTION_ACTION_SHOW_EXPLANATION = "Пояснение"
BUTTON_NAME_SOLVED_TASK_DESCRIPTION_ACTION_ACCEPT_ANSWER = "Засчитать"
BUTTON_NAME_SOLVED_TASK_DESCRIPTION_ACTION_REJECT_ANSWER = "Отклонить"

# get_user_mana_description_inline_markup
BUTTON_NAME_CHANGE_STUDENT_MANA = "Изменить"


# ----------------------------------------------------------------------------------------------------------------------
# Keyboard markups names
# ----------------------------------------------------------------------------------------------------------------------


# Common:
BUTTON_SHOW_RESULTS_TABLE = "Вывести результаты"  # Show results table
BUTTON_SHOW_STATUS = "Статус"  # Get login, password and status of current account
BUTTON_EXIT = "Выйти"  # Exit from current account
BUTTON_BACK = "Назад"  # Go to last state

# Students
BUTTON_SOLVE_EXERCISE = "Сдать задачу"  # Solve unsolved exercise

# get_student_send_explanation_keyboard
BUTTON_STUDENT_WANT_TO_SEND_EXPLANATION = "Да"
BUTTON_STUDENT_DO_NOT_WANT_TO_SEND_EXPLANATION = "Нет"

# Admins:
BUTTON_ADD = "Добавить"  # Button for select add action type (admin/super-admin)
BUTTON_DELETE = "Удалить"  # Button for select delete action type (admin/super-admin)
BUTTON_ACCOUNTS_LIST = "Список аккаунтов"  # Show accounts list (admin/super-admin)
BUTTON_EXERCISES_LIST = "Список заданий"  # Show exercises list (admin/super-admin)
BUTTON_ADD_STUDENT = "Ученик"  # Add new student account
BUTTON_ADD_ADMIN = "Администратор"  # Add new admin account
BUTTON_ADD_EXERCISE = "Задание"  # Add new exercise
BUTTON_ADD_QUEST = "Квест"  # Add new quest
BUTTON_DELETE_ACCOUNT = "Аккаунт"  # Delete exists account
BUTTON_DELETE_EXERCISE = "Задание"  # Delete exists exercise

# get_adding_exercise_interface_keyboard
BUTTON_ADD_ANSWER_ON_TASK = "Добавить ответ"
BUTTON_ADD_STATEMENT_FOR_TASK = "Добавить условие"
BUTTON_PREVIOUS_TASK_IN_ADDING_TASK_INTERFACE = "Предыдущее задание"
BUTTON_NEXT_TASK_IN_ADDING_TASK_INTERFACE = "Следующее задание"
BUTTON_FINISH_CREATING_EXERCISE = "Завершить создание."


# ----------------------------------------------------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------------------------------------------------


MESSAGE_ON_START_COMMAND = "Состояние сессии сброшено..."


# ----------------------------------------------------------------------------------------------------------------------
# Callbacks text
# ----------------------------------------------------------------------------------------------------------------------


# common
MESSAGE_ON_UNAUTHORIZED_USER = "Вы не авторизованы.\nВведите логин для авторизации:"
MESSAGE_ON_NOT_STUDENT_USER = "Эта команда не может быть вызвана админом."
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
MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_ADMIN = "Ответ '{login}' на задание {task_id}: {answer}\n" \
                                                          "Список правильных ответов на задание:\n{correct_answer}"
MESSAGE_ON_CELL_OF_NOT_SOLVED_TASK_IN_TABLE_FOR_ADMIN = "Ученик '{login}' не дал ответа на задание {task_id}.\n" \
                                                        "Список правильных ответов на задание:\n{correct_answer}"
MESSAGE_ON_CELL_OF_RIGHT_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Ваш правильный ответ на задание {task_id}: {answer}"
MESSAGE_ON_CELL_OF_WRONG_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Ваш ответ на задание {task_id}: {answer}\n" \
                                                            "Список правильных ответов на задание:\n{correct_answer}"
MESSAGE_ON_CELL_OF_NOT_SOLVED_TASK_IN_TABLE_FOR_STUDENT = "Вы не дали ответа на задание {task_id}."

# compute_refresh_results_table_callback
MESSAGE_ON_ALREADY_ACTUAL_INFORMATION_IN_RESULTS_TABLE = "Информация актуальна."

# compute_select_homework_for_send_answer_callback
TOP_MESSAGE_OF_STUDENT_TASK_LIST = "Выберите задание."

# compute_select_task_id_for_send_answer_callback
MESSAGE_ON_START_WAITING_ANSWER_ON_TASK = "Введите ответ на задание {task_id}:"

# compute_select_student_grade_for_create_callback
MESSAGE_ON_START_WAITING_LOGIN_OF_NEW_STUDENT_ACCOUNT = "Введите логин для нового аккаунта " \
                                                        "(доступны латинские символы, цифры и знаки препинания, " \
                                                        "длина не должна превышать {max_login_length}):"

# compute_select_exercise_grade_for_create_callback
MESSAGE_ON_START_WAITING_EXERCISE_NAME_FOR_CREATE = "Введите название новой работы " \
                                                    "(доступны латинские символы, цифры и знаки препинания, " \
                                                        "длина не должна превышать {max_exercise_name_length}):"

# compute_select_quest_grade_for_create_callback
MESSAGE_ON_INVALID_QUEST_GRADE = "Для выбранного класса уже создан квест."
MESSAGE_ON_START_WAITING_QUEST_NAME_FOR_CREATE = "Введите название нового квеста " \
                                                    "(доступны латинские символы, цифры и знаки препинания, " \
                                                        "длина не должна превышать {max_exercise_name_length}):"

# compute_show_exercise_description_callback
FIRST_MESSAGE_IN_EXERCISE_DESCRIPTION = "Описание работы '{exercise_name}', {grade} класс.\n"

# compute_account_action_show_password_callback
MESSAGE_WITH_PASSWORD_DESCRIPTION = "Пароль пользователя '{login}': {password}"

# compute_account_action_show_user_callback
MESSAGE_ON_UNAUTHORIZED_USER_LOGIN = "В этот аккаунт никто не вошёл."
MESSAGE_WITH_USER_TELEGRAM_INFO = "Имя: {first_name}\nФамилия: {last_name}\nЛогин в телеграмме: @{username}."

# compute_student_account_action_show_mana_callback
MESSAGE_WITH_STUDENT_AMOUNT_MANA = "Общее количество маны пользователя '{login}': {mana}"

# compute_student_account_action_show_results_callback
MESSAGE_ON_EMPTY_LIST_OF_OPEN_WORKS = "На данный момент для пользователя '{login}' нет открытых работ."
TOP_MESSAGE_OF_USER_RESULTS_TABLE = "Результаты '{login}':"
TOP_MESSAGE_OF_USER_RESULTS_TABLE_EXERCISES = "Домашние работы:"
TOP_MESSAGE_OF_USER_RESULTS_TABLE_QUESTS = "Квесты:"

# compute_callback_data_show_task_statement_callback
MESSAGE_WITH_TEXT_EXERCISE_STATEMENT = "Условие задачи {task_id}:\n{text_statement}"
MESSAGE_WITH_FILE_EXERCISE_STATEMENT = "Условие задачи {task_id}."
STATEMENT_FILE_NAME = "statement"

# compute_solved_task_description_action_show_explanation_callback
MESSAGE_ON_UNAVAILABLE_ANSWER_EXPLANATION = "Пояснение к выбранной задаче недоступно."
MESSAGE_WITH_TASK_TEXT_EXPLANATION_FOR_ADMIN = "Пояснение '{login}' к задаче {task_id}:\n{text_explanation}"
MESSAGE_WITH_TASK_FILE_EXPLANATION_FOR_ADMIN = "Пояснение '{login}' к задаче {task_id}."
MESSAGE_WITH_TASK_TEXT_EXPLANATION_FOR_STUDENT = "Ваше пояснение к задаче {task_id}:\n{text_explanation}"
MESSAGE_WITH_TASK_FILE_EXPLANATION_FOR_STUDENT = "Ваше пояснение к задаче {task_id}."
EXPLANATION_FILE_NAME = "explanation"

# compute_solved_task_description_action_switch_student_answer_callback
MESSAGE_NOTIFICATION_FOR_STUDENT_ON_ACCEPTED_TASK = "Ваш ответ к задаче {task_id} в работе '{exercise_name}' был принят."
MESSAGE_NOTIFICATION_FOR_STUDENT_ON_REJECTED_TASK = "Ваш ответ к задаче {task_id} в работе '{exercise_name}' был отклонён."
MESSAGE_SUCCESS_SWITCH_STUDENT_ANSWER = "Ответ на задание успешно отредактирован."
MESSAGE_ON_CHANGED_USER_MANA_BY_CHANGING_ANSWER = "Значение маны пользователя было изменено."

# compute_show_right_answers_on_task_callback
MESSAGE_WITH_LIST_OF_RIGHT_ANSWERS_ON_TASK = "Список правильных ответов к задаче {task_id}:\n{correct_answer}"

# compute_student_account_change_mana_callback
MESSAGE_ON_START_WAITING_MANA_DELT = "Введите на сколько изменить ману пользователя " \
                                     "(положительное или отрицательное число):"

# ----------------------------------------------------------------------------------------------------------------------
# Messages text
# ----------------------------------------------------------------------------------------------------------------------


# __compute_button_back
MESSAGE_ON_EXIT_FROM_CURRENT_STATE = "Отмена...\n"

# __compute_button_exit
MESSAGE_ON_LOG_OUT_FROM_CURRENT_ACCOUNT = "Вы вышли из текущего аккаунта.\n"

# __compute_button_status
MESSAGE_ON_STATUS_UNAUTHORIZED_ACCOUNT = "Статус: не авторизован"
MESSAGE_ON_STATUS_ADMIN_ACCOUNT = "Логин: {login}\nПароль: {password}\nСтатус: {status}"
MESSAGE_ON_STATUS_STUDENT_ACCOUNT = "Логин: {login}\nПароль: {password}\nСтатус: {status}\nКласс: {grade}\nМана: {mana}"

# __compute_button_show_results_table
MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE_NO_HOMEWORKS_OPENED = "На данный момент нет открытых работ."
MESSAGE_ON_COMMAND_SHOW_RESULTS_TABLE = "Выберите имя работы."

# __compute_button_admin_get_list_of_exercises
MESSAGE_ON_GET_LIST_OF_EXERCISES_NO_HOMEWORKS_OPENED = "На данный момент нет открытых работ."
MESSAGE_EXERCISE_NAME_IN_LIST_OF_EXERCISES = "{exercise_name}, {grade} класс"
MESSAGE_QUEST_NAME_IN_LIST_OF_EXERCISES = "Квест: {exercise_name}, {grade} класс"

# __compute_button_admin_get_list_of_accounts
TOP_MESSAGE_OF_LIST_OF_SUPER_ADMINS = "Супер-администраторы:"
TOP_MESSAGE_OF_LIST_OF_ADMINS = "Администраторы:"
TOP_MESSAGE_OF_LIST_OF_STUDENTS = "Ученики:"
STUDENT_DESCRIPTION_IN_LIST_OF_STUDENTS = "{login}, {grade} класс"

# __compute_button_admin_add_action
MESSAGE_ON_ADMIN_ADD_COMMAND = "Выберите объект для добавления:"

# __compute_button_admin_delete_action
MESSAGE_ON_ADMIN_DELETE_COMMAND = "Выберите объект для удаления:"

# __compute_button_student_send_answer
MESSAGE_ON_STUDENT_SEND_ANSWER_NO_HOMEWORKS_AVAILABLE = "На данный момент для вас нет открытых работ."
MESSAGE_ON_STUDENT_SEND_ANSWER = "Выберите имя работы."

# __compute_button_student_want_to_send_explanation
MESSAGE_ON_START_WAITING_EXPLANATION = "Следующим сообщением вы должны отправить решение задачи. " \
                                    "Для этого можно либо приложить файл, либо написать решение текстом, " \
                                    "либо сделать и то, и другое." \
                                    " ВАЖНО: и файл, и текстовое сообщение должны быть отправлены одним сообщением."

# __compute_button_admin_add_student
MESSAGE_ON_ADMIN_ADD_NEW_STUDENT = "Выберите класс нового ученика."

# __compute_button_admin_add_quest
MESSAGE_ON_EMPTY_GRADES_LIST_FOR_CREATE_QUEST = "Уже добавлены квесты для всех классов."
MESSAGE_ON_ADMIN_ADD_NEW_QUEST = "Выберите для какого класса будет создан квест."

# __compute_button_admin_add_exercise
MESSAGE_ON_ADMIN_ADD_NEW_EXERCISE = "Выберите для какого класса будет создано задание."

# __compute_button_adding_statement_for_task
MESSAGE_ON_ADD_STATEMENT_FOR_TASK = "Следующим сообщением вы должны отправить условие задачи. " \
                                    "Для этого можно либо приложить файл, либо написать условие текстом, " \
                                    "либо сделать и то, и другое." \
                                    " ВАЖНО: и файл, и текстовое сообщение должны быть отправлены одним сообщением."

# __compute_button_super_admin_add_admin_account
MESSAGE_ON_SUPER_ADMIN_ADD_NEW_ADMIN = "Введите логин для нового аккаунта администратора."

# __compute_button_admin_delete_account
MESSAGE_ON_ADMIN_DELETE_ACCOUNT = "Введите логин аккаунта для удаления:"

# __compute_button_admin_delete_exercise
MESSAGE_ON_ADMIN_DELETE_EXERCISE = "Введите имя работы для удаления:"

# common
RIGHT_ANSWERS_SPLITER = "\n"
MESSAGE_ON_UNKNOWN_COMMAND = "Неизвестная команда"
TOP_MESSAGE_OF_LIST_OF_EXERCISES = "Домашние работы"
TOP_MESSAGE_OF_LIST_OF_QUESTS = "Квесты"

# default_state
WELCOME_MESSAGE_FOR_ADMIN = "С возвращением. Статус аккаунта: администратор."
WELCOME_MESSAGE_FOR_STUDENT = "С возвращением. Статус аккаунта: ученик."
WELCOME_MESSAGE_FOR_UNAUTHORIZED_USERS = "Введите логин аккаунта для авторизации:"

# unauthorized_user_waiting_login
MESSAGE_ON_INVALID_LOGIN = "Пользователя с таким логином не существует, повторите попытку."
MESSAGE_ON_VALID_LOGIN = "Введите пароль:"

# unauthorized_user_waiting_password
MESSAGE_ON_INVALID_PASSWORD = "Введён неправильный пароль, повторите попытку."
NOTIFICATION_FOR_LAST_USER_ON_AUTHORIZED_ACCOUNT = "В ваш профиль выполнен вход с другого телеграмм аккаунта, " \
                                                   "ваша сессия прекращена. Введите логин для авторизации:"
MESSAGE_ON_SUCCESS_ADMIN_AUTHORIZATION = "Успешная авторизация. Статус аккаунта: администратор."
MESSAGE_ON_SUCCESS_STUDENT_AUTHORIZATION = "Успешная авторизация. Статус аккаунта: ученик."

# solving_task_waiting_answer
MESSAGE_ON_INVALID_EXERCISE_NAME = "Выбранное задание сейчас недоступно."
MESSAGE_ON_INVALID_ANSWER = "Введён некорректный ответ, повторите попытку сдачи."
MESSAGE_RIGHT_RESULT_MARK = "✅"
MESSAGE_WRONG_RESULT_MARK = "❌"
MESSAGE_ON_RIGHT_ANSWER = "Ваш ответ правильный!"
MESSAGE_ON_MANA_CHANGING = "Вам начислено {count} единиц маны."
MESSAGE_ON_WRONG_ANSWER = "Ваш ответ неправильный. Список правильных ответов:\n{correct_answer}"
NOTIFICATION_FOR_ADMINS_ON_SOLVED_TASK = "'{login}', {grade} класс добавил ответ к заданию {task_id} в работе '{exercise_name}'\n" \
                                         "Результат: {result}\n" \
                                         "Ответ ученика: {answer}\n" \
                                         "Список правильных ответов:\n{correct_answer}"

# solving_task_send_explanation_interface
MESSAGE_ON_MOVING_IN_EXPLANATION_SENDING_INTERFACE = "Добавить пояснение к ответу?"

# solving_task_waiting_explanation
MESSAGE_ON_SUCCESS_ADDED_EXPLANATION = "Пояснение к задаче успешно добавлено."

# adding_exercise_waiting_exercise_name
MESSAGE_ON_ALREADY_EXISTS_EXERCISE_NAME = "Работа с введённым именем уже существует, повторите попытку."
MESSAGE_ON_INVALID_NEW_EXERCISE_NAME = "Введённое имя работы содержит запрещённые символы, повторите попытку."
MESSAGE_ON_TOO_LONG_NEW_EXERCISE_NAME = "Введённое имя работы слишком длинное, повторите попытку."
MESSAGE_ON_CORRECT_NEW_EXERCISE_NAME = "Введите количество заданий в новой работе:"

# adding_exercise_waiting_number_of_right_answers
MESSAGE_ON_INVALID_NUMBER_OF_TASKS = "Введено некорректное число задач, повторите попытку."
MESSAGE_ON_CORRECT_NUMBER_OF_TASKS = "Поочерёдно заполните информацию о каждом задании."

# adding_exercise_waiting_list_of_right_answers
MESSAGE_ON_ACCEPTED_RIGHT_ANSWER = "Ответ принят."
MESSAGE_REQUEST_FOR_NEW_ANSWER = "Введите ответ к задаче номер {task_id}:"
MESSAGE_ON_SUCCESS_CREATION_OF_NEW_EXERCISE = "Новая работа успешно создана."
MESSAGE_ON_SUCCESS_CREATION_OF_NEW_QUEST = "Новый квест успешно создан."

# adding_exercise_waiting_statement
MESSAGE_ON_SUCCESS_STATEMENT_ADDITION = "Условие успешно добавлено."

# adding_exercise_waiting_answer_on_task_answers
MESSAGE_ON_MOVE_INTO_TASK_ADDING_INTERFACE = "Выберите действие для текущего задания {task_id}."

# adding_student_waiting_login
MESSAGE_ON_ALREADY_EXISTS_STUDENT_LOGIN = "Пользователь с таким логином уже существует, повторите попытку."
MESSAGE_ON_INVALID_NEW_STUDENT_LOGIN = "Введённый логин содержит запрещённые символы, повторите попытку."
MESSAGE_ON_TOO_LONG_NEW_STUDENT_LOGIN = "Введённый логин слишком длинный, повторите попытку."
MESSAGE_ON_CORRECT_NEW_STUDENT_LOGIN = "Введите пароль для нового аккаунта ученика:"

# adding_student_waiting_password
MESSAGE_ON_SUCCESS_ADDING_NEW_STUDENT_ACCOUNT = "Новый аккаунт ученика успешно создан."

# adding_admin_waiting_login
MESSAGE_ON_ALREADY_EXISTS_ADMIN_LOGIN = "Пользователь с таким логином уже существует, повторите попытку."
MESSAGE_ON_INVALID_NEW_ADMIN_LOGIN = "Введённый логин содержит запрещённые символы, повторите попытку."
MESSAGE_ON_TOO_LONG_NEW_ADMIN_LOGIN = "Введённый логин слишком длинный, повторите попытку."
MESSAGE_ON_CORRECT_NEW_ADMIN_LOGIN = "Введите пароль для нового аккаунта администратора:"

# adding_admin_waiting_password
MESSAGE_ON_SUCCESS_ADDING_NEW_ADMIN_ACCOUNT = "Новый аккаунт администратора успешно создан."

# deleting_account_waiting_login
MESSAGE_ON_INVALID_LOGIN_FOR_DELETE = "Пользователя с введенным логином не существует, повторите попытку."
MESSAGE_ON_FORBIDDEN_LOGIN_FOR_DELETE = "Вы не можете удалить этот аккаунт."
NOTIFICATION_FOR_LAST_USER_ON_DELETED_ACCOUNT = "Ваш аккаунт был удалён администратором. Введите логин для авторизации."
MESSAGE_ON_SUCCESS_DELETION_ACCOUNT = "Аккаунт успешно удалён."

# deleting_exercise_waiting_name
MESSAGE_ON_INVALID_EXERCISE_NAME_FOR_DELETE = "Не существует работы с введённым именем, повторите попытку."
MESSAGE_ON_SUCCESS_DELETION_EXERCISE = "Работа успешно удалена."

# changing_student_mana_waiting_delta
MESSAGE_ON_INVALID_USER_LOGIN = "Пользователя с выбранным логином не существует."
MESSAGE_ON_INVALID_DELTA_OF_MANA = "Введено некорректное изменение маны."
MESSAGE_ON_SUCCESS_CHANGING_STUDENT_MANA = "Количество маны было успешно изменено."
