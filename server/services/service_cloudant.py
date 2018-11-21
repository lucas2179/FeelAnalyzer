from ibmcloudenv import IBMCloudEnv
from cloudant.client import Cloudant

username = IBMCloudEnv.getString('cloudant_username')
password = IBMCloudEnv.getString('cloudant_password')
url = IBMCloudEnv.getString('cloudant_url')

cloudant = Cloudant(username, password, url=url, connect=True, auto_renew=True)

def getService(app):
    return 'cloudant', cloudant
