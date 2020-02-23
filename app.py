from time import sleep, gmtime, time, ctime
from datetime import datetime
import json
import asyncio
import requests
import pytz
from facebook import GraphAPI
from wit import Wit

vendors = [{
    'name': '',
    'access_token': '',
    'address_reply': '',
    'menu_reply': '',
}]

USER_ACCESS_TOKEN = 'EAAF5Cd9fC3YBAKXSAfXUXf1TlAhxN0Ut5tHZBwV8oIbk5NKN3gXUi8HZAvGDS3IzZAR04e1fcCCfJ7ID9ElYtjY2WaxMooYALyld8z3wlb5mPPF14oRPR6wKHJ9ZA9LPOQld8mp5g2K4l9E2SLjVJ1i5Mh1a5A5ZBTGJR3BE0VwZDZD'

ACCESS_TOKEN = 'EAAF5Cd9fC3YBAA8fp4wB85aGAAQhlycs0vPIoMSpxTJBZBsCw1M1EZBSZB2EZBaflXCl722YFap65g9ZBTsG9vZAzwuNlZBCVnqyQJvdyY1FYPcYYQHLUNPYDaZCzzJRiQZCm39qyNseBy6O4armK2L3dNsjB8CfipLZCHQE2vs5eZBqYTc3KdZCtZByb'

client = Wit('GQ4J2DTDIZSTOFHZ744JOP5MWXKWQCX2')

time_format = '%Y-%m-%dT%H:%M:%S%z'

page_id = '103750251156613'

vendors = requests.get('https://rest-bot-dev.herokuapp.com/vendors').json()


loop = asyncio.get_event_loop()

last_time_function_ran = datetime.strptime(
    '2020-02-22T02:10:01+0000', time_format)  # pytz.utc.localize(datetime.utcnow())


def timer_function():
    start_time = time()
    while True:
        Look_for_comments(vendors[1])
        sleep(300.0 - (time() % 300.0))


def Look_for_comments(vendor):
    print(vendor['page_id'])
    graph = GraphAPI(access_token=vendor['access_token'])
    global last_time_function_ran
    print('Started at {} ....'.format(last_time_function_ran))

    posts = graph.get_connections(
        id=vendor['page_id'], connection_name='posts', fields='updated_time,comments{message,created_time}')
    data = posts['data']
    for post in data:
        post_updated_time = datetime.strptime(
            post['updated_time'], time_format)
        if post_updated_time > last_time_function_ran:
            for comment in post['comments']['data']:
                comment_created_time = datetime.strptime(
                    comment['created_time'], time_format)

                if not check_for_comments(comment['id'], graph, vendor):

                    print('Found Comment!')
                    msg = ask_wit(comment['message'], vendor)
                    if msg:
                        graph.put_comment(object_id=comment['id'],
                                          message=msg)
                        print('Replied to Comment')

    last_time_function_ran = pytz.utc.localize(datetime.utcnow())
    print('...Finished at {}'.format(last_time_function_ran))


# ================================================= HELPER FUNCTIONS ================================================= #

def ask_wit(msg, vendor):
    response = client.message(msg)
    entity = response['entities']
    print(msg)
    if 'Address' in entity:
        confidence = entity['Address'][0]['confidence']
        if confidence > 0.65:
            return vendor['address_info']
        else:
            return False
    elif 'menu' in entity:
        confidence = entity['menu'][0]['confidence']
        if confidence > 0.6:
            return vendor['menu_info']
        else:
            print('not Suitable')
            return False


def check_for_comments(_id, graph, vendor):
    comments = graph.get_connections(
        id=_id, connection_name='comments')['data']
    for comment in comments:
        if comment['from']['id'] == vendor['page_id']:
            return True
    return False


# ================================================= Start Execution ================================================= #
if __name__ == "__main__":
    # try:
    #     loop.run_until_complete(main())
    # except Exception as e:
    #     pass
    # finally:
    #     loop.close()
    timer_function()
