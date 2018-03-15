import itchat

if itchat.check_login != 200:
    itchat.auto_login(hotReload=True)


def send_friends_msg(context, name):
    users = itchat.search_friends(name=name)
    username = users[0]['UserName']
    itchat.send(context, toUserName=username)


def send_chatrooms_msg(context, name):
    itchat.get_chatrooms(update=True)
    iroom = itchat.search_chatrooms(name)
    roomname = ''
    for room in iroom:
        if room['NickName'] == name:
            roomname = room['UserName']
            break
    if not roomname:
        print('Error: Chatroom:%s Not Found.' % name)
        send_friends_msg('Error: Chatroom:%s Not Found.' % name)
    itchat.send_msg(context, roomname)


if __name__ == '__main__':
    send_chatrooms_msg('This is a test message. Sorry to disturb you.', '马欢')
