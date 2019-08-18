import datetime
import json
import logging
import os
import yaml
import boto3
from flask import Flask, make_response
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
cache = SimpleCache()
app.url_map.strict_slashes = False

config_file = 'conf/config.yaml'

def datestamp():
    today = datetime.datetime.today()
    todaystr = str(today.strftime('%Y-%m-%dT%H:%M:%SZ'))
    return todaystr


# def get_source_credentials():
#     if 'AWS_ACCESS_KEY_ID' in os.environ:
#         access_key = os.environ['AWS_ACCESS_KEY_ID']
#     if 'AWS_SECRET_ACCESS_KEY' in os.environ:
#         secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
#     return (access_key, secret_access_key)


def get_assumed_credentials(role):
    #  to do, compare roles with what is in yaml (as a sanity check)
    # source_credentials = get_source_credentials()
    config = get_config()
    creds = cache.get(role)
    if creds is None:
        app.logger.error('credentials not cached')
        session = boto3.Session(profile_name=config['credentials']['source_profile'], region_name=config['aws']['region'])
        sts = session.client('sts')
        creds = sts.assume_role(
            RoleArn=config['credentials']['iam_role'],
            RoleSessionName='vagrant'
            )
        app.logger.error('called out to STS')
        cache.set(role, creds, timeout=3300)
    else:
        app.logger.info('using cached credentials')
    return creds


def get_config():
    if os.path.isfile(config_file):
        with open(config_file) as f:
            try:
                config = yaml.safe_load(f)
                return config
            except:
                app.logger.error('Failed to load YAML configuration')
    else:
        app.logger.error('Config file not found')


def modify_response(data):
    resp = make_response(data)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/status')
def index():
    config = get_config()
    return json.dumps('status')


@app.route('/latest/meta-data/<info>')
def metadata(info):
    config = get_config()
    if info == 'hostname':
        data = config['ec2']['hostname']
    elif info == 'instance-id':
        data = config['ec2']['instance_id']
    elif info == 'instance-type':
        data = config['ec2']['instance_type']
    elif info == 'local-ipv4':
        data = config['ec2']['local_ipv4']
    # elif info == 'placement/availability-zone':
    #     data = config['aws']['availability_zone']
    else:
        return 'not found', 404
    resp = modify_response(data)
    return resp


@app.route('/latest/meta-data/placement/availability-zone')
def az():
    config = get_config()
    az = config['aws']['availability_zone']
    resp = modify_response(az)
    return resp


@app.route('/latest/meta-data/iam/security-credentials')
def security_credentials():
    config = get_config()
    role = config['credentials']['iam_role'].split('/')[-1]
    resp = modify_response(role)
    return resp


@app.route('/latest/meta-data/iam/security-credentials/<role>')
def security_credentials_role(role):
    #  we shoud authenticate here and return the assumed credentials
    assumed_credentials = get_assumed_credentials(role)
    #  NB:  faking expiration until we work out the timezone shenanigans
    expiration_date = assumed_credentials['Credentials']['Expiration']
    future_date = expiration_date + datetime.timedelta(seconds=3600)

    data = {
        'Code': 'Success',
        'LastUpdated': datestamp(),
        'Type': 'AWS-HMAC',
        'AccessKeyId': assumed_credentials['Credentials']['AccessKeyId'],
        'SecretAccessKey': assumed_credentials['Credentials']['SecretAccessKey'],
        'Token': assumed_credentials['Credentials']['SessionToken'],
        'Expiration': future_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    #app.logger.info(data)
    resp = modify_response(json.dumps(data))
    return resp


@app.route('/latest/dynamic/instance-identity/document')
def document():
    config = get_config()
    todaystr = datestamp()
    data = {
        'accountId': config['aws']['account_id'],
        'availabilityZone': config['aws']['availability_zone'],
        'kernelId': None,
        'ramdiskId': None,
        'pendingTime': todaystr,
        'architecture': config['ec2']['architecture'],
        'privateIp': config['ec2']['local_ipv4'],
        'devpayProductCodes': None,
        'marketplaceProductCodes': None,
        'imageId': config['ec2']['image_id'],
        'version': '2017-09-03',
        'billingProducts': None,
        'instanceId': config['ec2']['instance_id'],
        'instanceType': config['ec2']['instance_type'],
        'region': config['aws']['region']
    }
    resp = modify_response(json.dumps(data))
    return resp


@app.errorhandler(404)
def error_401(error):
    return '404', 404


if __name__ == '__main__':
    app.run
