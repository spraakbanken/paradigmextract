import sys

import paradigmextract.paradigm as paradigm


def pr(i, b):
    if b:
        return '[v] %d' % i
    else:
        return '[s] %d' % i


def main():
    if '-p' in sys.argv:
        for p in paradigm.load_p_file(sys.argv[-1]):
            print('name: %s, count: %d' % (p.name, p.count))
            print('members: %s' % (", ".join(p.members)))
            for f in p.forms:
                print(str(f).replace('::', '\t'))
            print()
            print(p)
    elif '-j' in sys.argv:
        for p in paradigm.load_json_file(sys.argv[-1]):
            print('name: %s, count: %d' % (p.name, p.count))
            print('members: %s' % (", ".join(p.members)))
            for f in p.forms:
                print(str(f).replace('::', '\t'))
            print()
            print(p)
            print(p.jsonify())
    elif '-s' in sys.argv:
        for p in paradigm.load_p_file(sys.argv[-1]):
            print('%s: %d' % (p.name, p.count))
            # print the content of the slots
            for (i, (is_var, s)) in enumerate(p.slots):
                print('%s: %s' % (pr(i, is_var), " ".join(s)))
            print()
    elif '-t' in sys.argv:
        paradigm.load_p_file(sys.argv[-1])
    elif '-jt' in sys.argv:
        paradigm.load_json_file(sys.argv[-1])

    else:
            print('Usage: <program> [-p|-s] <paradigm_file>')


if __name__ == '__main__':
    main()
