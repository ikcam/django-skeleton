from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='profile_task')
def profile_task(task, pk=None, data=None, user_id=None):
    from django.contrib.auth.models import User
    from account.models import Profile as Model

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
