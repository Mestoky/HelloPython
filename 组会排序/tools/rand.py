'''每周运行一次，选出本周speaker，一轮之中不出现重复speaker；对于两轮之间，同一个speaker两次之间至少隔两周'''

import random
import os
import time
import configparser

config = configparser.ConfigParser()
config.read('example.ini', encoding='UTF-8')
candidate = config.get('Section1', 'candidate').split(',')


def write_f(file, info):
    config1 = configparser.ConfigParser()
    config1.add_section('Section1')
    config1.set('Section1', 'candidate', ','.join(info))
    with open(file, 'w', encoding='UTF-8') as configfile:
        config1.write(configfile)


def read_f(file):
    if not (os.path.exists(file) and os.path.isfile(file)):
        return []
    else:
        config2 = configparser.ConfigParser()
        config2.read(file, encoding='UTF-8')
        content = config2.get('Section1', 'candidate')
        if content:
            return config2.get('Section1', 'candidate').split(',')
        else:
            return []


def choose_speaker(li, rec):
    speaker = random.choice(li)
    if not rec or speaker not in rec:
        return speaker
    else:
        return choose_speaker(li, rec)


def decisions():
    random.seed(time.time())
    if not read_f('left.ini'):
        left_can = candidate
    else:
        left_can = read_f('left.ini')
    rec = read_f('rec.ini')
    speaker = choose_speaker(left_can, rec)
    print('下周组会轮到你：%s' % speaker)
    rec.append(speaker)
    if len(rec) > 2:
        rec.pop(0)
    write_f('rec.ini', rec)
    left_can.remove(speaker)
    if not left_can:
        left_can = candidate
    write_f('left.ini', left_can)
    return '下周组会轮到你：%s@%s' % (speaker, speaker)


def init():
    os.remove('left.ini')
    os.remove('rec.ini')


if __name__ == '__main__':
    decisions()
