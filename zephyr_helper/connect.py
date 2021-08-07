import requests



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
        """
        self._url = url
        self._project_id = project_id
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._session.auth = (self._login, self._password)
        self._session.headers = ('jira-project-id', self._project_id)

    def _fill_model(self, model, fill_owner=False, **fields) -> dict:
        """
        Вспомогательный метод для заполнения json модели тест кейса
        :param fields: набор **kwargs
        """
        # TODO: Есть баг что если дать название поля которого нет в модели, то просто ничего не произойдет
        case = dict()
        for field, value in fields.items():
            for k, v in model.items():
                if field == k:
                    self._validate_type(field, value, v)
                    case.update({k: value})
                    break
        case["projectId"] = int(self._project_id) if fields.get("projectId") is None else fields.get("projectId")
        if fill_owner:
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


