import xlrd
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from financez.models import Account, Entry, Currency


class Command(BaseCommand):
    help = 'Import accounts from 1c xls'

    def add_arguments(self, parser):
        parser.add_argument('file_name', nargs='+', type=str)

    def handle(self, *args, **options):
        file_name = options['file_name']
        wb = xlrd.open_workbook(file_name[0])
        sheet = wb.sheet_by_index(0)
        DATE = 0
        DR = 1
        CR = 2
        TOTAL = 3
        COMMENT = 4
        for row in range(sheet.nrows):
            self.stdout.write(
                '{} {} {} {}'.format(
                    sheet.cell_value(row, DR),
                    sheet.cell_value(row, CR),
                    sheet.cell_value(row, TOTAL),
                    sheet.cell_value(row, COMMENT)
                )
            )
            new_entry = Entry(
                date=datetime.strptime(sheet.cell_value(row, DATE), '%d.%m.%y'),
                acc_dr=Account.objects.get(code=sheet.cell_value(row, DR)),
                acc_cr=Account.objects.get(code=sheet.cell_value(row, CR)),
                total=sheet.cell_value(row, TOTAL).replace(',', '.'),
                currency=Currency.objects.get(name='rub'),
                comment=sheet.cell_value(row, COMMENT)
            )
            new_entry.save()

        self.stdout.write('Done')
