import time
import random

from zope import interface


class IConnection(interface.Interface):
    def connect(servers=None, timeout=None, discover=True, retryTime=10,
                *args, **kwargs):
        """
        connect to elasticsearch
        """

    def close():
        """
        close all connections to elasticsearch
        """

    def execute(method, path, body=None):
        """
        Perform method on path with optional body
        """


class NoServerAvailable(Exception):
    pass


class ServerList(list):
    def __init__(self, servers, retryTime=10):
        list.__init__(self, servers)
        self.dead = []
        self.retryTime = retryTime

    def get(self):
        if self.dead:
            retryTime, server = self.dead.pop()
            if retryTime > time.time():
                self.dead.append((retryTime, server))
            else:
                self.append(server)
        if not self:
            raise NoServerAvailable()

        return random.choice(self)

    def markDead(self, server):
        self.remove(server)
        self.dead.insert(0, (time.time() + self.retryTime, server))