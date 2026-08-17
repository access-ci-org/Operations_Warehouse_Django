from datetime import datetime, timezone, timedelta, tzinfo
import json
import logging
import socket

from django.db import DataError, IntegrityError
from django.conf import settings

from warehouse_state.models import *

logg2 = logging.getLogger(f'access-ci.{__name__}')

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
        obj, created = ProcessingStatus.objects.update_or_create(
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

    def FinishActivity(self, Code, Message, PublishedTimestamp=None):
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

        conf = getattr(settings, 'CONF', {}) or {}
        metrics_mode = conf.get('METRICS_MODE', 'DISABLED')
        if metrics_mode == 'ENABLE' and self.model.Topic == 'glue2.applications' and PublishedTimestamp:
            if 'ApplicationEnvironment.New' in Message:
                try:
                    metric = ProcessingMetric(
                        ProcessingID=self.model.ID,
                        ProcessingTimestamp=PublishedTimestamp,
                        ProcessingError=self.model.ProcessingCode,
                        About=self.model.About,
                        MetricName='ApplicationEnvironment',
                        MetricValue=Message['ApplicationEnvironment.New'],
                    )
                    metric.save()
                except (DataError, IntegrityError) as e:
                    msg = 'Exception on ProcessingMetric (MetricName={}, ResourceID={}, Published={}): {}'.format('ApplicationEnvironment', self.model.About, PublishedTimestamp, e)
                    logg2.error(msg)
                    pass
