import requests
import sys
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

API = "http://openedx.ing.puc.cl/user_api/v1/account/login_session/"
EMAIL = 'EMAIL'
PASSWORD = 'PASSWORD'
BOT_TOKEN = '700596284:AAFQgaXUPXJNTDExZuySj1EI7bdlJylHBSI'
FETCH = 300
OLD_DATA = []
NEW_DATA = []


def start(bot, job):
    bot.send_message(job.context, text='🤖 Hola! 🤖\n Este es el bot para recibir mensajes del foro de Sistemas Operativos y Redes. Para comenzar, escribe /login <email> <password> para iniciar sesión.')

def getToken(client):
    client.get(API)
    if 'csrftoken' in client.cookies:
        return client.cookies['csrftoken']
    else:
        return client.cookies['csrf']
def loginToAPI(client, token):
    print("TOKEN, ", token)
    login_data = dict(email=EMAIL, password=PASSWORD, csrfmiddlewaretoken=token, next='/')
    r = client.post(API, data=login_data, headers=dict(Referer=API))
    return (r.status_code)
    print("LOGIN", r.status_code, r.reason)

def update(bot, job):
    """Revisa si hay nuevos comentarios"""
    global OLD_DATA
    global NEW_DATA
    global EMAIL
    global PASSWORD
    client = requests.session()
    csrftoken = getToken(client)
    loginToAPI(client, csrftoken)
    s = client.get("http://openedx.ing.puc.cl/api/discussion/v1/threads/?course_id=course-v1%3APUC%2BIIC2333_II%2BIIC2333_II_2018&sort_order=desc")
    #print("GET COMMENTS", s.status_code, s.reason)
    answer = s.json()
    print(answer)
    if len(OLD_DATA) == 0:
        OLD_DATA = answer['results']
        NEW_DATA = OLD_DATA
    else:
        OLD_DATA = NEW_DATA
        NEW_DATA = answer['results']   
        if OLD_DATA != NEW_DATA:
            result = [x for x in NEW_DATA if x not in OLD_DATA][0]
            author = result['author']
            title = result['title']
            comment = result['raw_body']
            link = str("http://openedx.ing.puc.cl/courses/"+
                    result['course_id']+"/discussion/forum/"+
                    result['topic_id']+"/threads/"+result['id'])
            text = str("📩 Nueva pregunta/comentario 📩 \n"+
                    "👤: " + author + "\n"+
                    "Título: "+title+"\n"+
                    "Comentario: "+comment+"\n"+
                    "🔗: "+link)
            bot.send_message(job.context, text=text)
        else:
            bot.send_message(job.context, text="✅ No hay nuevos mensajes")




def getComments(bot,job):
    """Revisa si hay nuevos comentarios"""
    global OLD_DATA
    global NEW_DATA
    global EMAIL
    global PASSWORD
    client = requests.session()
    csrftoken = getToken(client)
    loginToAPI(client, csrftoken)
    s = client.get("http://openedx.ing.puc.cl/api/discussion/v1/threads/?course_id=course-v1%3APUC%2BIIC2333_II%2BIIC2333_II_2018&sort_order=desc")
    #print("GET COMMENTS", s.status_code, s.reason)
    answer = s.json()
    if len(OLD_DATA) == 0:
        OLD_DATA = answer['results']
        NEW_DATA = OLD_DATA
    else:
        OLD_DATA = NEW_DATA
        NEW_DATA = answer['results']   
        if OLD_DATA != NEW_DATA:
            result = [x for x in NEW_DATA if x not in OLD_DATA][0]
            author = result['author']
            title = result['title']
            comment = result['raw_body']
            link = str("http://openedx.ing.puc.cl/courses/"+
                    result['course_id']+"/discussion/forum/"+
                    result['topic_id']+"/threads/"+result['id'])
            text = str("📩 Nueva pregunta/comentario 📩 \n"+
                    "👤: " + author + "\n"+
                    "Título: "+title+"\n"+
                    "Comentario: "+comment+"\n"+
                    "🔗: "+link)
            bot.send_message(job.context, text=text)

    return(s.json())

def login(bot, update, args, job_queue, chat_data):
    global EMAIL
    global PASSWORD
    chat_id = update.mesage.chat_id
    try:
        EMAIL = str(args[0])
        PASSWORD = str(args[1])
        job = job_queue.run_once(getComments, FETCH, context=chat_id)
        chat_data['job'] = job
        update.message_reply_text('Login exitoso. Se revisará el foro cada 5 minutos comprobando si existe un nuevo mensaje.\n También puedes ocupar /update para comprobar.')

        
    except(IndexError, ValueError):
        update.message.reply_text("Hubo un error en el proceso. Uso: /login <email> <password>")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"',update,error)




def main():
    try:
        print("hola")
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", start))
        dp.add_handler(CommandHandler("login", login,
                                        pass_args=True,
                                        pass_job_queue=True,
                                        pass_chat_data=True))
        dp.add_handler(CommandHandler("update", update))
        dp.add_error_handler(error)
        updater.start_polling()
        updater.idle()
    except(error):
        print(error)

if __name__ == '__main__':
    main()

