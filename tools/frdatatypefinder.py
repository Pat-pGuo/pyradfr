import os

dictionary_dir = '../dictionaries/' # where the dictionary files are contained

pyrad_coverage = frozenset(['string', 'ipaddr', 'integer', 'date', 'octets',
                            'abinary', 'ipv6addr', 'ipv6prefix', 'short', 'byte',
                            'signed', 'tlv', 'integer64'])

if __name__ == '__main__':
    data_types = set()
    dicts_count = {}

    for root, dirs, files in os.walk(dictionary_dir):
        for file in files:
            file = os.path.join(root, file)
            with open(f'{dictionary_dir}{file}', 'r') as file_open:
                for line in file_open:
                    if line.startswith('ATTRIBUTE'):
                        data_type = line.split()[3]
                        if data_type not in data_types and data_type not in pyrad_coverage:
                            data_types.add(data_type)
                            print(file, line)
                        if data_type in data_types:
                            if file not in dicts_count:
                                dicts_count[file] = 0
                            dicts_count[file] += 1


    print('---Missing Data Types---')
    for data_type in sorted(list(data_types)):
        print(data_type)

    print(f'\n---Missing {len(data_types)} data types---\n')

    print('---Missing Data Types by Dictionary---')
    for file in sorted(list(dicts_count.keys())):
        print(file)
