import schedule
import time
from tools import sendwechat, choosespeaker


def job():
    """每周运行一次，选出本周speaker，一轮之中不出现重复speaker；对于两轮之间，同一个speaker两次之间至少隔两周"""
    choosespeaker.read_config('members.ini')
    speaker = choosespeaker.choose_speaker()
    print('下周组会轮到你：%s' % speaker)
    sendwechat.send_chatrooms_msg('下周组会轮到你：%s@%s' % (speaker, speaker), '马欢')
    choosespeaker.save_data()


schedule.every(5).seconds.do(job)
# schedule.every().friday.at("23:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

