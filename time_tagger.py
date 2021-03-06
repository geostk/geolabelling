import subprocess
import datetime
from dateutil import parser
import lxml.etree as etree
from xml.sax.saxutils import escape, unescape
import os


def get_heideltime_annotations(value, heideltime_path, language):

    tmp_file = 'tmp_temporalinfo.txt'
    with open(tmp_file, 'w') as f:
        f.write(value.encode('utf-8'))

    cwd = os.getcwd()

    p = subprocess.Popen(['java', '-jar', 'de.unihd.dbs.heideltime.standalone.jar', '-l', language, os.path.join(cwd, tmp_file)], cwd=heideltime_path, stdout=subprocess.PIPE)
    res, err = p.communicate()
    root = etree.fromstring(res)
    return root


def get_temporal_information(dist, dataset, heideltime_path='heideltime-standalone', language='GERMAN'):
    # get temporal information
    dataset_name = dataset.get('name', '')
    dataset_description = dataset.get('description', '')
    keywords = dataset.get('keywords', [])
    dist_name = dist.get('name', '')
    dist_description = dist.get('description', '')

    # priorities to different sources of datetime information: dist > dataset info
    for value in [dist_name, dist_description, dataset_name, dataset_description, ', '.join(keywords)]:
        dates = []
        # first escape any xml escaped characters
        esc_v = escape(value)
        root = get_heideltime_annotations(esc_v, heideltime_path, language)
        for t in root:
            if t.attrib['type'] == 'DATE':
                v = t.attrib['value']
                date = parser.parse(v)
                dates.append(date)
        if len(dates) > 0:
            start = min(dates).strftime("%Y-%m-%d")
            end = max(dates).strftime("%Y-%m-%d")
            return start, end
    return None, None