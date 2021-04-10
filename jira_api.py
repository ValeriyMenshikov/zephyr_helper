import pprint
import requests
from requests import Response


class ProjectConnect:
    FIELDS = (
        'id', 'key', 'projectId', 'name', 'averageTime', 'estimatedTime', 'labels', 'folderId', 'componentId',
        'statusId', 'priorityId', 'lastTestResultStatus(name,i18nKey,color)', 'majorVersion', 'createdOn',
        'createdBy', 'updatedOn', 'updatedBy', 'customFieldValues', 'owner'
    )

    def __init__(self, url: str = None, project_id: str = None, login: str = None, password: str = None):
        """
        :param url:                     url адрес Jira
        :param project_id:              id проекта с тест кейсами
        :param login:                   jira логин
        :param password:                jira пароль
        :param password:                jira пароль
        """
        self._url = url
        self._project_id = project_id
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._session.auth = (self._login, self._password)
        self._session.headers = ('jira-project-id', self._project_id)


class Case(ProjectConnect):
    TEST_SCRIPT_MODEL = {  # TODO определиться надо нам это или нет
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

    CASE_MODEL = {
        "id": int(),
        "projectId": int(),
        "name": str(),
        "objective": str(),
        "precondition": str(),
        "owner": str(),
        "labels": list(),
        "folderId": int(),  # TODO ее надо получать с помощью метода
        "statusId": int(),
        "priorityId": int(),
        "testData": list(),
        "parameters": list(),
        "estimatedTime": int(),
        "testScript": TEST_SCRIPT_MODEL
    }

    def search(self,
               name: str = '',
               key: str = '',
               fields: str = None,
               jql: str = None,
               max_results: int = 40,
               start_at: int = 0,
               archived: str = 'false') -> Response:
        r"""
        Args:
            name:   перечисление полей которые необходимо получить
            key:    перечисление полей которые необходимо получить
            fields: перечисление полей которые необходимо получить
                 id, key, projectId, name, averageTime, estimatedTime, labels,
                 folderId, componentId, statusId, priorityId, lastTestResultStatus(name,i18nKey,color),
                 majorVersion, createdOn, createdBy, updatedOn, updatedBy, customFieldValues, owner
            jql: можно написать свой запрос в jira для поиска
            max_results: количество строк для вывода
            start_at: с какого номера начать отображать результат(для пагинации)
            archived: можно написать свой запрос в jira для поиска
        """

        if fields == 'all':
            fields = str(','.join(self.FIELDS))
        elif fields is None:
            fields = str(','.join(['id', 'key', 'projectId', 'name', 'folderId']))

        query = f'testCase.projectId IN ({self._project_id}) '
        query = query + f'AND testCase.key = "{key}"' if key else query
        query = query + f'AND testCase.name = "{name}"' if name else query

        if jql:
            query = jql

        params = (
            ('archived', archived),
            ('fields', fields),
            ('maxResults', max_results),
            ('query', query),
            ('startAt', start_at),
        )
        cases = self._session.get(f'{self._url}/rest/tests/1.0/testcase/search', params=params)
        return cases

    def update(self, id=None, key: str = '', **fields) -> Response:
        """
        Метод для обновления параметнов тест-кейса\n

        Keyword Args:
            id:            required[int]
            key:           Optional[int]
            componentId:   Optional[int]
            estimatedTime: Optional[int]
            labels:        Optional[list]
            name:          Optional[str]
            objective:     Optional[str]
            parameters:    Optional[list]
            precondition:  Optional[str]
            priorityId:    Optional[int]
            projectId:     Optional[int]
            statusId:      Optional[int]
            testData:      Optional[list]
        """

        if not id and key:
            try:
                case_id = self.search(fields.get('name', ''), key).json()["results"][0]["id"]
            except KeyError as error:
                raise KeyError("Тест кейс не найден или было найдено более одного!") from error
        elif id:
            case_id = id
        else:
            raise KeyError("id или Key должны быть указаны обязательно!")

        case = self._fill_case_model(id=case_id, **fields)
        case.setdefault('id', case_id)
        response = self._session.put(f'{self._url}/rest/tests/1.0/testcase/{case_id}', json=case)
        pprint.pprint(response.request.body)
        pprint.pprint(response.request.url)

        return response

    def create(self, name, folderId, **fields) -> Response:
        """
        Метод для создания тест-кейса\n

        Keyword Args:
            name:           Required[str]
            folderId:       Required[int]
            componentId:    Optional[int]
            estimatedTime:  Optional[int]
            labels:         Optional[list]
            objective:      Optional[str]
            precondition:   Optional[str]
            priorityId:     Optional[int]
            projectId:      Optional[int]
            statusId:       Optional[int]
            testData:       Optional[list]
        """
        case = self._fill_case_model(name=name, folderId=folderId, **fields)
        # case["folderId"] = self.__folder_id if self.__folder_id is not None else fields["folderId"]
        return self._session.post(f'{self._url}/rest/tests/1.0/testcase', json=case)

    def _fill_case_model(self, **fields) -> dict:
        """
        Вспомогательный метод для заполнения json модели тест кейса
        :param fields: набор **kwargs
        """
        case = dict()
        for field, value in fields.items():
            for k, v in self.CASE_MODEL.items():
                if field == k:
                    self._validate_type(field, value, v)
                    case.update({k: value})
                    break
        case["projectId"] = int(self._project_id) if fields.get("projectId") is None else fields.get("projectId")
        case["owner"] = self._login if fields.get("owner") is None else fields.get("owner")
        return case

    @staticmethod
    def _validate_type(field, val1=None, val2=None):
        value1_type, value2_type = None, None
        for obj_type in [dict, int, list, str, tuple, set]:
            if isinstance(val1, obj_type):
                value1_type = obj_type
            if isinstance(val2, obj_type):
                value2_type = obj_type
        if not value1_type == value2_type:
            raise TypeError(f"Поле <{field}> должно иметь тип {value2_type}")


class Folder(ProjectConnect):
    def create(self, name) -> Response:
        json = {
            "index": 1,
            "name": name,
            "projectId": int(self._project_id)
        }
        return self._session.post(url=f'{self._url}/rest/tests/1.0/folder/testcase', json=json)

    def sub_folder_create(self, name, parent_id=5650) -> Response:
        json = {
            "index": 3,
            "name": name,
            "projectId": int(self._project_id),
            "parentId": parent_id}

        return self._session.post(f'{self._url}/rest/tests/1.0/folder/testcase', json=json)

    def tree(self) -> Response:
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/foldertree/testcase')

    def content(self) -> Response:
        params = (
            ('archived', 'false'),
            # ('fields', 'id,key,projectId,name,averageTime,estimatedTime,labels,folderId,componentId,statusId,priorityId,lastTestResultStatus(name,i18nKey,color),majorVersion,createdOn,createdBy,updatedOn,updatedBy,customFieldValues,owner'),
            ('maxResults', '100'),
            ('query',
             f'testCase.projectId IN ({self._project_id}) AND testCase.folderTreeId IN (27803) ORDER BY testCase.id ASC'),
            ('sort', 'id:asc'),
            ('startAt', '0'),
        )
        return self._session.get(f'{self._url}/rest/tests/1.0/testcase/search', params=params)


class StatusModel(ProjectConnect):
    def case(self) -> Response:
        """
        Метод получения возможных статусов тесткейсов
        :return: Response object
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/testcasestatus')

    def result(self) -> Response:
        """
        Метод получения возможных статусов прохождения тесткейсов
        :return: Response object
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/testresultstatus')

    def priority(self) -> Response:
        """
        Метод получения приоритетов тесткейсов
        :return: Response object
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/testcasepriority')


class ZephyrClient:
    def __init__(self, **kwargs):
        """
        Класс для связки объектов в один\n
        Keyword Args:
            url: [str]
            project_id: [str]
            login: [str]
            password: [str]

        Returns: object
        """
        self.TestCase = Case(**kwargs)
        self.Folder = Folder(**kwargs)
        self.StatusModel = StatusModel(**kwargs)
