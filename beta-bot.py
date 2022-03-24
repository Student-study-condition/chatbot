import logging
import os
from dotenv import load_dotenv
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

import src.cloudant_db.db as db
import src.statistic.compare as stat

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])

'''
start command
'''
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Hi I am Lena, I am a robot that can help you find a good environment to study. press /help for more information'
    )
'''
register
'''
def register(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    print(update.message.chat_id, "chatid")
    database = db.UserDatabase()
    print(database.add_user(str(update.message.chat_id), update.message.chat.username, update.message.chat.first_name, update.message.chat.first_name))
    update.message.reply_text(f"user id {update.message.chat_id} has been registered")

'''
unregister
'''
def unregister(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    print(update.message.chat_id, "chatid")
    database = db.UserDatabase()
    database.remove_user(str(update.message.chat_id))
    update.message.reply_text(f"user has been unregister")    

'''
help command
'''
def help(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    reply_text = '''Hi, we have the following command
    Use /start to start this bot.
    Use /register to register user, User must agree with our /policy
    Use /unregister to unregister user and stop using our service
    use /study to tell us you are studying in this location
    use /checkstudy to check if this is a good study location
    use /policy to look at our policy
    '''
    update.message.reply_text(reply_text)

'''
study command
'''
class Study:
    def __init__(self, study_location):
        self.database = db.UserDatabase()
        self.study_loc = study_location
        self.markup = ReplyKeyboardMarkup(self.study_loc, one_time_keyboard=True)

    #Start the conversation and ask user for input.
    def start(self, update: Update, context: CallbackContext) -> int:
        if self.database.get_user(str(update.message.chat_id)) == 'error':
            update.message.reply_text(f"user has not been registered please /register")
            return ConversationHandler.END
        else: 
            update.message.reply_text(
            "Hi! Could you tell me about your regular study location",
            reply_markup=self.markup,
            )

            return 1

    def __regular_choice(self, update: Update, context: CallbackContext) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text
        context.user_data['choice'] = text

        self.database.register_study_device(str(update.message.chat_id), text)
        
        update.message.reply_text(f'Device {text} Has been registered')

        return ConversationHandler.END

    def __noInput(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hi! That device is not registerd, could you try another one ",
            reply_markup=self.markup,
        )

        return 1

    def __end(self) -> int:
        return ConversationHandler.END

    def set_study_location(self) -> int:       
        # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
        study_handler = ConversationHandler(
            entry_points=[CommandHandler('study', self.start)],
            states={
                1: [
                    MessageHandler(
                        Filters.regex('^(4C11AE917C14|NOISY-LOC|DEVICE_ID)$'), self.__regular_choice
                    ),
                   MessageHandler(Filters.regex('^Done$'), self.__end),
                   MessageHandler(Filters.regex('^(?!.*(4C11AE917C14|NOISY-LOC|DEVICE_ID))'), self.__noInput),
                ]
            },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), self.__end)],
        )

        return study_handler
'''
check study command
'''
class checkStudy:
    def __init__(self, study_location):
        self.database = db.UserDatabase()
        self.iot_database = db.IOTdatabase()

        self.study_loc = study_location
        self.markup = ReplyKeyboardMarkup(self.study_loc, one_time_keyboard=True)

    #Start the conversation and ask user for input.
    def start(self, update: Update, context: CallbackContext) -> int:
        if self.database.get_user(str(update.message.chat_id)) == 'error':
            update.message.reply_text(f"user has not been registered please /register")
            return ConversationHandler.END
        else: 
            update.message.reply_text(
            "Hi! Where are you going to study",
            reply_markup=self.markup,
            )

            return 1

    def __regular_choice(self, update: Update, context: CallbackContext) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text
        context.user_data['choice'] = text

        try:
            if text in self.database.get_user(str(update.message.chat_id))['registerDevices']:
                update.message.reply_text('user are studing in their usual location')
            else:
                prefered_stat = self.iot_database.get_stat(self.database.get_user(str(update.message.chat_id))['registerDevices'][0])
                new_stat = self.iot_database.get_stat(text)  

                res = stat.compareData(prefered_stat, new_stat)

                if (res == 'ok'):
                    result = "This location is suitable for study"
                else:
                    result = "This location may be not recommended as " + res

                update.message.reply_text(f'The study location {result}')

                return ConversationHandler.END

        except:
            update.message.reply_text(
            "Is there any preferred /study location")
            return ConversationHandler.END

    def __noInput(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hi! that device does not exist, could you try another one ",
            reply_markup=self.markup,
        )

        return 1

    def __end(self) -> int:
        return ConversationHandler.END

    def check_study_location(self) -> int:       
        # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
        study_handler = ConversationHandler(
            entry_points=[CommandHandler('checkstudy', self.start)],
            states={
                1: [
                    MessageHandler(
                        Filters.regex('^(4C11AE917C14|NOISY-LOC|DEVICE_ID)$'), self.__regular_choice
                    ),
                   MessageHandler(Filters.regex('^Done$'), self.__end),
                   MessageHandler(Filters.regex('^(?!.*(4C11AE917C14|NOISY-LOC|DEVICE_ID))'), self.__noInput),
                ]
            },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), self.__end)],
        )

        return study_handler
'''
policy command
'''
def policy(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    reply_text = '''Hi, we are collecting your use username and telegram shown name for analytic purpose
    '''
    update.message.reply_text(reply_text) 

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    load_dotenv()
    updater = Updater(os.getenv('APP_TOKEN'))
    
    study_location = [['4C11AE917C14', 'NOISY-LOC', 'DEVICE_ID'], ['Cancel']]
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(Study(study_location).set_study_location())
    dispatcher.add_handler(checkStudy(study_location).check_study_location())
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('register', register))
    dispatcher.add_handler(CommandHandler('unregister', unregister))
    dispatcher.add_handler(CommandHandler('policy', policy))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()