from requests import Response
from zephyr_helper.connect import ProjectConnect
from zephyr_helper.utils import logger


class StatusModel(ProjectConnect):
    @logger
    def case(self) -> Response:
        """
        Метод получения возможных статусов тесткейсов
        :return: Response object
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/testcasestatus')

    @logger
    def result(self) -> Response:
        """
        Метод получения возможных статусов прохождения тесткейсов
        :return: Response object
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/testresultstatus')

    @logger
    def priority(self) -> Response:
        """
        Метод получения приоритетов тесткейсов
        :return: Response object
        """
        return self._session.get(f'{self._url}/rest/tests/1.0/project/{self._project_id}/testcasepriority')