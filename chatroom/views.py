
import threading
from django.shortcuts import render
from dwebsocket.decorators import accept_websocket,require_websocket
from django.http import HttpResponse



clients = {} 

def index(request,schoolname,classname):
    return render(request, 'index.html',{"schoolname":schoolname,"classname":classname})


def modify_message(message):
    return message.lower()


@accept_websocket
def echo(request,schoolname,classname):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            if not (schoolname+classname) in clients:
                clients[schoolname+classname] = []
            clients[schoolname+classname].append(request.websocket)
            for message in request.websocket:
                if not message:
                    break
                for client in clients[schoolname+classname]:
                    client.send(message)
        finally:
            lock.release()
            
#@accept_websocket
#def echo(request):
#    if not request.is_websocket():#判断是不是websocket连接
#        try:#如果是普通的http方法
#            message = request.GET['message']
#            return HttpResponse(message)
#        except:
#            return render(request,'index.html')
#    else:
#        for message in request.websocket:

@accept_websocket
def echo_once(request):
    schoolname = 'xjtu'
    classname = 'software'
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            if not schoolname+classname in clients:
                clients[schoolname+classname] = []
            clients[schoolname+classname].append(request.websocket)
            for message in request.websocket:
                if not message:
                    break
                for client in clients[schoolname+classname]:
                    client.send(message)
        finally:
            lock.release()
#            request.websocket.send(message)#发送消息到客户端
