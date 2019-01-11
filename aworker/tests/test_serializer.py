from unittest import TestCase

from aworker.serializers import TaskInfo, PickleSerializer


class SerializerTestCase(TestCase):
    def test_pickle(self):
        ps = PickleSerializer()

        task_name = 'test_task_name',
        args = (1, 2, 3)
        kwargs = dict(key='value')
        options = dict(optional='string')
        sent_task_info = TaskInfo(task_name, args, kwargs, options)
        packed = ps.pack(sent_task_info)

        task_info = ps.unpack(packed)
        self.assertEqual(sent_task_info.task_id, task_info.task_id)
        self.assertIsInstance(task_info, TaskInfo)
        self.assertEqual(task_info.task_name, task_name)
        self.assertEqual(task_info.args, args)
        self.assertEqual(task_info.kwargs, kwargs)
        self.assertEqual(task_info.options, options)
