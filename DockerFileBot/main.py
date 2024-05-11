import datetime
import logging
import os
import re
import prettytable
import paramiko
import psycopg2
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv('TOKEN')

logging.basicConfig(filename='../logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Hellow, {user.full_name} ( ´ ∀ ` )ﾉ please use /help for commands!')
    context.bot.send_sticker(chat_id=update.message.chat_id,
                             sticker='CAACAgIAAxkBAAErPh1mOFl9BFBDMH3dc2BF9c5w_RYifgACBygAAtJJaEgTl0HFZiKOszUE')


def whoami(update: Update, context):
    update.message.reply_text(f'THATS YOU!!!! (〃＾▽＾〃)')
    context.bot.send_sticker(chat_id=update.message.chat_id,
                             sticker='CAACAgIAAxkBAAErPj1mOFxDJsNOJfbSUo1NkmVvWacK4AACtT4AAuzI-UtGBnyUAm9EmjUE')


def connectToDb():
    try:
        conn = psycopg2.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                                host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), database=os.getenv("DB_DATABASE"))
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def helpCommand(update: Update, context):
    update.message.reply_text('''
    <i>I CAN DO THIS STUFF</i>:
    ◇─◇──◇─Bot─◇──◇─◇
    ✧ /start ඞ
    ✧ /help ඞ
    ✧ /whoami ඞ
    ◇─◇──◇─RegEX─◇──◇─◇
    ✧ /find_emails ඞ
    ✧ /find_phone_numbers ඞ
    ✧ /verify_password ඞ
    ◇─◇─Linux─Monitoring─◇─◇
    ✧ /get_release ඞ
    ✧ /get_uname ඞ
    ✧ /get_uptime ඞ
    ✧ /get_df ඞ
    ✧ /get_free ඞ
    ✧ /get_mpstat ඞ
    ✧ /get_w ඞ
    ✧ /get_auths ඞ
    ✧ /get_critical ඞ
    ✧ /get_ps ඞ
    ✧ /get_ss ඞ
    ✧ /get_apt_list ඞ
    ✧ /get_services ඞ
    ◇─◇──◇─DB─◇──◇─◇
    ✧ /get_repl_logs ඞ
    ✧ /db_phone_numbers ඞ
    ✧ /db_emails ඞ
    ◇─◇──◇─End─◇──◇─◇
    ''', parse_mode='HTML')
    context.bot.send_sticker(chat_id=update.message.chat_id,
                             sticker='CAACAgEAAxkBAAErUF9mPQs8yUDT9RM1i77MMeTHrBS71AACuQEAAi1DuUVMhuIdoMGb4TUE')

def ram(update: Update, context):
    update.message.reply_text("Our lives are short. Will you share yours with me?")
    context.bot.send_animation(chat_id=update.message.chat_id, animation=r'https://media1.tenor.com/m/Q9DfmJUXe1EAAAAd/overwatch-ramattra.gif')


