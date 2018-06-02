from myapp.celery import app
from core.tasks import model_task


@app.task(name='profile_task')
def user_task(**kwargs):
    from account.models import User as Model
    return model_task(Model, **kwargs)
