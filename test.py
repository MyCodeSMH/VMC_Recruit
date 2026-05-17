from utils.vector_db_utils import VectorDB
from utils.s3_utils import S3
from utils.ddb_utils import DDB


def getStatus():
    print("PineCone:\n")
    vdb=VectorDB()
    vdb.clearVectorDB()
    print("s3:\n")
    s3=S3()
    # s3.list_s3_files(default_folder=False)
    # s3.delete_files(default_folder=False)
    s3.list_s3_files()
    # s3.delete_files()
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
#    getStatus()
   print("clear component status...")
   clearComponents()
#    print("fetching component status...")
#    getStatus()


if __name__=="__main__":
    main()


## to prevent multiple downloads of nltk

# import nltk
# import os
# import fcntl
# import time

# NLTK_LOCK_FILE = "/tmp/nltk_download.lock"
# NLTK_PACKAGES  = ['punkt_tab', 'stopwords', 'wordnet']

# def safe_nltk_download():
#     with open(NLTK_LOCK_FILE, 'w') as lock_file:
#         try:
#             # Acquire exclusive lock — other sessions wait
#             fcntl.flock(lock_file, fcntl.LOCK_EX)
#             for pkg in NLTK_PACKAGES:
#                 try:
#                     nltk.data.find(f'tokenizers/{pkg}')
#                 except LookupError:
#                     nltk.download(pkg, quiet=True)
#         finally:
#             # Release lock — next session proceeds
#             fcntl.flock(lock_file, fcntl.LOCK_UN)

# safe_nltk_download()


## Clean jd_match.py 
# import nltk
# nltk.data.path.insert(0, '/usr/share/nltk_data')  # point to pre-downloaded data
# # Remove nltk.download() calls entirely ✅



###Golden rule — treat NLTK data like a dependency: install once at build/deploy time, never download at runtime inside a multi-session application.

###Best practice:
# 1. Have VPC two subnets.
#   A. Public subnets facing internet gateway routable, allow only load balancer to provision with elastic IP
#   B. Private subnets for EC2 instances 

# 2. Security group, you application port inbound rule to allow the public subnets specific Port and IP

# 3. Load balancer with Elastic IP , user that to expose to outside world.
# 4. Public DNS register this IP with required domain name. Example: demoapp.vhkinfotech.com with public trusted certificate (paid)