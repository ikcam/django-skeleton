import traceback

from django.core.mail import mail_admins

from celery.schedules import crontab
from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


def model_task(
    model, company_id, task, user_request_id=None, pk=None, data=None
):
    from core.models import Company, User

    if company_id:
        company = Company.objects.get(id=company_id)
    else:
        company = None
    data = data or {}

    if not isinstance(data, dict):
        raise Exception("Data is not a dict {}".format(data))

    data['company'] = company
    user_request = None

    if user_request_id:
        user_request = User.objects.get(id=user_request_id)
        data['user_request'] = user_request

    if pk:
        obj = model.objects.get(pk=pk)
        entity = obj
        task_func = getattr(obj, task)
    else:
        obj = '%s' % model.__name__
        entity = model

    for mod in task.split('.'):
        entity = getattr(entity, mod)

    if not callable(entity):
        raise Exception("{}: task not callable.".format(task))

    try:
        logger.info("{0}: running task {1}".format(obj, task))
        response = entity(**data) if data else entity()
    except Exception as err:
        mail_admins(
            'Celery Error',
            '''
Information:
- Model: {model}
- Company: {company}
- Task: {task}
- User request: {user_request}
- PK: {pk}
- Data: {data}
- Exception message:{err}

Traceback:
{traceback}
            '''.format(
                model=model.__name__,
                company=company,
                task=task,
                user_request=user_request,
                pk=pk,
                data=data,
                err=err,
                traceback=traceback.format_exc(),
            )
        )
        raise

    if isinstance(response, list):
        for item in response:
            user_request.add_notification(
                company=company,
                model=model,
                obj=obj,
                response=item,
            )
    else:
        if user_request:
            user_request.add_notification(
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


@app.task(name='check_company')
def check_company():
    from core.models import Company
    Company.check_all()


@app.task(name='check_event')
def check_event():
    from core.models import Event
    Event.check_all()


app.add_periodic_task(
    crontab(day_of_week='*', hour='7', minute='0'),
    check_company
)
app.add_periodic_task(crontab(minute='*/5'), check_event)
