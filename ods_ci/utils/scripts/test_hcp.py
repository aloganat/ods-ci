from clouds.aws.roles.roles import get_roles
from clouds.aws.session_clients import iam_client
import os
client = iam_client()
print (client)
print(os.environ)
# client.list_roles()

