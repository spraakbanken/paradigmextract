import sys

import paradigmextract.paradigm as paradigm


def jsonify_form(form_obj):
    gram = {}
    process = []
    for (t, v) in form_obj.msd:
        if t is not None:
            if v is not None:
                gram[t] = v
            else:
                gram[t] = ''
        else:
            if v is not None:
                gram['msd'] = 'v'
    for part in form_obj.form:
        if part.isdigit():
            pr = {
                "operator": "addAfter",
                "processType": "pextractAddVariable",
                "variableNum": part
            }
            process.append(pr)
        else:
            pr = {
                "operator": "addAfter",
                "processType": "pextractAddConstant",
                "stringValue": part
            }
            process.append(pr)
    return {"Process": process, "GrammaticalFeatures": gram}


# function for construction paradigm lmf-json objects
def jsonify_paradigm(paradigm_obj):
    paradigm = {
        # If used with Karp: lexiconName is needed
        '_lexiconName': paradigm_obj.lex,
        'lexiconName': paradigm_obj.lex,
        '_partOfSpeech': paradigm_obj.pos,
        '_entries': len(paradigm_obj.members),
        '_uuid': paradigm_obj.uuid,
        'MorphologicalPatternID': paradigm_obj.name,
        'VariableInstances': []
    }
    for var_inst in paradigm_obj.var_insts:
        paradigm['VariableInstances'].append({})
        for v, i in var_inst:
            if v in ["0", 0]:
                v = "first-attest"
            paradigm['VariableInstances'][-1][v] = i

    paradigm['TransformCategory'] = {}
    for key, mem in paradigm_obj.classes.items():
        paradigm['TransformCategory'][key] = list(mem)

    paradigm["TransformSet"] = [jsonify_form(form) for form in paradigm_obj.forms if not form.identifier]
    return paradigm


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
            print(jsonify_paradigm(p))
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
