from celery.schedules import crontab
from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='company_task')
def company_task(task, pk=None, data=None, user_id=None):
    from django.contrib.auth.models import User
    from core.models.company import Company as Model

    if pk:
        obj = Model.objects.get(pk=pk)
        task_func = getattr(obj, task)
    else:
        obj = '%s' % Model.__name__
        task_func = getattr(Model, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    if user_id:
        user = User.objects.get(id=user_id)
        user.add_notification(
            model=Model,
            obj=obj,
            response=response,
        )

    return response


@app.task(name='invite_task')
def invite_task(task, pk=None, data=None, user_id=None):
    from django.contrib.auth.models import User
    from core.models.invite import Invite as Model

    if pk:
        obj = Model.objects.get(pk=pk)
        task_func = getattr(obj, task)
    else:
        obj = '%s' % Model.__name__
        task_func = getattr(Model, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    if user_id:
        user = User.objects.get(id=user_id)
        user.add_notification(
            model=Model,
            obj=obj,
            response=response,
        )

    return response


@app.task(name='companies_check')
def companies_check():
    from core.models.company import Company
    Company.check_all()


app.add_periodic_task(crontab(minute=0, hour=3), companies_check)
