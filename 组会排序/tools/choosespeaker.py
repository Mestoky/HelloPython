"""每周运行一次，选出本周speaker，一轮之中不出现重复speaker；对于两轮之间，同一个speaker两次之间至少隔两周"""
import configparser
import random
import time


def read_config():
    """生成config并读取/初始化ini文件"""
    config = configparser.ConfigParser()
    if config.read('members.ini', encoding='UTF-8'):
        all_can = config.get('all', 'candidates').split(',')
        left_can = config.get('left', 'candidates').split(',')
        rec_can = config.get('record', 'candidates').split(',')
    else:
        all_can = ['A', 'B', 'C', 'D', 'E', 'F']
        left_can = all_can[:]
        rec_can = []
        config.add_section('all')
        config.add_section('left')
        config.add_section('record')
        config.set('all', 'candidates', ','.join(all_can))
    return config, all_can, left_can, rec_can


def write_config(config, speaker, all_can, left_can, rec_can):
    """处理left_can和rec_can并写入ini"""
    left_can.remove(speaker)
    rec_can.append(speaker)
    if len(left_can) == 0:
        left_can.extend(all_can)
    if len(rec_can) > 2:
        rec_can.pop(0)
    config.set('left', 'candidates', ','.join(left_can))
    config.set('record', 'candidates', ','.join(rec_can))
    with open('members.ini', 'w', encoding='UTF-8') as configfile:
        config.write(configfile)


def make_decision():
    """从演讲候选人中选出演讲人"""
    config, all_can, left_can, rec_can = read_config()  # 获取演讲候选人
    random.seed(time.time())  # 设定随机种子
    speaker = random.choice(list(set(left_can) - set(rec_can)))  # 选出演讲人
    write_config(config, speaker, all_can, left_can, rec_can)  # 保存结果
    return speaker


if __name__ == '__main__':
    print(make_decision())
