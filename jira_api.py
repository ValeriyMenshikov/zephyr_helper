import pprint
import requests
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
        "id": None,
        "projectId": None,
        "name": None,
        "objective": None,
        "precondition": None,
        "owner": None,
        "labels": None,
        "folderId": None,  # TODO ее надо получать с помощью метода
        "statusId": None,  # TODO 1625 automated #733 draft сделать класс с константами
        "priorityId": None,  # TODO Normal  сделать класс с приоритетами
        "testData": None,
        "parameters": None,
        "estimatedTime": None,
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
        self.__folder_id = None

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

        if jql:
            query = jql

        params = (
            ('archived', archived),
            ('fields', fields),
            ('maxResults', max_results),
            ('query', query),
            ('startAt', '0'),
        )
        cases = self.__request.get(f'{self.__url}/rest/tests/1.0/testcase/search', params=params)
        return cases

    def update(self, key: str = '', **fields) -> Response:
        """
        Метод для обновления параметров существующего тесткейса, позволяет найти тест кейс по ключу например
        PVZ-T1 и сразу обновить

        :param key:                         str  -- ключевое слово для поиска тест кейса
        :param componentId:                 int  -- поставить метку существующего компонента
        :param estimatedTime:               int  -- время
        :param id:                          int  -- id тесткейса
        :param labels:                      list -- список меток тесткейса
        :param name:                        str  -- название тесткейса
        :param objective:                   str  -- описание тесткейса
        :param parameters:                  list -- список параметров
        :param precondition:                str  -- исходное состояние
        :param priorityId:                  int  -- id приоритета
        :param projectId:                   int  -- id проекта по умолчанию подтягивается из родительского класса
        :param statusId:                    int  -- id статуса из статус модели
        :param testData:                    list -- список тестовых данных
        :return: Response object
        """

        if fields.get("id") is None:
            try:
                case_id = self.search(fields.get('name', ''), key).json()["results"][0]["id"]
            except KeyError as error:
                raise KeyError("Тест кейс не найден или было найдено более одного!") from error
        else:
            case_id = fields.get("id")

        case = self._fill_case_model(**fields)

        case.setdefault('id', case_id)
        return self.__request.put(f'{self.__url}/rest/tests/1.0/testcase/{case_id}', json=case)

    def create(self, **fields) -> Response:
        """
        Метод для создания тесткейса в проекте
        :param componentId:                 int  -- поставить метку существующего компонента
        :param estimatedTime:               int  -- время
        :param id:                          int  -- id тесткейса
        :param labels:                      list -- список меток тесткейса
        :param name:                        str  -- название тесткейса
        :param objective:                   str  -- описание тесткейса
        :param parameters:                  list -- список параметров
        :param precondition:                str  -- исходное состояние
        :param priorityId:                  int  -- id приоритета
        :param projectId:                   int  -- id проекта по умолчанию подтягивается из родительского класса
        :param statusId:                    int  -- id статуса из статус модели
        :param testData:                    list -- список тестовых данных
        :return: Response object
        """
        case = self._fill_case_model(**fields)
        case["projectId"] = int(self.__project_id) if fields.get("projectId") is None else fields.get("projectId")
        case["folderId"] = self.__folder_id if self.__folder_id is not None else fields["folderId"]
        case["owner"] = self.__login if fields.get("owner") is None else fields.get("owner")
        return self.__request.post(f'{self.__url}/rest/tests/1.0/testcase', json=case)

    def _fill_case_model(self, **fields):
        case = dict()
        for field, value in fields.items():
            for k in self.CASE_MODEL:
                if field == k:
                    case.update({k: value})
        return case


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



