import sys
import json
import codecs
from typing import List, Dict, Any

import paradigmextract.paradigm as paradigm


def load_json_file(file: str, lex: str = '', pos: str = '') -> List[paradigm.Paradigm]:
    try:
        return load_json(json.load(codecs.open(file, encoding='utf-8')), lex=lex, pos=pos)
    except Exception as e:
        print('Could not read json file %s' % e)
        raise


def load_json(objs: List[Dict[str, Any]], lex: str = '', pos: str = '') -> List[paradigm.Paradigm]:
    paradigms = []
    obj_no = 1
    try:
        for paradigm in objs:
            var_insts = [list(inst.items()) for inst in paradigm.get('VariableInstances', [])]
            p_id = paradigm.get('MorphologicalPatternID', '')
            uuid = paradigm.get('_uuid', '')
            form_msd = []

            classes = dict([(key, set(val)) for key, val in paradigm.get('TransformCategory', {}).items()])

            for transform in paradigm.get("TransformSet", []):
                f = []
                for p in transform.get("Process", []):
                    # TODO check processType? and operator?
                    if p.get('processType', '') == "pextractAddVariable":
                        f.append(p['variableNum'])
                    if p.get('processType', '') == "pextractAddConstant":
                        f.append(p['stringValue'])
                msd = list(transform.get('GrammaticalFeatures').items())
                form_msd.append(('+'.join(f), msd))
            paradigms.append((form_msd, var_insts, p_id, uuid))
            obj_no += 1
    except Exception as e:
        print('Error on object %d:\n %s' % (obj_no, e))
        raise
    paradigms.sort(reverse=True)
    # classes is removed
    return [paradigm.Paradigm(wfs, p_members, p_id, uuid=uuid, lex=lex, pos=pos)
            for (wfs, p_members, p_id, uuid) in paradigms]


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


def load_p_file(file: str, pos: str = '', lex: str = '') -> List[paradigm.Paradigm]:
    paradigms = []
    line_no = 1
    with codecs.open(file, encoding='utf-8') as f:
        try:
            for l in f:
                try:
                    (p, ex) = l.strip().split('\t')
                except:
                    p = l.strip()
                    ex = ''
                p_members = []
                wfs = []
                for s in p.split('#'):
                    (w, m) = s.split('::')
                    msd = [tuple(x.split('=')) for x in m.split(',,')]
                    wfs.append((w, msd))
                if len(ex) > 0:
                    for s in ex.split('#'):
                        mem = []
                        for vbind in s.split(',,'):
                            mem.append(tuple(vbind.split('=')))
                        p_members.append(mem)
                else:  # no variables
                    p_members = []
                paradigms.append((len(p_members), wfs, p_members))
                line_no += 1
        except:
            print('Error on line %s' % line_no)
            raise
    paradigms.sort(reverse=True)
    return [paradigm.Paradigm(wfs, p_members, 'p%d_%s' % (i, p_members[0][0][1]), pos=pos, lex=lex)
            for (i, (_, wfs, p_members)) in enumerate(paradigms, 1)]


def main():
    if '-p' in sys.argv:
        for p in load_p_file(sys.argv[-1]):
            print('name: %s, count: %d' % (p.name, p.count))
            print('members: %s' % (", ".join(p.members)))
            for f in p.forms:
                print(str(f).replace('::', '\t'))
            print()
            print(p)
    elif '-j' in sys.argv:
        for p in load_json_file(sys.argv[-1]):
            print('name: %s, count: %d' % (p.name, p.count))
            print('members: %s' % (", ".join(p.members)))
            for f in p.forms:
                print(str(f).replace('::', '\t'))
            print()
            print(p)
            print(jsonify_paradigm(p))
    elif '-s' in sys.argv:
        for p in load_p_file(sys.argv[-1]):
            print('%s: %d' % (p.name, p.count))
            # print the content of the slots
            for (i, (is_var, s)) in enumerate(p.slots):
                print('%s: %s' % (pr(i, is_var), " ".join(s)))
            print()
    elif '-t' in sys.argv:
        load_p_file(sys.argv[-1])
    elif '-jt' in sys.argv:
        load_json_file(sys.argv[-1])

    else:
            print('Usage: <program> [-p|-s] <paradigm_file>')


if __name__ == '__main__':
    main()
