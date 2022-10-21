from datetime import datetime, timezone, timedelta, tzinfo
import json
import socket

from warehouse_state.models import *

class ProcessingActivity():
    '''
        Application: application name, such as os.path.basename(__file__)
        Function: application function, or 'main' if their is none
        ID: unique ID (pk) for this entry, this value should stay the same between processing
        Topic: type of information, such as 'Outages', 'inca', etc.
        About: which qualified resource (ResourceID) or domain the information is about
    '''
    def __init__(self, Application, Function, ID, Topic, About):
        self.Application = Application
        self.Function = Function
        self.ID = ID
        obj, created = ProcessingRecord.objects.update_or_create(
                            ID=ID,
                            defaults = {
                                'Topic': Topic,
                                'About': About,
                                'ProcessingNode': socket.gethostname(),
                                'ProcessingApplication': self.Application,
                                'ProcessingFunction': self.Function,
                                'ProcessingStart': datetime.now(timezone.utc)
                            })
        obj.save()
        self.model = obj

    def FinishActivity(self, Code, Message):
        self.model.ProcessingEnd=datetime.now(timezone.utc)
        if Code is False:
            self.model.ProcessingCode='1'
        elif Code is True:
            self.model.ProcessingCode='0'
        else:
            self.model.ProcessingCode=str(Code)
        if isinstance(Message, dict):
            self.model.ProcessingMessage=json.dumps(Message)
        else:
            self.model.ProcessingMessage=Message
        self.model.save()

        if self.model.ProcessingCode != '0':
            obj = ProcessingError(Topic=self.model.Topic,
                                 About=self.model.About,
                                 ProcessingNode=self.model.ProcessingNode,
                                 ProcessingApplication=self.model.ProcessingApplication,
                                 ProcessingFunction=self.model.ProcessingFunction,
                                 ErrorTime=self.model.ProcessingEnd,
                                 ErrorCode=self.model.ProcessingCode,
                                 ErrorMessage=self.model.ProcessingMessage,
                                 Reference1=self.model.ID
                             )
            obj.save()
            self.errmodel = obj
