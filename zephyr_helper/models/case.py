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
