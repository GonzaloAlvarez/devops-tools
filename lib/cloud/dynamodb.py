import boto3
import decimal
import sys
import hashlib
from collections import Mapping, Set, Sequence
from decimal import Decimal

class DynamoDb(object):
    def __init__(self, region, access_key, secret_key):
        self.dynamodb = boto3.resource(
                'dynamodb',
                region_name = region,
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key)
        self.table_name = hashlib.sha256(access_key + sys.argv[0]).digest().encode('hex')[0:32]
        if self.table_name not in self.dynamodb.meta.client.list_tables()['TableNames']:
            self.table = self._create_table(self.table_name, 'fid')
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
        return self.table.put_item(Item=self._sanitize(data))

    def list(self):
        output = []
        response = self.table.scan()

        entries = response['Items']
        while response.get('LastEvaluatedKey'):
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            entries.extend(response['Items'])

        for item in entries:
            output.insert(len(output), self._unencode(item))
        return output

    def remove(self, key):
        self.table.delete_item(Key={'fid': key})

    def get(self, key):
        return self._unencode(self.table.get_item(Key={'fid': key})['Item'])
