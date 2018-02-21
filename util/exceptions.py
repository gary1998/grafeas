'''
Created on Sep 13, 2017

@author: alberto
'''


class AlreadyExistsError(Exception):
    def __init__(self, resource):
        super().__init__("Already exists: {}".format(resource))
        self.resource = resource


class NotFoundError(Exception):
    def __init__(self, resource):
        super().__init__("Not found: {}".format(resource))
        self.resource = resource


class UnauthorizedError(Exception):
    def __init__(self, resource):
        super().__init__("Unauthorized: {}".format(resource))
        self.resource = resource