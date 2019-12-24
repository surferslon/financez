import xlrd
from django.core.management.base import BaseCommand, CommandError
from financez.models import Account


class Command(BaseCommand):
    help = 'Import accounts from 1c xls'

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs='+', type=str)

    def handle(self, *args, **options):
        file_name = options['file_name']
        wb = xlrd.open_workbook(file_name[0])
        sheet = wb.sheet_by_index(0)
        CODE = 0
        NAME = 1
        TYPE = 2
        PARENT = 3
        for row in range(sheet.nrows):
            new_account = Account(
                code=sheet.cell_value(row, CODE),
                name=sheet.cell_value(row, NAME),
                acc_type='p' if sheet.cell_value(row, TYPE) == 'Пассивный' else 'a'
            )
            new_account.save()
            self.stdout.write(
                '{} {} {}'.format(
                    sheet.cell_value(row, CODE),
                    sheet.cell_value(row, NAME),
                    sheet.cell_value(row, TYPE)
                )
            )

        for row in range(sheet.nrows):
            if not sheet.cell_value(row, PARENT):
                continue
            account = Account.objects.get(code=sheet.cell_value(row, CODE))
            account.parent = Account.objects.get(code=sheet.cell_value(row, PARENT))
            account.save()

        self.stdout.write('Done')
