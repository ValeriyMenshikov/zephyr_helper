from requests import Response
from zephyr_helper.connect import ProjectConnect
from zephyr_helper.utils import logger
from zephyr_helper.models.folder import FOLDER_MODEL


class Folder(ProjectConnect):

    @logger
    def create(self, name: str = None, parent_id: int = None) -> Response:
        """
        Метод для создания новой папки
        :param name: Имя новой папки
        :param parent_id: Идентификатор папки в которой создаем
        :return:
        """
        json = self._fill_model(model=FOLDER_MODEL, name=name, parentId=parent_id)
        return self._session.post(url=f'{self._url}/rest/tests/1.0/folder/testcase', json=json)

    @logger
    def tree(self) -> Response:
        """
        Метод отображает дерево содержимого в проекте
        :return:
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/foldertree/testcase')

    @logger
    def content(self,
                folder_id: int = None,
                fields: str = None,
                jql: str = None,
                max_results: int = 100,
                start_at: int = 0,
                archived: str = 'false') -> Response:
        """
        Метод для отображения содержимого выбранной папки
        :param folder_id: id выбранной папки
        :param fields: поля для отображения
        :param jql: свой jql запрос для фильтрации
        :param max_results: сколько вывести
        :param start_at: сколько пропустить
        :param archived: показывать заархивированные или нет
        :return:
        """
        if fields == 'all':
            fields = str(','.join(self.FIELDS))
        elif fields is None:
            fields = str(','.join(['id', 'key', 'projectId', 'name', 'folderId']))

        query = f'testCase.projectId IN ({self._project_id}) AND testCase.folderTreeId IN ({folder_id}) ORDER BY testCase.id ASC'
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
