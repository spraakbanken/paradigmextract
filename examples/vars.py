import codecs
import glob
from collections import defaultdict


def main():
    for fp in glob.glob('paradigms/*.para'):
        print('\n[%s]\n' % fp)
        with codecs.open(fp, encoding='utf-8') as f:
            result = []
            for (i, l) in enumerate(f, 1):
                (_, ex) = l.split('\t')
                d = defaultdict(list)
                d2 = defaultdict(list)
                for insts in ex.strip().split('#'):
                    for v in insts.split(','):
                        (i, s) = v.split('=')
                        d[int(i)].append(s)
                p_name = d[0][0]
                pc = len(d[0])
                del d[0]
                vc = len(d)
                count = None
                for (j, xs) in d.items():
                    if all([len(x) <= 5 for x in xs]):
                        d2[j] = set(xs)
                        if count is None:
                            count = len(d2[j])
                        else:
                            count = min(count, len(d2[j]))
                if len(d2) > 0 and pc > count:
                    result.append((pc, p_name, vc, d2))
            result.sort(reverse=True)
            for (pc, p_name, vc, d2) in result:
                print('%s (c: %d, vc: %d)' % (p_name, pc, vc)).encode('utf-8')
                for (i, xs) in d2.iteritems():
                    print('  %d: %s' % (i, "|".join(set(xs)))).encode('utf-8')


if __name__ == '__name__':
    main()
