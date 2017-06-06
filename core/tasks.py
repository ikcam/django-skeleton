from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='invite_tasks')
def invite_task(pk, task, data=None):
    from core.models import Invite

    obj = Invite.objects.get(pk=pk)
    task_func = getattr(obj, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    return response
