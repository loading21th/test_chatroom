
import threading
from django.shortcuts import render
from dwebsocket.decorators import accept_websocket,require_websocket
from django.http import HttpResponse
from uwsgidecorators import postfork
import os
import redis
import logging

class RedisHelper:
    def __init__(self,channel):
        self.channel = channel
        self.__conn = redis.Redis(host='192.168.15.12')
        self.pub = self.__conn.pubsub()
        self.pub.subscribe(self.channel)

    def publishi(self,msg):
        self.__conn.publish(self.channel,msg)

    def unsubscribe(self):
        self.pub.unsubscribe()


    def subscribe(self,websocket):
        logger = logging.getLogger('django')
        logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' : i am the new thread')
        count = 0
        try:
            for item in self.pub.listen():
                if item['type'] == 'message':
                    count = count +1
                    logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' :recive message: '+str(item['data']))
                    websocket.send(item['data'])
        finally:
            logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' : unsubscribe')
            self.unsubscribe()

    @postfork
    def writeback(self,websocket):
        logger = logging.getLogger('django')
        logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' : ready to start a new thread')
        th1 = threading.Thread(target=self.subscribe,args=(websocket,))
        th1.start()

def index(request,schoolname,classname):
    return render(request, 'index.html',{"schoolname":schoolname,"classname":classname})


def modify_message(message):
    return message.lower()


#@accept_websocket
#def echo(request,schoolname,classname):
#    if request.is_websocket:
#        lock = threading.RLock()
#        try:
#            lock.acquire()
#            if not (schoolname+classname) in settings.WEBSOCKET_CLIENTS:
#                settings.WEBSOCKET_CLIENTS[schoolname+classname] = []
#            settings.WEBSOCKET_CLIENTS[schoolname+classname].append(request.websocket)
#            for message in request.websocket:
#                if not message:
#                    break
#                for client in settings.WEBSOCKET_CLIENTS[schoolname+classname]:
#                    client.send(message)
#        finally:
#            lock.release()
            
@accept_websocket
def echo(request,schoolname,classname):
    logger = logging.getLogger('django')
    logger.debug('****************'+str(os.getpid())+' : '+str(threading.currentThread())+' : connect')
    if request.is_websocket:
        client = RedisHelper(schoolname+classname);
        client.writeback(request.websocket)
        for message in request.websocket:
            if not message:
                break
            logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' : send a message')
            client.publishi(message)
#            for i in threading.enumerate():
#               print(str(i))
        logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' : websocket close')
    client.unsubscribe()
    logger.debug('*****'+str(os.getpid())+' : '+str(threading.currentThread())+' : 请求结束')



@accept_websocket
def echo_once(request):
    schoolname = 'xjtu'
    classname = 'software'
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            if not schoolname+classname in settings.WEBSOCKET_CLIENTS:
                settings.WEBSOCKET_CLIENTS[schoolname+classname] = []
            settings.WEBSOCKET_CLIENTS[schoolname+classname].append(request.websocket)
            for message in request.websocket:
                if not message:
                    break
                for client in settings.WEBSOCKET_CLIENTS[schoolname+classname]:
                    client.send(message)
        finally:
            lock.release()
#            request.websocket.send(message)#发送消息到客户端
