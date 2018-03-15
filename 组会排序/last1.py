import schedule
import time
from tools import send_wx, rand


def job():

    send_wx.send_chatrooms_msg(rand.decisions(), '马欢')


schedule.every(5).seconds.do(job)
# schedule.every().wednesday.at("23:53").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
    pass
