# zephyr helper

Small package for using zephyr tms

- Package version: 1.0.0

## Requirements.

Python >= 3.6

## Installation & Usage

### pip install

```sh
pip install zephyr_helper 
```

Then import the package:

```python
import zephyr_helper
```

## Getting Started

```python
from zephyr_helper.client import ZephyrClient

# Create zephyr tms client
tms = ZephyrClient(url='https://jira.com',
                   project_id='123456789',
                   login='user',
                   password='password')

# Create folder in project
new_folder = tms.Folder.create(name='New folder',
                               parent_id=123456789)

# Show folder tree
project_tree = tms.Folder.tree()

# Create test case
test_case = tms.TestCase.create(name='Some check', 
                                folderId=new_folder['id'])

# Get test case status model
test_status = tms.StatusModel.case()

```

## Author

```
Menshikov Valeriy
```