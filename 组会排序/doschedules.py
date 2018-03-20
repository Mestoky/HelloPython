import schedule
import time
from tools import sendwechat, choosespeaker


def job():
    speaker = choosespeaker.make_decisions()
    print('下周组会轮到你：%s' % speaker)
    sendwechat.send_chatrooms_msg('下周组会轮到你：%s@%s' % (speaker, speaker), '马欢')


schedule.every(5).seconds.do(job)
# schedule.every().friday.at("23:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

