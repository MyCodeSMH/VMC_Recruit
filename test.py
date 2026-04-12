from utils.vector_db_utils import VectorDB
from utils.s3_utils import S3
from utils.ddb_utils import DDB


def getStatus():
    print("PineCone:\n")
    vdb=VectorDB()
    vdb.clearVectorDB()
    print("s3:\n")
    s3=S3()
    s3.list_s3_files()
    print("DynamoDB:\n")
    ddb=DDB()
    ddb.getRecordCount()

def clearComponents():
    print("PineCone:\n")
    vdb=VectorDB()
    vdb.clearVectorDB(delete_flag=True)
    print("s3:\n")
    s3=S3()
    s3.delete_files()
    print("DynamoDB:\n")
    ddb=DDB()
    ddb.clear_table_items()



def main():
#    print("fetching component status...")
   getStatus()
   print("clear component status...")
#    clearComponents()
#    print("fetching component status...")
#    getStatus()


if __name__=="__main__":
    main()