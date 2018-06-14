from crmplus.celery import app
from core.tasks import model_task


@app.task(name='link_task')
def link_task(**kwargs):
    from common.models import Link as Model
    return model_task(Model, **kwargs)


@app.task(name='message_task')
def message_task(**kwargs):
    from common.models import Message as Model
    return model_task(Model, **kwargs)
