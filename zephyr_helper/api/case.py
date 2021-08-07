from requests import Response
from zephyr_helper.connect import ProjectConnect
from zephyr_helper.utils import logger
from zephyr_helper.models.case import TEST_SCRIPT_MODEL, CASE_MODEL


class Case(ProjectConnect):
    @logger
    def search(self,
               name: str = '',
               key: str = '',
               folder_id=None,
               fields: str = None,
               jql: str = None,
               max_results: int = 40,
               start_at: int = 0,
               archived: str = 'false') -> Response:
        r"""
        Args:
            name:   имя тест-кейса
            key:    номер тест кейса, например PVZ-T1
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
        query = query + f'AND testCase.key = "{key}" ' if key else query
        query = query + f'AND testCase.name = "{name}"' if name else query
        query = query + f'AND testCase.folderTreeId = {folder_id}' if folder_id else query

        if jql:
            query = jql

        params = (
            ('archived', archived),
            ('fields', fields),
            ('maxResults', max_results),
            ('query', query),
            ('startAt', start_at),
        )
        return self._session.get(f'{self._url}/rest/tests/1.0/testcase/search', params=params)

    @logger
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
                case_id = self.search(key=key).json()["results"][0]["id"]
            except KeyError as error:
                raise KeyError("Тест кейс не найден или было найдено более одного!") from error
        elif id:
            case_id = id
        else:
            raise KeyError("id или Key должны быть указаны обязательно!")

        case = self._fill_model(model=CASE_MODEL, fill_owner=True, id=case_id, **fields)
        case.setdefault('id', case_id)
        return self._session.put(f'{self._url}/rest/tests/1.0/testcase/{case_id}', json=case)

    @logger
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
        case = self._fill_model(model=CASE_MODEL, fill_owner=True, name=name, folderId=folderId, **fields)
        return self._session.post(f'{self._url}/rest/tests/1.0/testcase', json=case)
