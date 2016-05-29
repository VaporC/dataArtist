import puka
from pyqtgraph_karl.Qt import QtCore, QtGui



class RabbitMQServer(object):
    '''
    A server for communicating between different programs 
    and remote control using RabbitMQ
    '''
    def __init__(self, gui):
        self.gui = gui
        self.timer = None
        
        self.opts = {'refreshrate':1000, #ms
                  'host':'localhost',
                  'timeout':1, #ms
                  'corfirmPosts':False
                  }

        self.listenTo = {'addFile':self.gui.addFilePath,
                         'changeActiveDisplay':lambda number: 
                                self.gui.currentWorkspace().changeDisplayNumber(number),
                         'showDisplay':self.gui.showDisplay,
                         'runScriptFromName':self.gui.runScriptFromName,
                         }

    
    def start(self):
        '''
        configure the server and check the 
        message-inbox every self.opts['refeshrate']
        '''
        self.configure()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkInbox)
        self.timer.start(self.opts['refreshrate'])


    def checkInbox(self):
        '''
        Check all self.listentO keys
           and execute connected method
        '''
        for promise, action in self.promises.items():
            msg_result = self.client.wait(promise, timeout=self.opts['timeout']/1000.0)#wait for 10ms
            if msg_result:
                #MESSAGE RECEIVED
                b = msg_result['body']
                if self.opts['corfirmPosts']:
                    #PRINT CONFIRMATION
                    print " [R] %s -> '%s'" % (msg_result['routing_key'], b)
                if b == 'STOP':
                    #stop listening to that channel:
                    self.promises.pop(promise)
                else:
                    action(b)
            
       
    def configure(self):
        self.client = puka.Client("amqp://%s/" %self.opts['host'])
        try:
            promise = self.client.connect()
        except Exception: 
            raise Exception("Couldn't connect to RabbitMQ. Please visit https://www.rabbitmq.com/download.html and install it.")
        self.client.wait(promise)

        self.promises = {}
        for name, action in self.listenTo.iteritems():
            #INITITALIZE ALL QUEUES
            promise = self.client.queue_declare(queue=name)
            self.client.wait(promise)
            consume_promise = self.client.basic_consume(queue=name, no_ack=True)
            self.promises[consume_promise] = action
        

    def stop(self):
        if self.timer is not None and self.timer.isActive():
            self.timer.stop()
            self.client.close()



if __name__ == '__main__':
    app = QtGui.QApplication([])
    r = RabbitMQServer(None)
    r.start()
    app.exec_()