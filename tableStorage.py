from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
import config

"""
def tableStorage function creates an entity in Azure Table Storage to record analytics of the HinScraper Application

:param str table_name: name of the azure table
:param str partition_key: (year)(YYYY) unique id
:param str row_key: (month-day)(MM-DD) unique id
:param int hins_processed: number of hins processed in a given session
:param float time_by_system: time it took the system to complete the request
:param float time_by_user: time it would have taken the user to complete the request
:param int requests: (default = 1) increments the request value

"""

def tableStorage(table_name, partition_key, row_key, hins_processed, timesaved, time_by_system, time_by_user, requests):

    try: 
        table_service = TableService(account_name=config.AZURE['STORAGE_ACCOUNT_NAME'], account_key=config.AZURE['STORAGE_ACCOUNT_KEY'])

        entity = {'PartitionKey': partition_key, 'RowKey': row_key,
            'HinsProcessed': hins_processed, 'TimeSaved': timesaved, 
            'TimeBySystem': time_by_system, 'TimeByUser': time_by_user,
            'Requests': requests}

        if not table_service.exists(table_name, timeout=None):
            table_service.create_table(table_name, fail_on_exist=False)
        
        try:
            table_service.insert_entity(table_name, entity)
            print("Entity Doesn't Exist")
            print("Creating Entity\n")
        except Exception as e:
            print("Entity Exists")
            print("Updating entity\n")

            currentEntity = table_service.get_entity(table_name, partition_key, row_key)
            tempHinProcessed = currentEntity.HinsProcessed + hins_processed
            tempTimeSaved = currentEntity.TimeSaved + timesaved
            tempTimeBySystem = currentEntity.TimeBySystem + time_by_system
            tempTimeByUser = currentEntity.TimeByUser + time_by_user
            tempRequest = currentEntity.Requests + requests

            entity = {'PartitionKey': partition_key, 'RowKey': row_key,
            'HinsProcessed': tempHinProcessed, 'TimeSaved': tempTimeSaved, 
            'TimeBySystem': tempTimeBySystem, 'TimeByUser': tempTimeByUser,
            'Requests': tempRequest}

            table_service.update_entity(table_name, entity, if_match='*', timeout=None)

    except Exception as e:
        print(e)