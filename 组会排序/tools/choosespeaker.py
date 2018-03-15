'''每周运行一次，选出本周speaker，一轮之中不出现重复speaker；对于两轮之间，同一个speaker两次之间至少隔两周'''

import random
import os
import time
import configparser


def initial_write():
    config = configparser.ConfigParser()
    config.add_section('all')
    config.set('all', 'candidates', 'A,B,C,D,E,F,G,H,I,J,K,L,M,N')
    config.add_section('left')
    config.set('left', 'candidates', '')
    config.add_section('record')
    config.set('record', 'candidates', '')
    with open('members.ini', 'w', encoding='UTF-8') as configfile:
        config.write(configfile)


def write_data(name, info):
    config = configparser.ConfigParser()
    config.read('members.ini', encoding='UTF-8')
    config.set(name, 'candidates', ','.join(info))
    with open('members.ini', 'w', encoding='UTF-8') as configfile:
        config.write(configfile)


def read_data(name):
    if not (os.path.exists('members.ini') and os.path.isfile('members.ini')):
        initial_write()
    config = configparser.ConfigParser()
    config.read('members.ini', encoding='UTF-8')
    content = config.get(name, 'candidates')
    if content:
        return content.split(',')
    else:
        return []


def choose_speaker(li, rec):
    speaker = random.choice(li)
    while speaker in rec:
        speaker = random.choice(li)
    return speaker


def make_decisions():
    random.seed(time.time())
    candidate = read_data('all')
    if not read_data('left'):
        left_can = candidate
    else:
        left_can = read_data('left')
    rec = read_data('record')
    speaker = choose_speaker(left_can, rec)
    print('下周组会轮到你：%s' % speaker)
    rec.append(speaker)
    if len(rec) > 2:
        rec.pop(0)
    write_data('record', rec)
    left_can.remove(speaker)
    if not left_can:
        left_can = candidate
    write_data('left', left_can)
    return '下周组会轮到你：%s@%s' % (speaker, speaker)


def initial():
    write_data('record', '')
    write_data('left', '')


if __name__ == '__main__':
    make_decisions()
