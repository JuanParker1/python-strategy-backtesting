from config.auth import telegramBotToken, telegramGroupID


def sendMsg(ID=telegramGroupID, msg=''):
    """
    Send Telegram Message to selected ID.
    """
    import telegram

    bot = telegram.Bot(token=telegramBotToken)

    bot.sendMessage(chat_id=ID,
                    text=f'{msg}')


def sendImg(ID=telegramGroupID, caption='', img=''):
    """
    Send Telegram Message to selected ID.
    """
    import telegram

    bot = telegram.Bot(token=telegramBotToken)


    bot.sendPhoto(chat_id=ID,
                  caption=caption,
                  photo=open(img, 'rb'))

#sendMsg(ID=telegramGroupID, msg='Bonsoir')
