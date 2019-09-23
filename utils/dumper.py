# Persistence layer to save all classes into filesystem

import os
import pickle

from os.path import exists
from utils.migration import *

class Dumper:

    def __get_dump_filename(self, cls_or_obj):
        if cls_or_obj == Workload or isinstance(cls_or_obj, Workload):
            return 'source_workload.pickle'
        elif cls_or_obj == MigrationTarget or isinstance(cls_or_obj, MigrationTarget):
            return 'target_migration.pickle'
        elif cls_or_obj == Migration or isinstance(cls_or_obj, Migration):
            return 'migration.pickle'


    def dump(self, migration_obj):
        file_name = self.__get_dump_filename(migration_obj)
        with open(file_name, 'wb') as dump_file:
            pickle.dump(migration_obj, dump_file)


    def read(self, migration_obj):
        file_name = self.__get_dump_filename(migration_obj)

        result = None
        if not exists(file_name):
            return result

        with open(file_name, 'rb') as dump_file:
            result = pickle.load(dump_file)
        return result


    def delete(self, migration_obj):
        file_name = self.__get_dump_filename(migration_obj)
        if exists(file_name):
            os.remove(file_name)
