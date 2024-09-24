#
# encoding: utf-8

import logging
import json
from tablib import Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Import:
    @staticmethod
    def import_from_json(request, resource=None, sfile=None):
        try:
            return json.load(sfile)
        except Exception as e:
            logger.error(f"Import::JSON import error {e}")
        return []


    @staticmethod
    def import_from_csv(request, resource, sfile=None):
        try:
            if sfile:
                rsrce = resource()
                dataset = Dataset()
                imported_data = dataset.load(sfile.read().decode(), format='csv')
                keys = []
                for f in rsrce.get_fields():
                    keys.append(f.column_name)
                r = []
                for row in imported_data:
                    d = {}
                    for i, v in enumerate(row):
                        k = keys[i]
                        d[k] = v
                    r.append(d)
                return r
        except Exception as e:
            logger.error(f"Import::CSV import error {e}")
        return []

