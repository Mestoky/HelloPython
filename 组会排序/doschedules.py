import schedule
import time
from tools import sendwechat, choosespeaker


def job():
    sendwechat.send_chatrooms_msg(choosespeaker.make_decisions(), '马欢')


schedule.every(5).seconds.do(job)
# schedule.every().friday.at("23:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

