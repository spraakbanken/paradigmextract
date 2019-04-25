# -*- coding: utf-8 -*-

import codecs
from collections import defaultdict
import paradigmextract.genregex as genregex
import json
import logging
import re
import paradigmextract.regexmatcher as regexmatcher
import sys

from typing import List, Dict, Tuple, Set, Optional, Any


def overlap(ss):
    count = 0
    for (c1, c2) in zip(prefix[::-1], suffix):
        if c1 == c2:
            count += 1
        else:
            return count
    return count


class Paradigm:
    """A class representing a paradigm.

    Args:
       form_msd:list(tuple)
            Ex: [('1+en',[('tense','pres')]), ...,
       var_insts:list(tuple)
            Ex: [[('1','dimm')],[('1','dank')], ...]
    """

    def __init__(self, form_msds: List[Tuple[str, Any]], var_insts: List[List[Tuple[str, Any]]], p_id: str='', small: bool=False, pos: str = '',
                 lex: str='', uuid: str='', classes={}) -> None:
        # def __init__(self, paradigm):
        # prefix: just for naming, exclude since we have p_id?
        # def __init__(self, form_msds, var_insts, prefix=None, p_id=None):
        logging.debug('make paradigm %s %s in lexicon %s' % (p_id, uuid, lex))
        self.p_info = {}
        self.small = small
        self.classes = classes
        self.forms = []
        self.pos = pos
        self.lex = lex
        self.uuid = uuid
        if small:
            self.var_insts = []
        else:
            self.var_insts = var_insts
        self.p_id = p_id

        for (f, msd) in form_msds:
            self.forms.append(Form(f, msd, var_insts))

    def set_id(self, p_id: str) -> None:
        self.p_id = p_id

    def set_uuid(self, uuid: str) -> None:
        self.uuid = uuid

    # This one is probably broken, should be extend, not append?
    def add_var_insts(self, var_inst: List[Tuple[Any, Any]]) -> None:
        self.var_insts.append([(str(key), val) for key, val in var_inst])

    def set_pos(self, pos: str) -> None:
        self.pos = pos

    def set_lexicon(self, lexicon: str) -> None:
        self.lex = lexicon

    def shrink(self) -> None:
        self.var_insts = []
        self.members = []
        self.small = True

    def empty_classes(self) -> None:
        self.classes = {}

    def add_class(self, name, members) -> None:
        if name not in self.classes:
            print('classname', name)
            print('classse', self.classes)
            self.classes[name] = set()
        # print('add class', name, members)
        self.classes[name].update(members)
        # print('added class', self.classes)

    def __getattr__(self, attr):
        # TODO Will mflbackend need to recompute this when updating paradigms?
        if len(self.p_info) > 0:  # Compute only once.
            return self.p_info[attr]
        else:
            if self.p_id:
                self.p_info['name'] = self.p_id
            if len(self.var_insts) != 0:
                # TODO naming strategy: how to name paradigms?
                if not self.p_id:
                    self.p_info['name'] = 'p_%s' % self.__call__(*[s for (_, s) in self.var_insts[0][1:]])[0][0]
                self.p_info['count'] = len(self.var_insts)
                self.p_info['members'] = [var[0][1] for var in self.var_insts]
            else:  # no variables
                # TODO naming strategy: name might get weird without var_insts
                if not self.p_id:
                    self.p_info['name'] = 'p_%s' % self.__call__()[0][0]
                self.p_info['members'] = []
                # TODO changed from 1 to 0, since empty paradigms should not pretend to have members
                # May cause errors when calculating score
                self.p_info['count'] = 0
            self.p_info['slots'] = self.__slots()
        return self.p_info[attr]

    def __slots(self) -> List[Tuple[bool, Any]]:
        slts = []
        """Compute the content of the slots.
        """
        # string slots
        fs = [f.strs() for f in self.forms if not f.identifier]
        str_slots = list(zip(*fs))
        # var slots
        vt = defaultdict(list)
        for vs in self.var_insts:
            for (v, s) in vs:
                vt[v].append(s)
        var_slots = list(vt.items())
        var_slots.sort(key=lambda x: x[0])
        (s_index, v_index) = (0, 0)
        for i in range(len(str_slots) + len(var_slots)):  # interleave strings and variables
            if i % 2 == 0:
                    slts.append((False, str_slots[s_index]))
                    s_index += 1
            elif var_slots:  # handle empty paradigms
                slts.append((True, var_slots[v_index][1]))
                v_index += 1
        return slts

    def fits_paradigm(self, w: str, tag: str='', constrained: bool=True, baseform: bool=False) -> bool:
        # TODO will this make word fail if you provide all forms+identifier?
        for f in self.forms:
            if f.match(w, tag=tag, constrained=constrained) and not f.identifier:
                return True
            if baseform:
                break
        return False

    def match(self, w: str, selection=None, constrained: bool=True, tag: str='', baseform: True=False) -> List:
        result = []
        if selection is not None:
            forms = [self.forms[i] for i in selection]
        elif baseform:
            forms = self.forms[:1]
        else:
            forms = [f for f in self.forms if not f.identifier]
        if tag:
            forms = [f for f in forms if f.msd == tag]
        for f in forms:
            # print('forms to evaluate', f.form, f.msd, 'to', w)
            xs = f.match_vars(w, constrained)
            # print('vars', xs)
            result.append(xs)
        return result

    def paradigm_forms(self) -> List[Dict[str, Any]]:
        if len(self.var_insts) > 0:
            ss = [s for (_, s) in self.var_insts[0]]
        else:
            ss = []
        return [f.shapes(ss) for f in self.forms]

    def __call__(self, *insts):
        table = []
        for f in self.forms:
            (w, msd) = f(*insts)
            table.append((''.join(w), msd))
        return table

    # function for construction paradigm lmf-json objects
    def jsonify(self):
        paradigm = {}
        paradigm['_lexiconName'] = self.lex
        # If used with Karp: lexiconName is needed
        paradigm['lexiconName'] = self.lex
        paradigm['_partOfSpeech'] = self.pos
        paradigm['_entries'] = len(self.members)
        paradigm['_uuid'] = self.uuid
        paradigm['MorphologicalPatternID'] = self.name
        paradigm['VariableInstances'] = []
        for var_inst in self.var_insts:
            paradigm['VariableInstances'].append({})
            for v, i in var_inst:
                if v in ["0", 0]:
                    v = "first-attest"
                paradigm['VariableInstances'][-1][v] = i

        paradigm['TransformCategory'] = {}
        for key, mem in self.classes.items():
            paradigm['TransformCategory'][key] = list(mem)

        paradigm["TransformSet"] = [form.jsonify() for form in self.forms if not form.identifier]
        return paradigm

    def pattern(self):
        return "#".join([f.__str__() for f in self.forms])

    def __str__(self):
        p = "#".join([f.__str__() for f in self.forms])
        v = "#".join([",,".join(['%s=%s' % v for v in vs]) for vs in self.var_insts])
        return '%s\t%s' % (p, v)


