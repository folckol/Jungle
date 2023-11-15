import random
import ssl
import time

import requests
import cloudscraper

from faker import Faker



# Функция для генерации случайного user-agent
def generate_user_agent():
    browsers = [
        {'name': 'Mozilla', 'versions': ['5.0', '4.0']},
        {'name': 'Chrome', 'versions': ['112.0.5615','111.0.5563','110.0.5481','109.0.5414','108.0.5359','107.0.5304','106.0.5249','105.0.5195', '89.0.4389.82', '83.0.4103.96', '91.0.4472.124', '84.0.4147.105']},
        {'name': 'Safari', 'versions': ['537.36', '537.11', '536.30', '535.19']},
        {'name': 'MSIE', 'versions': ['10.0']},
    ]

    # Список операционных систем и их версий
    operating_systems = [
        {'name': 'Windows NT', 'versions': ['5.1', '6.1', '6.2', '6.3']},
        {'name': 'Macintosh', 'versions': ['Intel Mac OS X 10.10', 'Intel Mac OS X 10.8']},
        {'name': 'Ubuntu', 'versions': ['14.04', '16.04', '18.04']},
    ]

    browser = random.choice(browsers)
    operating_system = random.choice(operating_systems)
    browser_version = random.choice(browser['versions'])
    operating_system_version = random.choice(operating_system['versions'])

    # Форматирование user-agent
    if browser['name'] == 'MSIE':
        user_agent = f"{browser['name']} {browser_version}; {operating_system['name']} {operating_system_version}; WOW64; Trident/{random.randint(4, 6)}.0"
    else:
        user_agent = f"{browser['name']}/{browser_version} ({operating_system['name']} {operating_system_version}; {'Win64; x64;' if operating_system['name'] == 'Windows NT' else ''} rv:{random.randint(45, 51)}.0) {'Gecko/' + str(random.randint(20100101, 20151231)) if browser['name'] == 'Mozilla' else 'AppleWebKit/' + str(random.randint(500, 600)) + '.0'} {'Chrome/' + str(random.randint(80, 95)) + '.0.' + str(random.randint(4000, 4500)) + '.' + str(random.randint(50, 200)) if browser['name'] == 'Chrome' else ''} {'Safari/' + random.choice(browser['versions']) if browser['name'] == 'Safari' else ''}"

    return user_agent


def _make_scraper():
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers(
        "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
        "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
        "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
        "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
        "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
        "AECDH-AES128-SHA:AECDH-AES256-SHA"
    )
    ssl_context.set_ecdh_curve("prime256v1")
    ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
    ssl_context.check_hostname = False

    return cloudscraper.create_scraper(
        debug=False,
        ssl_context=ssl_context
    )


def get_list(file_name):
    list = []
    with open(file_name) as file:
        for line in file:
            list.append(line.rstrip())
    return list


if __name__ == '__main__':


    # while True:
    #     print(generate_user_agent())
    #     time.sleep(2)
    
    proxies = get_list('proxies.txt')
    addresses = get_list('addresses.txt')
    emails = get_list('emails.txt')
    twitters = get_list('twitters.txt')

    for i in range(len(proxies)):
        try:
            proxy_list = proxies[i].split(':')
            proxy = f'http://{proxy_list[2]}:{proxy_list[3]}@{proxy_list[0]}:{proxy_list[1]}'

            session = _make_scraper()
            session.proxies = {'http': proxy,
                               'https': proxy}
            session.user_agent = generate_user_agent()
            adapter = requests.adapters.HTTPAdapter(max_retries=2)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
        except:
            print(f'{i + 1} - Proxy error')

        try:

            fake = Faker()
            Faker.seed(random.randint(1, 10000))

            payload = {'name': 'Rise - Waitlist Form',
                       'source': 'https://www.itsjungle.xyz/',
                       'test': False,
                       'fields[Name]': fake.first_name(),
                       'fields[Waitlist Email]': emails[i],
                       'fields[Twitter]': twitters[i],
                       'fields[Wallet]': addresses[i],
                       'dolphin': False}
        except:
            print(f'{i + 1} - Files error')
            break

        try:
            session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            with session.post('https://webflow.com/api/v1/form/640408ff73a83231ed4e36b4', data=payload, timeout=15) as response:
                if response.json()['msg'] == 'ok':
                    print(f'{i+1} - Succesfully registered')
                else:
                    print(f'{i+1} - Error')
        except:
            print(f'{i + 1} - Error')


    input()