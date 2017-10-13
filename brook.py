# encoding: utf-8

import sys
import argparse
from workflow import Workflow3, ICON_WEB, web
from bs4 import BeautifulSoup


# from workflow.background import run_in_background, is_running


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
    result = wf.cached_data('result', search_torrents, max_age=60)

    soup = BeautifulSoup(result, 'html.parser')

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for row in soup.select('table tr')[1:]:
        columns = row.find_all('td')
        wf.add_item(title=columns[1].text.strip(),
                    subtitle=' '.join(columns[0].text.strip().splitlines()),
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    workflow = Workflow3()
    sys.exit(workflow.run(main))