class Form:
    """A class representing a paradigmatic wordform and, possibly, its
    morphosyntactic description.

    Args:
       form:str
            Ex: 1+a+2
       msd:list(tuple)
            Ex: [('num','sg'),('case':'nom') .. ]
                [] no msd available
                [(None,'SGNOM')] no msd type available
    """
    def __init__(self, form: str, msd=[], v_insts: List[Tuple[str, Any]]=[]):
        (self.form, self.msd) = (form.split('+'), msd)
        self.scount = 0
        self.identifier = len(msd) > 0 and len(msd[0]) > 0 and msd[0][1] == "identifier"
        r = ''
        for f in self.form:
            if f.isdigit():
                r += '(.+)'
            else:
                r += f
                self.scount += len(f)
        self.regex = r
        self.cregex = re.compile(self.regex)
        # vars
        collect_vars = defaultdict(set)
        for vs in v_insts:
            for (i, v) in vs:
                collect_vars[i].add(v)
        self.v_regex = []
        for (_, ss) in collect_vars.items():
            try:
                self.v_regex.append(re.compile(genregex.genregex(ss, pvalue=0.05).pyregex()))
            except:
                logging.error('error reading %s!' % ss)
                raise

    def shapes(self, ss) -> Dict[str, Any]:
        w = "".join(self.__call__(*ss)[0])
        return {'form': "+".join(self.form),
                'msd': self.msd,
                'w': w,
                'regex': self.regex,
                'cregex': self.cregex,
                'v_regex': self.v_regex}

    def __call__(self, *insts):
        """Instantiate the variables of the wordform.
           Args:
            insts: fun args
                   Ex: f('schr','i','b')
        """
        (w, vindex) = ([], 0)
        for p in self.form:
            if p.isdigit():  # is a variable
                w.append(insts[vindex])
                vindex += 1
            else:
                w.append(p)
        return (w, self.msd)

    def match(self, w: str, tag: str='', constrained=True) -> Optional[List[Tuple[int, Any]]]:
        # print('compare', w, tag, 'to', self.msd)
        if tag and self.msd != tag:
            return False
            # return None?
        return self.match_vars(w, constrained) is not None

    def match_vars(self, w: str, constrained: bool=True) -> Optional[List[Tuple[int, Any]]]:
        matcher = regexmatcher.mregex(self.regex)
        ms = matcher.findall(w)
        if ms is None:
            return None
        elif ms == []:
            return []
        if not constrained:
            return [(self.scount, m) for m in ms]
        else:
            result = []
            for vs in ms:
                if type(vs) == str:
                    var_and_reg = [(vs, self.v_regex[0])]
                else:
                    var_and_reg = zip(vs, self.v_regex)
                vcount = 0
                m_all = True
                for (s, r) in var_and_reg:
                    m = r.match(s)
                    if m is None:
                            return None
                    xs = m.groups()  # .+-matches have no grouping
                    if len(xs) > 0 or r.pattern == '.+':
                        if r.pattern != '.+':
                            vcount += len("".join(xs))  # select the variable specificity
                    else:
                        m_all = False
                        break
                if m_all:
                    result.append((self.scount+vcount, vs))
            if result == []:
                return None
            else:
                return result

    def strs(self) -> List[str]:
        """Collects the strings in a wordform.
           A variable is assumed to be surrounded by (possibly empty) strings.
        """
        ss = []
        if self.form[0].isdigit():
            ss.append('_')
        for i in range(len(self.form)):
            if not(self.form[i].isdigit()):
                ss.append(self.form[i])
            elif i < len(self.form)-1 and self.form[i+1].isdigit():
                ss.append('_')
        if self.form[-1].isdigit():
            ss.append('_')
        return ss

    def jsonify(self) -> Dict[str, Any]:
        gram = {}
        process = []
        for (t, v) in self.msd:
            if t is not None:
                if v is not None:
                    gram[t] = v
                else:
                    gram[t] = ''
            else:
                if v is not None:
                    gram['msd'] = 'v'
        for part in self.form:
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

    def __str__(self) -> str:
        ms = []
        for (t, v) in self.msd:
            if t is not None:
                if v is not None:
                    ms.append('%s=%s' % (t, v))
                else:
                    ms.append(t)
            else:
                if v is not None:
                    ms.append(v)
        if len(ms) == 0:
            return "+".join(self.form)
        else:
            return "%s::%s" % ("+".join(self.form), ",,".join(ms))


def load_p_file(file: str, pos: str='', lex: str='') -> List[Paradigm]:
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
            logging.error('Error on line %s' % line_no)
            raise
    paradigms.sort(reverse=True)
    return [Paradigm(wfs, p_members, 'p%d_%s' % (i, p_members[0][0][1]), pos=pos, lex=lex)
            for (i, (_, wfs, p_members)) in enumerate(paradigms, 1)]


def load_json_file(file: str, lex: str='', pos: str='') -> List[Paradigm]:
    try:
        return load_json(json.load(codecs.open(file, encoding='utf-8')), lex=lex, pos=pos)
    except Exception as e:
        logging.error('Could not read json file %s' % (e))
        raise


def load_json(objs: List[Dict[str, Any]], lex: str='', pos: str='') -> List[Paradigm]:
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
        logging.error('Error on object %d:\n %s' % (obj_no, e))
        raise
    paradigms.sort(reverse=True)
    return [Paradigm(wfs, p_members, p_id, uuid=uuid, lex=lex, pos=pos, classes=classes)
            for (wfs, p_members, p_id, uuid) in paradigms]


def pr(i, b):
    if b:
        return '[v] %d' % (i)
    else:
        return '[s] %d' % (i)


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
            print(p.jsonify())
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
