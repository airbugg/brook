# encoding: utf-8

import sys
from workflow import Workflow3, web
from bs4 import BeautifulSoup


# from workflow.background import run_in_background, is_running

def is_trusted(column):
    if column.find('img', title='Trusted') is not None:
        return '✅ | '
    return ''

def is_vip(column):
    if column.find('img', title='VIP') is not None:
        return '👑 | '
    return ''

def search_torrents(query):
    url = 'https://thepiratebay.org/search/{}/0/99/0'.format(query)
    r = web.get(url)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by pinboard and extract the posts
    result = r.content

    return result


def main(wf):
    # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    results = search_torrents(query)
    soup = BeautifulSoup(wf.decode(results), 'html.parser')

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for row in soup.select('table tr')[1:]:
        columns = row.find_all('td')
        description = columns[1].text.strip().split('\n\n')
        vip = is_vip(columns[1])
        trusted = is_trusted(columns[1])
        title = description[0]
        metadata = description[1].encode('utf-8').split(',')
        size = metadata[1].strip().split()[1]
        upload_date = metadata[0].strip()
        seeders = columns[2].text
        leechers = columns[3].text
        type = ' '.join(columns[0].text.strip().replace('\t', '').splitlines())
        magnet = columns[1].select('a[href^="magnet"]')[0]['href']

        subtitle = '{}{}{} | {} | {} | LE: {} | SE: {}'.format(vip, trusted, type, size, upload_date, leechers, seeders)

        wf.add_item(title=title,
                    subtitle=subtitle,
                    arg=magnet,
                    valid=True if int(seeders) > 0 else False)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
