from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='link_task')
def link_task(task, pk=None, data=None):
    from common.models.link import Link

    if pk:
        obj = Link.objects.get(pk=pk)
        task_func = getattr(obj, task)
    else:
        obj = '%s' % Link.__name__
        task_func = getattr(Link, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    return response


@app.task(name='message_task')
def message_task(task, pk=None, data=None):
    from common.models.message import Message

    if pk:
        obj = Message.objects.get(pk=pk)
        task_func = getattr(obj, task)
    else:
        obj = '%s' % Message.__name__
        task_func = getattr(Message, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    return response
