from celery.schedules import crontab
from celery.utils.log import get_task_logger

from matrix.celery import app


logger = get_task_logger(__name__)


def model_task(model, company_id, task, user_id=None, pk=None, data=None):
    from core.models import Company, User

    if company_id:
        company = Company.objects.get(id=company_id)
    data = data or {}
    user = None

    if user_id:
        user = User.objects.get(id=user_id)
        data['user'] = user

    if pk:
        obj = model.objects.get(pk=pk)
        task_func = getattr(obj, task)
    else:
        obj = '%s' % model.__name__
        task_func = getattr(model, task)

    if callable(task_func):
        logger.info("{0}: running task {1}".format(obj, task))
        response = task_func(**data) if data else task_func()
    else:
        raise Exception("{}: task not callable.".format(task))

    if user:
        user.add_notification(
            company=company,
            model=model,
            obj=obj,
            response=response,
        )

    return response


@app.task(name='company_task')
def company_task(**kwargs):
    from core.models import Company as Model
    return model_task(model=Model, **kwargs)


@app.task(name='invite_task')
def invite_task(**kwargs):
    from core.models import Invite as Model
    return model_task(model=Model, **kwargs)


@app.task(name='link_task')
def link_task(**kwargs):
    from core.models import Link as Model
    return model_task(Model, **kwargs)


@app.task(name='message_task')
def message_task(**kwargs):
    from core.models import Message as Model
    return model_task(Model, **kwargs)


@app.task(name='user_task')
def user_task(**kwargs):
    from core.models import User as Model
    return model_task(model=Model, **kwargs)


@app.task(name='companies_check')
def companies_check():
    from core.models import Company
    Company.check_all()


app.add_periodic_task(crontab(minute=0, hour=3), companies_check)
