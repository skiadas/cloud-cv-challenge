from boto3 import client

## Manages a dynamodb database

class dbtable:
    @classmethod
    def create(cls, tableName, keyName):
      obj = cls(tableName, keyName)
      obj.dynamodb.create_table(
          TableName=tableName,
          AttributeDefinitions=[
              {'AttributeName': keyName, 'AttributeType': 'S'}],
          KeySchema=[{'AttributeName': keyName, 'KeyType': 'HASH'}],
          BillingMode='PAY_PER_REQUEST')
      return obj

    def __init__(self, tableName, keyName):
        self.dynamodb = client('dynamodb')
        self.tableName = tableName
        self.keyName = keyName

    def get(self, keyValue):
      """Return the value for given key"""
      result = self.dynamodb.get_item(
        TableName=self.tableName,
        Key={ self.keyName: { 'S': keyValue } },
        AttributesToGet=['count'],
        ConsistentRead=True)
      if 'Item' in result:
        # TODO: Ideally we will be allowing other return type values here
        return int(result['Item']['count']['N'])
      else:
        return None

    def increaseCount(self, keyValue):
      self.dynamodb.update_item(
        TableName=self.tableName,
        Key={self.keyName: {'S': keyValue}},
        UpdateExpression='ADD #c :n',
        ExpressionAttributeNames={'#c': 'count'},
        ExpressionAttributeValues={':n': {'N': '1'}})


    def entries_count(self):
      """Returns the total number of entries in the table"""
      result = self.dynamodb.describe_table(TableName=self.tableName)['Table']
      return result['ItemCount']
