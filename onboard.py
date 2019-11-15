#!/usr/bin/env python3

import boto3
import os
import uuid
import time
import logging
import botocore
from botocore.exceptions import ClientError
from botocore.vendored import requests
import json
import signal
import requests
import argparse

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


account_id = boto3.client('sts').get_caller_identity().get('Account')

parser = argparse.ArgumentParser(prog='rlawsaddccount')

parser.add_argument(
        '-u',
        '--username',
        type=str,
        help='Prisma Cloud username or access key id')

parser.add_argument(
        '-p',
        '--password',
        type=str,
        help='Prisma Cloud password or secret key')

parser.add_argument(
        '-c',
        '--customername',
        type=str,
        help='Prisma Cloud tenant name')

parser.add_argument(
        '-a',
        '--accountname',
        type=str,
        help='Account name to be used for AWS account within Prisma Cloud')

parser.add_argument(
        '-g',
        '--accountgroup',
        type=str,
        help='Prisma Cloud account group to assign to this account')

parser.add_argument(
        '-e',
        '--externalid',
        type=str,
        help='External ID that is configured for the AWS account trust relationship')

parser.add_argument(
        '-r',
        '--rolename',
        type=str,
        help='Name of the role added for Prisma Cloud access eg, PrismaReadOnlyRole')

parser.add_argument(
        '-t',
        '--tenant',
        type=str,
        help='select Prisma Cloud tenant (app, app2, app3, app4, app.eu, app.anz, app.gov')

parser.add_argument(
        '-n',
        '--updateacct',
        action='store_true',
        help='This flag will cause an existing account to be updated rather than created')

args = parser.parse_args()
        
print(args)        
        
globalVars = {}
globalVars['username']              = os.environ["PRISMA_USER_NAME"] if args.username == None else args.username
globalVars['password']              = os.environ["PRISMA_PASSWORD"] if args.password == None else args.password
globalVars['customername']          = os.environ["PRISMA_CUSTOMER_NAME"] if args.customername == None else args.customername
globalVars['accountname']           = os.environ["PRISMA_ACCOUNT_NAME"] if args.accountname == None else args.accountname
globalVars['accountgroup']          = os.environ["PRISMA_ACCOUNT_GROUP"] if args.accountgroup == None else args.accountgroup
globalVars['updateacct']            = os.environ["PRISMA_CREATE_ACCOUNT"] if "PRISMA_CREATE_ACCOUNT" in os.environ else args.updateacct
globalVars['externalid']            = osnenviron["EXTERNAL_ID"] if args.externalid == None else args.externalid
globalVars['rolename']              = os.environ["ROLE_NAME"] if args.rolename == None else args.rolename
globalVars['prismatenant']          = os.environ["PRISMA_TENANT"] if args.tenant == None else args.tenant
globalVars['accountgroupid']	    = None

if globalVars["prismatenant"]=="app":
  tenant="api"
elif globalVars["prismatenant"]=="app2":
  tenant="api2"
elif globalVars["prismatenant"]=="app3":
  tenant="api3"
elif globalVars["prismatenant"]=="app.eu":
  tenant="api.eu"
elif globalVars["prismatenant"]=="app.anz":
  tenant="api.anz"
### Create IAM Role

def start(globalVars):
    account_information = create_account_information(globalVars['accountname'])
    LOGGER.info(account_information)
    print("Starting lookup")
    response = lookup_accountgroup_id(globalVars, account_information)
    response = register_account_with_redlock(globalVars, account_information)
    return


def create_account_information(account_name):
    external_id = globalVars['externalid']
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    arn = "arn:aws:iam::"+ account_id + ":role/" + globalVars["rolename"]
    account_information = {
        'name': account_name,
        'external_id': external_id,
        'account_id': account_id,
        'arn': arn
    }
    return account_information

def get_auth_token(globalVars):
    url = "https://%s.prismacloud.io/login" % (tenant)
    headers = {'Content-Type': 'application/json'}
    payload = {
        "username": globalVars['username'],
        "password": globalVars['password'],
        "customerName": globalVars['customername']
    }
    payload = json.dumps(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()['token']
    return token

def call_redlock_api(auth_token, action, endpoint, payload, globalVars):
    url = "https://%s.prismacloud.io/" % tenant + endpoint
    headers = {'Content-Type': 'application/json', 'x-redlock-auth': auth_token}
    payload = json.dumps(payload)
    LOGGER.info(payload)
    response = requests.request(action, url, headers=headers, data=payload)
    return response

def register_account_with_redlock(globalVars, account_information):
    token = get_auth_token(globalVars)
    LOGGER.info('In register_account_with_redlock')
    LOGGER.info(token)
    payload = {
        "accountId": account_information['account_id'],
        "enabled": True,
        "externalId": account_information['external_id'],
        "groupIds": [ globalVars['accountgroupid']],
        "name": account_information['name'],
        "roleArn": account_information['arn']
    }
    if globalVars['updateacct'] == False:
       logging.info("Adding account to Prisma")
       response = call_redlock_api(token, 'POST', 'cloud/aws', payload, globalVars)
       logging.info("Account: " + account_information['name'] + " has been on-boarded to Prisma.")
       LOGGER.info(response)
    else:
       logging.info("Updating account in Prisma")
       endpoint = 'cloud/aws/' + account_information['account_id']
       response = call_redlock_api(token,'PUT', endpoint, payload, globalVars)
    return response

def lookup_accountgroup_id(globalVars, account_information):
    token = get_auth_token(globalVars)
    LOGGER.info('Looking up account group id')
    payload = {}
    endpoint = 'cloud/group/name'
    accountgroups = call_redlock_api(token, 'GET', endpoint, payload, globalVars)
    for each in accountgroups.json():
      if each['name']==globalVars['accountgroup']:
        globalVars['accountgroupid'] = each['id']
        return globalVars['accountgroupid']


start(globalVars)
print("Onboarded Account Successfully")

