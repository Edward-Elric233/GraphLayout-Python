import json
import re

def dataProcess():
    with open('example2.json') as fp:
        global data
        data = fp.read()

    data = json.loads(data)

    nodes = []
    links = []
    data_nodes = data['nodes'];
    data_links = data['links'];

    for i, key in enumerate(data_nodes.keys()):
        nodes.append(key)
        data_nodes[key]['id'] = i

    print(nodes)
    with open('key.csv', 'w') as wp:
        wp.write('key,\n')
        wp.write('-,\n')
        for i in nodes:
            wp.write('%s,\n'%i)


    for key in data_links:
        source = re.split(r'[./@+]', data_links[key]['source'])
        source = '_'.join(source)
        target = re.split(r'[./@+]', data_links[key]['target'])
        target = '_'.join(target)
        links.append({'source': data_nodes[source]['id'], 'target': data_nodes[target]['id'], 'relation': data_links[key]['relation']})
        type = data_links[key]['relation']
        length = 0
        if type == 'r_dns_a' or type =='r_request_jump' or type == 'r_cert' or type == 'r_subdomain/r_request_jump':
            length = 150
        elif type == 'r_whois_name' or type == 'r_whois_email' or type == 'r_whois_phone':
            length = 120
        elif type == 'r_cert_chain' or type == 'r_dns_cname':
            length = 90
        else:
            length = 60
        links[-1]['length'] = length

    print(links)
    with open('test_data.edges', 'w') as wp:
        for edge in links:
            wp.write('%d %d %d %s\n' % (edge['source'], edge['target'], edge['length'], edge['relation']))

    return (nodes, data_nodes)
