'''
Created on 22 janv. 2023

@author: denis
'''
import datetime, os
import zipfile
from io import BytesIO
import xhtml2pdf.pisa as pisa

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings


def media_resources(uri, rel):  # @UnusedVariable
    return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))


class Render:
    @staticmethod
    def render(path, params, mode='inline', filename='pdf'):
        html  = render_to_string(path, params)
        #template = get_template(path)
        #html = template.render(params)
        content = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), dest=content, link_callback=media_resources)
        if not pdf.err:
            response = HttpResponse(content.getvalue(), content_type='application/pdf;')
            response['Content-Disposition'] = '%s; filename=%s-%s.pdf' % (mode, filename, int(datetime.datetime.now().timestamp()), )
            response['Content-Transfer-Encoding'] = 'binary'
            return response
        else:
            return HttpResponse("Error Rendering PDF", status=400)


class Export:
    """
    mode in ('inline', 'attachment')
    """
    @staticmethod
    def export_to_csv(resource, queryset=None, mode='attachment', filename='csvfile'):
        try:
            rsrce = resource()
            dataset = rsrce.export(queryset)
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = '%s; filename="%s-%s.csv"' %(mode, filename, int(datetime.datetime.now().timestamp()), )
            return response
        except Exception as e:
            return HttpResponse("CSV export error %s" % str(e), status=400)


    @staticmethod
    def export_to_json(resource, queryset=None, mode='attachment', filename='jsonfile'):
        try:
            rsrce = resource()
            dataset = rsrce.export(queryset)
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = '%s; filename="%s-%s.json"' %(mode, filename, int(datetime.datetime.now().timestamp()), )
            return response
        except Exception as e:
            return HttpResponse("JSON export error %s" % str(e), status=400)


    @staticmethod
    def export_to_xls(resource, queryset=None, mode='attachment', filename='xlsfile'):
        try:
            rsrce = resource()
            dataset = rsrce.export(queryset)
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = '%s; filename="%s-%s.xls"' %(mode, filename, int(datetime.datetime.now().timestamp()), )
            return response
        except Exception as e:
            return HttpResponse("XLS export error %s" % str(e), status=400)



    @staticmethod
    def export_zipfile(pathname, files, mode='attachment', filename='zipfile'):
        try:
            zip_io = BytesIO()
            with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                for zfile in files:
                    zip_file.write(os.path.join(pathname, zfile), arcname=zfile)

            response = HttpResponse(zip_io.getvalue())
            response['Content-Disposition'] = f'{mode}; filename="{filename}_{int(datetime.datetime.now().timestamp())}.zip"'
            response['Content-Type'] = 'application/x-zip-compressed'
            response['Content-Length'] = zip_io.tell()
            return response
        except Exception as e:
            return HttpResponse("ZIP file export error %s" % str(e), status=400)


