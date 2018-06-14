from crmplus.celery import app
from core.tasks import model_task


@app.task(name='user_task')
def user_task(**kwargs):
    from account.models import User as Model
    return model_task(Model, **kwargs)
