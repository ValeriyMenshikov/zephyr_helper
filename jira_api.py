import pprint
import requests
import copy
from requests import Response



class ZephyrJira:
    def __init__(self, url: str, project_id: str, login: str, password: str):
        self.url = url
        self.project_id = project_id
        self.login = login
        self.password = password
        self._session = requests.Session()
        self._session.auth = (self.login, self.password)
        self._session.headers = {'jira-project-id': self.project_id}
        self.TestCase = Case(self)
        self.Folder = Folder(self)
        self.Status = StatusModel(self)


class Case:
    CASE_MODEL = {
        "projectId": None,
        "name": None,
        "objective": None,
        "precondition": None,
        "owner": None,
        "folderId": None,  # TODO ее надо получать с помощью метода
        "statusId": None,  # TODO 1625 automated #733 draft сделать класс с константами
        "priorityId": None,  # TODO Normal  сделать класс с приоритетами
        "testScript": {
            "stepByStepScript": {
                "steps": [
                    {
                        "index": 0,
                        "description": "",
                        "expectedResult": "",
                        "customFieldValueIndex": {},
                        "customFieldValues": []
                    }
                ]
            }
        }
    }

    def __init__(self, zephyr):
        self.__url = zephyr.url
        self.__request = zephyr._session
        self.__project_id = zephyr.project_id
        self.__login = zephyr.login

    def search(self,
               name: str = '',
               key: str = '',
               fields: str = None,
               jql: str = None,
               max_results: str = '40',
               archived: str = 'false') -> Response:
        """
        :param fields: перечисление полей которые необходимо получить
         id, key, projectId, name, averageTime, estimatedTime, labels,
         folderId, componentId, statusId, priorityId, lastTestResultStatus(name,i18nKey,color),
         majorVersion, createdOn, createdBy, updatedOn, updatedBy, customFieldValues, owner
        :param jql: можно написать свой запрос в jira для поиска
        :return:
        """
        all_fields = (
            'id', 'key', 'projectId', 'name', 'averageTime', 'estimatedTime', 'labels', 'folderId', 'componentId',
            'statusId', 'priorityId', 'lastTestResultStatus(name,i18nKey,color)', 'majorVersion', 'createdOn',
            'createdBy', 'updatedOn', 'updatedBy', 'customFieldValues', 'owner')

        if fields == 'all':
            fields = str(','.join(all_fields))
        elif fields is None:
            fields = str(','.join(['id', 'key', 'projectId', 'name', 'folderId']))

        query = f'testCase.projectId IN ({self.__project_id}) '
        query = query + f'AND testCase.key = "{key}"' if key else query
        query = query + f'AND testCase.name = "{name}"' if name else query

        params = (
            ('archived', archived),
            ('fields', fields),
            ('maxResults', max_results),
            ('query', query),
            ('startAt', '0'),
        )
        cases = self.__request.get(f'{self.__url}/rest/tests/1.0/testcase/search', params=params)
        return cases

    def update(self, case_id: int = None, name: str = '', key: str = '') -> Response:
        if case_id is None:
            try:
                case_id = self.search(name, key).json()["results"][0]["id"]
            except KeyError as error:
                raise KeyError("Тест кейс не найден!") from error

        json = {
            "id": 21828,
            "projectId": int(self.__project_id),
            "name": "asdasdsd",
            "testData": [],
            "parameters": []}
        return self.__request.put(f'{self.__url}/rest/tests/1.0/testcase/{case_id}', json=json)

    # def create(self, name=None, objective=None, precondition=None, owner=None) -> Response:
    #     case = copy.deepcopy(self.CASE_MODEL)
    #     json = {
    #         "projectId": int(self.__project_id),
    #         "name": name,
    #         "objective": objective,
    #         "precondition": precondition,
    #         "owner": self.__login,
    #         "folderId": 5650,  # TODO ее надо получать с помощью метода
    #         "statusId": 1625,  # TODO 1625 automated #733 draft сделать класс с константами
    #         "priorityId": 1402,  # TODO Normal  сделать класс с приоритетами
    #         "testScript": {
    #             "stepByStepScript": {
    #                 "steps": [
    #                     {
    #                         "index": 0,
    #                         "description": "",
    #                         "expectedResult": "",
    #                         "customFieldValueIndex": {},
    #                         "customFieldValues": []
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    #     return self.__request.post(f'{self.__url}/rest/tests/1.0/testcase', json=json)

    def create(self, name=None, objective=None, precondition=None, owner=None) -> Response:
        case = copy.deepcopy(self.CASE_MODEL)
        json = {
            "projectId": int(self.__project_id),
            "name": name,
            "objective": objective,
            "precondition": precondition,
            "owner": self.__login,
            "folderId": 5650,  # TODO ее надо получать с помощью метода
            "statusId": 1625,  # TODO 1625 automated #733 draft сделать класс с константами
            "priorityId": 1402,  # TODO Normal  сделать класс с приоритетами
            "testScript": {
                "stepByStepScript": {
                    "steps": [
                        {
                            "index": 0,
                            "description": "",
                            "expectedResult": "",
                            "customFieldValueIndex": {},
                            "customFieldValues": []
                        }
                    ]
                }
            }
        }
        return self.__request.post(f'{self.__url}/rest/tests/1.0/testcase', json=json)

class Folder:
    def __init__(self, zephyr):
        self.__url = zephyr.url
        self.__request = zephyr._session
        self.__project_id = zephyr.project_id

    def create(self, name) -> Response:
        json = {
            "index": 1,
            "name": name,
            "projectId": int(self.__project_id)
        }
        return self.__request.post(url=f'{self.__url}/rest/tests/1.0/folder/testcase', json=json)

    def sub_folder_create(self, name, parent_id=5650) -> Response:
        json = {
            "index": 3,
            "name": name,
            "projectId": int(self.__project_id),
            "parentId": parent_id}

        return self.__request.post(f'{self.__url}/rest/tests/1.0/folder/testcase', json=json)

    def tree(self) -> Response:
        return self.__request.get(f'{self.__url}/rest/tests/1.0/project/17109/foldertree/testcase')

    def content(self) -> Response:
        params = (
            ('archived', 'false'),
            # ('fields', 'id,key,projectId,name,averageTime,estimatedTime,labels,folderId,componentId,statusId,priorityId,lastTestResultStatus(name,i18nKey,color),majorVersion,createdOn,createdBy,updatedOn,updatedBy,customFieldValues,owner'),
            ('maxResults', '100'),
            ('query',
             f'testCase.projectId IN ({self.__project_id}) AND testCase.folderTreeId IN (27803) ORDER BY testCase.id ASC'),
            ('sort', 'id:asc'),
            ('startAt', '0'),
        )
        return self.__request.get(f'{self.__url}/rest/tests/1.0/testcase/search', params=params)


class StatusModel:
    def __init__(self, zephyr):
        self.__url = zephyr.url
        self.__request = zephyr._session
        self.__project_id = zephyr.project_id

    def case(self) -> Response:
        return self.__request.get(f'{self.__url}/rest/tests/1.0/project/{self.__project_id}/testcasestatus')

    def result(self) -> Response:
        return self.__request.get(f'{self.__url}/rest/tests/1.0/project/{self.__project_id}/testresultstatus')

    def priority(self) -> Response:
        return self.__request.get(f'{self.__url}/rest/tests/1.0/project/{self.__project_id}/testcasepriority')



