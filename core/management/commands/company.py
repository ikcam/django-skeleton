from django.core.management import BaseCommand, CommandError

from core.models import Company


class Command(BaseCommand):
    help = 'Enable a module for a company'

    def add_arguments(self, parser):
        parser.add_argument(
            'id', type=int, help="Company ID"
        )
        parser.add_argument(
            '-m', '--module', nargs='+', type=str,
            help="Module(s) to activate"
        )
        parser.add_argument(
            '-rm', '--remove', nargs='+', type=str,
            help="Module(s) to remove"
        )

    def handle(self, *args, **options):
        company_id = options['id']
        modules = options['module'] or []
        rmodules = options['remove'] or []

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExists:
            raise CommandError('Company "%s" does not exist' % company_id)

        for module in modules:
            try:
                company.module_add(module, force=True)
                self.stdout.write(
                    self.style.SUCCESS('Module "%s" added for company "%s"' % (
                        module,
                        company.name,
                    ))
                )
            except AssertionError as e:
                raise CommandError(
                    'Company: "%s": %s' % (company.name, e)
                )

        for module in rmodules:
            try:
                company.module_remove(module)
                self.stdout.write(
                    self.style.SUCCESS(
                        'Module "%s" removed for company "%s"' % (
                            module,
                            company.name,
                        )
                    )
                )
            except AssertionError as e:
                raise CommandError(
                    'Company: "%s": %s' % (company.name, e)
                )