def ssh_connect(str_command):
    host = os.getenv("RM_HOST")
    port = os.getenv("RM_PORT")
    username = os.getenv("RM_USER")
    password = os.getenv("RM_PASSWORD")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(str_command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


def create_handler(command_name, command_func, state_name, execute_func):
    return ConversationHandler(
        entry_points=[CommandHandler(command_name, command_func)],
        states={
            state_name: [MessageHandler(Filters.text & ~Filters.command, execute_func)],
        },
        fallbacks=[]
    )


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Can you type me textto to find phones?? 	☆ ～(^▽^人) im like.. poor OSINT assistant')
    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text

    phone_num_regex = re.compile(r'[8|+7][\s\-]*\(?\d{3}\)?[\s\-]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}')
    phone_number_list = phone_num_regex.findall(user_input)

    if not phone_number_list:
        update.message.reply_text('No phone numbers... oh :c')
        return ConversationHandler.END

    phone_numbers = ''
    for i in range(len(phone_number_list)):
        phone_numbers += f'{i + 1}. {phone_number_list[i]}\n'

    connection = connectToDb()
    if connection:
        try:
            with connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO phones(phone_number, telegram_user_id, username, msg_date)
                    VALUES (%s, %s, %s, %s)
                    """
                for phone in phone_number_list:
                    cursor.execute(insert_query, (phone, update.effective_user.id,
                                                  update.effective_user.username, datetime.datetime.now().date()))
            connection.commit()
        except Exception as e:
            update.message.reply_text("Oh .. i couldn't insert your phones right now... (ノ_<。)")
        finally:
            connection.close()
    else:
        update.message.reply_text("Somebody stole my database 	(⇀‸↼‶)")

    update.message.reply_text(phone_numbers)
    update.message.reply_text("You can see which phone numbers you found using /db_phone_numbers ☆ ～('▽^人)")
    context.bot.send_sticker(chat_id=update.message.chat_id,
                             sticker='CAACAgIAAxkBAAErQB1mONqeFKCa_vRBPKF2bbXFwPPUFQAChBQAArO70EtWYhEvSPGKpTUE')
    return ConversationHandler.END


def dbOutputPhoneNumbers(update: Update, context):
    connection = connectToDb()
    if connection:
        try:
            with connection.cursor() as cursor:
                select_query = """
                           SELECT phone_number, username, msg_date FROM phones
                           WHERE telegram_user_id = %s
                           """
                cursor.execute(select_query, (update.effective_user.id,))
                data = cursor.fetchall()
                if not data:
                    update.message.reply_text("No data for you... let's go find anything with"
                                              " /find_phone_numbers together! ヾ(・ω・`)ノヾ(´・ω・)ノ゛	")
                    context.bot.send_sticker(chat_id=update.message.chat_id,
                                             sticker='CAACAgIAAxkBAAErQm1mOVrDt9U-E4-ERCQV7J7eYXPjvwACZB4AAihXgUmUUOtkAdktlDUE')
                else:
                    table = prettytable.PrettyTable()
                    table.field_names = ["Phone Number", "Username", "Date"]
                    for row in data:
                        table.add_row(row)
                    table_string = table.get_string()
                    update.message.reply_text(f"Here you go! Your phone numbers ( ´-ω･)︻┻┳══━一:"
                                              f"```\n{table_string}\n```", parse_mode="Markdown")
                    update.message.reply_text("You can find more using /find_phone_numbers ヽ(ˇ∀ˇ )ゞ")
        except Exception as e:
            update.message.reply_text("Oh .. i couldn't find your phone numbers data right now... (ノ_<。)")
        finally:
            connection.close()
    else:
        update.message.reply_text("Somebody stole my database 	(⇀‸↼‶)")


def findEmailsCommand(update: Update, context):
    update.message.reply_text('Can you type me textto to find emaills???  ☆ ～(^▽^人) im like.. poor OSINT assistant')
    return 'findEmails'


def findEmails(update: Update, context):
    user_input = update.message.text

    email_regex = re.compile(r'[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}')
    email_list = email_regex.findall(user_input)

    if not email_list:
        update.message.reply_text('No emails... oh :c')
        return ConversationHandler.END

    emails = ''
    for i in range(len(email_list)):
        emails += f'{i + 1}. {email_list[i]}\n'

    connection = connectToDb()
    if connection:
        try:
            with connection.cursor() as cursor:
                insert_query = """
                        INSERT INTO emails(email, telegram_user_id, username, msg_date)
                        VALUES (%s, %s, %s, %s)
                        """
                for email in email_list:
                    cursor.execute(insert_query, (email, update.effective_user.id,
                                                  update.effective_user.username, datetime.datetime.now().date()))
            connection.commit()
        except Exception as e:
            update.message.reply_text("Oh .. i couldn't insert your emails right now... (ノ_<。)")
        finally:
            connection.close()
    else:
        update.message.reply_text("Somebody stole my database 	(⇀‸↼‶)")

    update.message.reply_text(emails)
    update.message.reply_text("You can see which emails you found using /db_emails ☆ ～('▽^人)")
    context.bot.send_sticker(chat_id=update.message.chat_id,
                             sticker='CAACAgIAAxkBAAErQCFmONq5IMFaxfjtD02nSuXkP3Cc0gACEzcAAoMNWEvU6xZQbuvNhDUE')

    return ConversationHandler.END


def dbOutputEmails(update: Update, context):
    connection = connectToDb()
    if connection:
        try:
            with connection.cursor() as cursor:
                select_query = """
                           SELECT email, username, msg_date FROM emails
                           WHERE telegram_user_id = %s
                           """
                cursor.execute(select_query, (update.effective_user.id,))
                data = cursor.fetchall()
                if not data:
                    update.message.reply_text("No data for you... let's go find anything with"
                                              " /find_emails together! ヾ(・ω・`)ノヾ(´・ω・)ノ゛	")
                    context.bot.send_sticker(chat_id=update.message.chat_id,
                                             sticker='CAACAgIAAxkBAAErQmdmOVmKWD3rBgq-HVvKmU7TwFBfSwACHjAAAiBcUEgwpYVCybjqoDUE')
                else:
                    table = prettytable.PrettyTable()
                    table.field_names = ["Phone Number", "Username", "Date"]
                    for row in data:
                        table.add_row(row)
                    table_string = table.get_string()
                    update.message.reply_text(f"Here you go! Your emails ( ´-ω･)︻┻┳══━一:"
                                              f"```\n{table_string}\n```", parse_mode="Markdown")
                    update.message.reply_text("You can find more using /find_emails ヽ(ˇ∀ˇ )ゞ")
        except Exception as e:
            update.message.reply_text("Oh .. i couldn't find your emails data right now... (ノ_<。)")
        finally:
            connection.close()
    else:
        update.message.reply_text("Somebody stole my database 	(⇀‸↼‶)")


def checkPassCommand(update: Update, context):
    update.message.reply_text('check your pass?? oK i will check it with my plush Rei <(￣︶￣)>	')
    return 'checkPass'


def checkPass(update: Update, context):
    user_input = update.message.text

    pass_regex = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$')
    password = pass_regex.search(user_input)

    if not password:
        update.message.reply_text('Rei said no to your pass. I am sowwy ...')
        return ConversationHandler.END

    update.message.reply_text('Rei approved! You have GREAT SECURE pass!')
    context.bot.send_sticker(chat_id=update.message.chat_id,
                             sticker='CAACAgIAAxkBAAErQCNmONsVBa-9nyNVvlnXfH1RuKLfigACTBAAAvh-kEjvVlNYeKGD4DUE')
    return ConversationHandler.END


def checkAptCommand(update: Update, context):
    result = ssh_connect("apt list --installed | awk '{print $1}' | head -n 50")
    update.message.reply_text(result)
    update.message.reply_text('Which pckg you want to read info about???')
    return 'checkApt'


def checkApt(update: Update, context):
    user_input = update.message.text
    result = ssh_connect(f"apt show {user_input}")

    if "E:" in result:
        update.message.reply_text(f"No information found for your package '{user_input}' (｡T ω T｡)	")
    else:
        update.message.reply_text(result)
        update.message.reply_text(
            "You wanna know your package - i get you your package! We like.. friends already teehee °˖✧◝(⁰▿⁰)◜✧˖°")
    return ConversationHandler.END


def checkServiceCommand(update: Update, context):
    result = ssh_connect("systemctl list-units --type=service | awk '{print $1}' | head -n 50")
    update.message.reply_text(result)
    update.message.reply_text('Say me your service - and i will say who you are! (Joke, just info about service..)')
    return 'checkService'


def checkService(update: Update, context):
    user_input = update.message.text
    result = ssh_connect(f"systemctl status {user_input} --no-pager")

    if "not found" in result.lower() or "could not be found" in result.lower():
        update.message.reply_text(f"I camt found '{user_input}'...")
    else:
        update.message.reply_text(result)
        update.message.reply_text("Here you go!! All about your soulmate-sevice!!(*¯ ³¯*)♡	")
    return ConversationHandler.END


def readLogFile(log_path, num_lines=20):
    with open(log_path, 'r') as f:
        lines = f.readlines()
    filtered_lines = [line for line in lines if 'repl' in line.lower() or 'accept connections' in line.lower()]
    return filtered_lines[-num_lines:]


def replLogsCommand(update: Update, context):
    log_path = '/var/log/postgresql/postgresql-15-main.log'
    try:
        filtered_logs = readLogFile(log_path)
        log_content = "".join(filtered_logs)
        if not log_content:
            update.message.reply_text("No logs ufufu -●●●-ｃ(・・ )")
        else:
            update.message.reply_text(log_content)
            update.message.reply_text("Woah, you can replicate?!!??!")
    except Exception as e:
        update.message.reply_text(f"Error reading log file: {e}")


def ssh_command(update: Update, context):
    command_map = {
        "get_release": "lsb_release -a",
        "get_uname": "uname -a",
        "get_uptime": "uptime",
        "get_df": "df -h",
        "get_free": "free -h",
        "get_mpstat": "mpstat -A",
        "get_w": "w",
        "get_auths": "last -n 10",
        "get_critical": "journalctl -p 2 -n 5",
        "get_ps": "ps -eo comm | head -n 50",
        "get_ss": "ss -tunlp"
    }

    user_command = update.message.text.replace("/", "")

    if user_command not in command_map:
        update.message.reply_text("there's no command like this (-ω-、)")
        return

    command = command_map[user_command]
    result = ssh_connect(command)
    update.message.reply_text(result)
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    command_list = ['get_release', 'get_uname', 'get_uptime', 'get_df', 'get_free', 'get_mpstat', 'get_w', 'get_auths',
                    'get_critical', 'get_ps', 'get_ss']

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("whoami", whoami))
    dp.add_handler(create_handler('find_phone_numbers', findPhoneNumbersCommand, 'findPhoneNumbers', findPhoneNumbers))
    dp.add_handler(create_handler('find_emails', findEmailsCommand, 'findEmails', findEmails))
    dp.add_handler(create_handler('verify_password', checkPassCommand, 'checkPass', checkPass))
    dp.add_handler(create_handler('get_apt_list', checkAptCommand, 'checkApt', checkApt))
    dp.add_handler(create_handler('get_services', checkServiceCommand, 'checkService', checkService))
    dp.add_handler(CommandHandler(command_list, ssh_command))
    dp.add_handler(CommandHandler("get_repl_logs", replLogsCommand))
    dp.add_handler(CommandHandler("db_phone_numbers", dbOutputPhoneNumbers))
    dp.add_handler(CommandHandler("db_emails", dbOutputEmails))
    dp.add_handler(CommandHandler("special_for_melock", ram))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
