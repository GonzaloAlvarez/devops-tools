import decimal
import sys
from collections import Mapping, Set, Sequence
from decimal import Decimal
from lib.fmd.tabledef import TableDefinition
from lib.encryption.aespcrypt import AESPCrypt
from lib.cloud.baseaws import BaseAws
from lib.lang.singleton import Singleton

@Singleton
class KeyCache(object):
    _cache = None
    def set(self, elements):
        self._cache = []
        self._cache.extend(elements)

    def invalidate(self):
        self._cache = None

    def get(self, key, get_function):
        if self._cache == None:
            self.set(get_function())
        if key in self._cache:
            return key
        return None

class DynamoDb(BaseAws):
    def __init__(self, configuration, table_definition = TableDefinition()):
        super(DynamoDb, self).__init__(configuration)
        self.dynamodb = self.resource('dynamodb')
        self.table_name = self.resource_name
        self.table_definition = table_definition
        self.cache = KeyCache.instance()
        if self.table_name not in self.dynamodb.meta.client.list_tables()['TableNames']:
            self.table = self._create_table(self.table_name, table_definition.key)
        else:
            self.table = self.dynamodb.Table(self.table_name)

    def _create_table(self, table_name, key_field):
        table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': key_field,
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': key_field,
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5,
                }
            )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        return table

    def _sanitize(self, data):
        """ Sanitizes an object so it can be updated to dynamodb (recursive) """
        if not data and isinstance(data, (basestring, Set)):
            new_data = None  # empty strings/sets are forbidden by dynamodb
        elif isinstance(data, (basestring, bool)):
            new_data = data  # important to handle these one before sequence and int!
        elif isinstance(data, Mapping):
            new_data = {key: self._sanitize(data[key]) for key in data}
        elif isinstance(data, Sequence):
            new_data = [self._sanitize(item) for item in data]
        elif isinstance(data, Set):
            new_data = {self._sanitize(item) for item in data}
        elif isinstance(data, (float, int, long, complex)):
            new_data = Decimal(data)
        else:
            new_data = data
        return new_data

    def _unencode(self, obj):
        if isinstance(obj, list):
            for i in xrange(len(obj)):
                obj[i] = self._unencode(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.iterkeys():
                obj[k] = self._unencode(obj[k])
            return obj
        elif isinstance(obj, decimal.Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj

    def put(self, data):
        self.cache.invalidate()
        return self.table.put_item(Item=self._sanitize(data))

    def list(self, filter_name= None):
        output = []
        filter_expr = None
        if filter_name:
            filter_expr = self.table_definition.filter_exprs[filter_name]
            response = self.table.scan(FilterExpression = filter_expr)
        else:
            response = self.table.scan()

        entries = response['Items']
        while response.get('LastEvaluatedKey'):
            if filter_expr:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression = filter_expr)
            else:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            entries.extend(response['Items'])

        for item in entries:
            output.insert(len(output), self._unencode(item))
        return output

    def remove(self, key):
        self.cache.invalidate()
        self.table.delete_item(Key={self.table_definition.key: key})

    def exists(self, key):
        if self.cache.get(key, lambda: [entry['fid'] for entry in self.list()]):
            return True
        return False

    def get(self, key):
        item_element = self.table.get_item(Key={self.table_definition.key: key})
        if 'Item' in item_element:
            return self._unencode(self.table.get_item(Key={self.table_definition.key: key})['Item'])
        else:
            return None
