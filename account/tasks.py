from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='profile_task')
def profile_task(task, pk=None, data=None):
    from account.models import Profile

    if pk:
        obj = Profile.objects.get(pk=pk)
        task_func = getattr(obj, task)
    else:
        obj = '%s' % Profile.__name__
        task_func = getattr(Profile, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    return response
