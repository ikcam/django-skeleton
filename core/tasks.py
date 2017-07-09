from celery.schedules import crontab
from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='company_task')
def company_task(pk, task, data=None):
    from core.models import Company

    obj = Company.objects.get(pk=pk)
    task_func = getattr(obj, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    return response


@app.task(name='invite_task')
def invite_task(pk, task, data=None):
    from core.models import Invite

    obj = Invite.objects.get(pk=pk)
    task_func = getattr(obj, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    return response


@app.task(name='companies_check')
def companies_check():
    from core.models import Company
    Company.check_all()


app.add_periodic_task(crontab(minute=0, hour=3), companies_check)
