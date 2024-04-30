# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import time

import pymongo
import logging
import copy
from pathlib import Path
from uuid import uuid4
from urllib.parse import quote_plus
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymysql.cursors import DictCursor
from twisted.enterprise import adbapi
from scrapy.exceptions import DropItem

#from crawlab import save_item
#from crawlab.config import get_task_id
#from crawlab.entity.result import Result

def get_shot_uuid(n=63):
    def numberToBase(n, b):
        if n == 0:
            return [0]
        digits = []
        while n:
            digits.append(int(n % b))
            n //= b
        return digits[::-1]

    # urlsafe_66_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-.~'
    file_name_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'
    if n > len(file_name_alphabet):
        n = len(file_name_alphabet)
    return ''.join(file_name_alphabet[x] for x in numberToBase(uuid4().int, n))


class MysqlScrapyPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
          	port=13306,
            charset='utf8mb4',
            cursorclass=DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.save_data_2_db, item)
        query.addErrback(self.handle_error, item, spider)
        #result = Result(item)
        #result.set_task_id(get_task_id())
        #save_item(result)
        return item

    def handle_error(self, failure, item, spider):
        print(failure)

    def save_data_2_db(self, cursor, item):
        adapter = ItemAdapter(item)
        adapter = adapter.asdict()
        metadata = adapter.pop('metadata', {})
        table_name = item.get_table_name()
        unique = item.get_unique_fields()
        dbcall_func = getattr(item, 'get_express_sql', None)
        if item.get('operator_name') == 'Uniting Account':
            a = 1
        if dbcall_func:
            sql_str, params = dbcall_func()
            cursor.execute(sql_str, params)
        else:
            # 判断记录是否存在如果存在则更新
            unique_list = []
            for field in unique:
                val = item.get(field)
                if val is None:
                    condition = f'%s = NULL' % field
                else:
                    condition = f'%s = "%s"' % (field, item.get(field))
                unique_list.append(condition)
            where_cluse = 'WHERE ' + ' AND '.join(unique_list)
            select_cluse = f'SELECT * FROM {table_name}'
            sql_str = f'{select_cluse} {where_cluse};'
            records = self.do_get(cursor, sql_str)
            if records:
                if metadata.get('update', True):
                    # 如果存在执行更新
                    update_list = []
                    for key, val in adapter.items():
                        if key in unique:
                            continue
                        else:
                            if val is None:
                                update_list.append(f'%s = NULL' % key)
                            else:
                                if isinstance(val, str) and '"' in str(val):
                                    val = val.replace('\"', '""')
                                update_list.append(f'%s = "%s"' % (key, val))
                    update_cluse = f'UPDATE {table_name}'
                    set_cluse = 'SET %s' % ','.join(update_list)
                    sql_str = f'{update_cluse} {set_cluse} {where_cluse}'
                    # print(sql_str)
                    cursor.execute(sql_str)
                else:
                    duplicates = []
                    for field in unique:
                        duplicates.append(f'{field}<{item.get(field)}>')
                    raise DropItem("Duplicate item found: %s" % ','.join(duplicates))
            else:
                # 不存在执行插入
                column_list = []
                values_list = []
                for key, val in adapter.items():
                    column_list.append(key)
                    if val is None:
                        values_list.append('NULL')
                    else:
                        if isinstance(val, str) and '"' in str(val):
                            val = val.replace('\"', '""')
                        values_list.append(val)
                sql_str = f"INSERT INTO {table_name} " + '(%s) ' % ','.join(
                    ["%s"] * len(column_list)) + 'VALUES (%s);' % ','.join(['"%s"'] * len(column_list))
                sql_str = sql_str % tuple(column_list + values_list)
                sql_str = sql_str.replace('"NULL"', 'NULL')
                # print(sql_str)
                cursor.execute(sql_str)

    def do_get(self, cursor, sql_string):
        cursor.execute(sql_string)
        return cursor.fetchall()


class MongodbPipline(object):
    def __init__(self, client, db_name):
        self.db = client[db_name]

    @classmethod
    def from_settings(cls, settings):
        uri = "mongodb://%s:%s@%s:%s" % (
            quote_plus(settings["MONGODB_USER"]), quote_plus(settings["MONGODB_PASSWORD"]), settings["MONGODB_HOST"],
            settings["MONGODB_PORT"])

        client = pymongo.MongoClient(uri)
        return cls(client, settings["MONGODB_DBNAME"])

    def process_item(self, item, spider):
        self.save_data(item, spider)
        return item

    def save_data(self, item, spider):
        table_name = item.get_table_name()
        unique = item.get_unique_fields()
        item = ItemAdapter(item).asdict()
        metadata = item.pop('metadata', {})
        update_dict = copy.deepcopy(item)
        collection = self.db[table_name]
        unique_dict = {}
        for field in unique:
            unique_dict[field] = update_dict.pop(field)
        if collection.find_one(unique_dict):
            # 存在 更新
            if metadata.get('update', True):
                collection.update_one(unique_dict, {"$set": update_dict})
            else:
                duplicates = []
                for field in unique:
                    duplicates.append(f'{field}<{item.get(field)}>')
                logging.exception("Duplicate item found: %s" % ','.join(duplicates))
        else:
            # 插入
            collection.insert_one(item)


class FieldsPipline(object):

    def process_item(self, item, spider):
        fields_saved = item.get_save_fields()
        path_dir = f'media/{spider.name}/fields'
        file_name = f"{get_shot_uuid()}_{str(time.time()).replace('.', '')}.json"
        if not fields_saved:
            return item
        path = Path(__file__).parent / path_dir
        if not path.exists():
            os.makedirs(path, exist_ok=True)
        item_dict = {}
        for field in fields_saved:
            val = item.get(field)
            if val:
                item_dict[field] = val
                item[field] = f'{path_dir}/{file_name}'
        if not item_dict:
            return item
        with open(path / file_name, 'w') as f:
            json.dump(item_dict, f)
        return item
