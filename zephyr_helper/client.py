from zephyr_helper.api.case import Case
from zephyr_helper.api.folder import Folder
from zephyr_helper.api.status_model import StatusModel
from copy import deepcopy


class ZephyrClient:
    def __init__(self, url: str, project_id: str, login: str, password: str):
        self.url = url
        self.project_id = project_id
        self.login = login
        self.password = password

        options = deepcopy(self.__dict__)

        self.TestCase = Case(**options)
        self.Folder = Folder(**options)
        self.StatusModel = StatusModel(**options)