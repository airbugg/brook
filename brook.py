# encoding: utf-8

import sys
from workflow import Workflow3, web
from bs4 import BeautifulSoup

PIRATE_SEARCH_TEMPLATE = 'https://thepiratebay.org/search/{}/0/99/0'
RARG_SEARCH_TEMPLATE = 'https://rarbgto.org/torrents.php?search={}'
RARG_TABLE_SELECTOR = 'tr.lista2'


def is_trusted(column):
    if column.find('img', title='Trusted') is not None:
        return '✅ | '
    return ''


def is_vip(column):
    if column.find('img', title='VIP') is not None:
        return '👑 | '
    return ''


def search_torrents(search_template, query):
    url = search_template.format(query)
    r = web.get(url, timeout=30, allow_redirects=True)

    r.raise_for_status()

    result = r.content

    return result


def format_pirate_bay_results(query, bs):
    results = []

    results_table = bs.select('table tr')[1:]

    if not results_table:
        results_table.append({
            'title': 'No torrents found.',
            'subtitle': 'No torrents matching "{}" were found. Try to avoid punctuation, it helps.'.format(query)
        })
        return results_table

    for row in results_table:
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
        media_type = ' '.join(columns[0].text.strip().replace('\t', '').splitlines())
        magnet = columns[1].select('a[href^="magnet"]')[0]['href']

        subtitle = '{}{}{} | {} | {} | LE: {} | SE: {}'.format(vip, trusted, media_type, size, upload_date, leechers, seeders)

        results.append({
            'title': title,
            'subtitle': subtitle,
            'arg': magnet,
            'valid': True if int(seeders) > 0 else False
        })

    return results


def format_rarg_results(bs):
    results = []

    print(bs.select(RARG_TABLE_SELECTOR))
    for row in bs.select(RARG_TABLE_SELECTOR)[1:]:
        print(row)
    #     # columns = row.find_all('td')
    #     # description = columns[1].text.strip().split('\n\n')
    #     # vip = is_vip(columns[1])
    #     # trusted = is_trusted(columns[1])
    #     # title = description[0]
    #     # metadata = description[1].encode('utf-8').split(',')
    #     # size = metadata[1].strip().split()[1]
    #     # upload_date = metadata[0].strip()
    #     # seeders = columns[2].text
    #     # leechers = columns[3].text
    #     # type = ' '.join(columns[0].text.strip().replace('\t', '').splitlines())
    #     # magnet = columns[1].select('a[href^="magnet"]')[0]['href']
    #
    #     subtitle = '{}{}{} | {} | {} | LE: {} | SE: {}'.format(vip, trusted, type, size, upload_date, leechers, seeders)
    #
    #     results.append({
    #         'title': title,
    #         'subtitle': subtitle,
    #         'arg': magnet,
    #         'valid': True if int(seeders) > 0 else False
    #     })
    #
    # return results


def main(wf):
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    results = search_torrents(PIRATE_SEARCH_TEMPLATE, query)
    soup = BeautifulSoup(wf.decode(results), 'html.parser')

    for item in format_pirate_bay_results(query, soup):
        wf.add_item(**item)

    wf.send_feedback()


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
