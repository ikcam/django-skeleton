from celery.utils.log import get_task_logger

from myapp.celery import app


logger = get_task_logger(__name__)


@app.task(name='profile_tasks')
def profile_tasks(pk, task):
    from account.models import Profile

    obj = Profile.objects.get(pk=pk)

    if task == 'key_send':
        logger.info('Key send: %s' % obj)
        if obj.key_send():
            logger.info('Key sended: %s' % obj)
        else:
            logger.error('Key not sended: %s' % obj)
    else:
        logger.warning('Invalid task: %s.' % task)
