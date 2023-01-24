import locale
from telegram_logic.user_handler import UserHandler


def main():
    locale.setlocale(locale.LC_ALL, locale.normalize("RU"))

    bot = UserHandler()
    bot.run()


if __name__ == "__main__":
    main()
