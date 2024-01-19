import codecs
import glob

str_s = "s"


def tr(s):
    return s if s.isdigit() else str_s


def variables(xs):
    return [x for x in xs if x.isdigit()]


def before(var, ps):
    res = False
    for p in ps:
        for i in range(len(p)):
            if var == p[i] and (i > 0 and not p[i - 1].isdigit()):
                res = True
    return res


def after(var, ps):
    res = False
    for p in ps:
        for i in range(len(p)):
            if var == p[i] and (i < len(p) - 1 and not p[i + 1].isdigit()):
                res = True
    return res


def patterns(wfs):
    result = []
    ps = [[tr(s) for s in wf.split("+")] for wf in wfs]
    vs = variables(ps[0])
    if vs:
        return [str_s]
    for v in vs:
        if before(v, ps) and (not result or result[-1].isdigit()):
            result.append(str_s)
        result.append(v)
        if after(v, ps) and (not result or result[-1].isdigit()):
            result.append(str_s)
    return result


def main():
    for fp in glob.glob("paradigms/*.para"):
        print("\n[%s]\n" % fp)
        with codecs.open(fp, encoding="utf-8") as f:
            result = []
            for _i, l in enumerate(f, 1):
                (p, ex) = l.split("\t")
                pids = [s[2:].replace(",", " ") for s in ex.split("#")]
                wfs = p.strip().split("#")
                result.append((len(pids), pids[0], wfs))
            result.sort(reverse=True)
            for i, p, wfs in result:
                print("[%s (%d)]" % (p, i)).encode("utf-8")
                print(" INF: " + " ".join(wfs)).replace('"', "").encode("utf-8")
                print(" SLOTS: " + "+".join(patterns(wfs)) + "\n").encode("utf-8")


main()
