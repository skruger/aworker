import pickle
import uuid


class TaskInfo(object):
    def __init__(self, task_name, args, kwargs, options, task_id=False):
        self.task_id = task_id or str(uuid.uuid4())
        self.task_name = task_name
        self.args = args
        self.kwargs = kwargs
        self.options = options

    def __eq__(self, other):
        return all([
            self.task_id == other.task_id,
            self.task_name == other.task_name,
            self.args == other.args,
            self.kwargs == other.kwargs,
            self.options == other.options,
        ])


class BaseSerializer(object):
    def __init__(self, **options):
        self.options = options

    def pack(self, task_info, string_encoded=False):
        """
        Package task_name, args, kwargs, and options in a form that can be parsed
        into a TaskInfo object by unpack()

        :param task_info:
        :param string_encoded:
        :return: <bytes> or <string>
        """
        raise NotImplementedError()

    def unpack(self, value):
        """
        Unpack a serialized string or bytes value into a TaskInfo object

        :param value:
        :return: <TaskInfo>
        """
        raise NotImplementedError()


class PickleSerializer(BaseSerializer):
    def pack(self, task_info, string_encoded=False):
        assert not string_encoded
        return pickle.dumps(task_info)

    def unpack(self, value):
        return pickle.loads(value)


