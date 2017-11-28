from myapp.celery import app
from core.tasks import model_task


@app.task(name='profile_task')
def profile_task(**kwargs):
    from account.models import Profile as Model
    return model_task(Model, **kwargs)
