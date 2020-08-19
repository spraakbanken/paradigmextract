from collections import defaultdict
import logging
import re
from paradigmextract import genregex
from paradigmextract import regexmatcher

from typing import List, Tuple, Optional, Any


class Paradigm:
    """A class representing a paradigm.

    Args:
       form_msds:list(tuple)
            Ex: [('1+en',[('tense','pres')]), ...,
       var_insts:list(tuple)
            Ex: [[('1','dimm')],[('1','dank')], ...]
    """

    def __init__(
        self,
        form_msds: List[Tuple[str, Any]],
        var_insts: List[List[Tuple[str, Any]]],
        p_id: str = "",
        pos: str = "",
        uuid: str = "",
    ) -> None:
        logging.debug("make paradigm %s %s" % (p_id, uuid))
        self._p_info = {}
        self.forms = []
        self.pos = pos
        self.uuid = uuid
        self.var_insts = var_insts
        self.p_id = p_id

        for (f, msd) in form_msds:
            self.forms.append(Form(f, msd, var_insts))

    def __getattr__(self, attr):
        """
        Caches information about paradigm
        Stuff gets weird when the paradigm has no members, should naming of a paradigm really be done here?
        """
        if len(self._p_info) > 0:
            return self._p_info[attr]
        else:
            if self.p_id:
                self._p_info["name"] = self.p_id
            if len(self.var_insts) != 0:
                if not self.p_id:
                    self._p_info["name"] = (
                        "p_%s"
                        % self.__call__(*[s for (_, s) in self.var_insts[0][1:]])[0][0]
                    )
                self._p_info["count"] = len(self.var_insts)
                self._p_info["members"] = [var[0][1] for var in self.var_insts]
            else:
                if not self.p_id:
                    self._p_info["name"] = "p_%s" % self.__call__()[0][0]
                self._p_info["members"] = []
                self._p_info["count"] = 0
            self._p_info["slots"] = self.__slots()
        return self._p_info[attr]

    def __slots(self) -> List[Tuple[bool, Any]]:
        slts = []
        """Compute the content of the slots.
        """
        # string slots
        fs = [f.strs() for f in self.forms]
        str_slots = list(zip(*fs))
        # var slots
        vt = defaultdict(list)
        for vs in self.var_insts:
            for (v, s) in vs:
                vt[v].append(s)
        var_slots = list(vt.items())
        var_slots.sort(key=lambda x: x[0])
        (s_index, v_index) = (0, 0)
        for i in range(
            len(str_slots) + len(var_slots)
        ):  # interleave strings and variables
            if i % 2 == 0:
                slts.append((False, str_slots[s_index]))
                s_index += 1
            elif var_slots:  # handle empty paradigms
                slts.append((True, var_slots[v_index][1]))
                v_index += 1
        return slts

    def fits_paradigm(
        self, w: str, tag: str = "", constrained: bool = True, baseform: bool = False
    ) -> bool:
        for f in self.forms:
            if f.match(w, tag=tag, constrained=constrained):
                return True
            if baseform:
                break
        return False

    def match(
        self,
        w: str,
        selection=None,
        constrained: bool = True,
        tag: str = "",
        baseform: bool = False,
    ) -> List[Optional[List[Tuple[int, Any]]]]:
        result = []
        if selection is not None:
            forms = [self.forms[i] for i in selection]
        elif baseform:
            forms = self.forms[:1]
        else:
            forms = self.forms
        if tag:
            forms = [f for f in forms if f.msd == tag]
        for f in forms:
            xs = f.match_vars(w, constrained)
            result.append(xs)
        return result

    def __call__(self, *insts):
        table = []
        for f in self.forms:
            (w, msd) = f(*insts)
            table.append(("".join(w), msd))
        return table

    def __str__(self):
        p = "#".join([f.__str__() for f in self.forms])
        v = "#".join([",,".join(["%s=%s" % v for v in vs]) for vs in self.var_insts])
        return "%s\t%s" % (p, v)


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

    def __init__(self, form: str, msd=(), v_insts: List[List[Tuple[str, Any]]] = ()):
        (self.form, self.msd) = (form.split("+"), msd)
        self.scount = 0
        # self.identifier = len(msd) > 0 and len(msd[0]) > 1 and msd[0][1] == "identifier"
        r = ""
        for f in self.form:
            if f.isdigit():
                r += "(.+)"
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
                self.v_regex.append(
                    re.compile(genregex.Genregex(ss, pvalue=0.05).pyregex())
                )
            except:
                logging.error("error reading %s!" % ss)
                raise

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
        return w, self.msd

    def match(self, w: str, tag: str = "", constrained: bool = True) -> bool:
        if tag and self.msd != tag:
            return False
        return self.match_vars(w, constrained) is not None

    def match_vars(
        self, w: str, constrained: bool = True
    ) -> Optional[List[Tuple[int, Any]]]:
        matcher = regexmatcher.MRegex(self.regex)
        ms = matcher.findall(w)
        if ms is None:
            return None
        elif not ms:
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
                    if len(xs) > 0 or r.pattern == ".+":
                        if r.pattern != ".+":
                            vcount += len(
                                "".join(xs)
                            )  # select the variable specificity
                    else:
                        m_all = False
                        break
                if m_all:
                    result.append((self.scount + vcount, vs))
            if result:
                return None
            else:
                return result

    def strs(self) -> List[str]:
        """Collects the strings in a wordform.
           A variable is assumed to be surrounded by (possibly empty) strings.
        """
        ss = []
        if self.form[0].isdigit():
            ss.append("_")
        for i in range(len(self.form)):
            if not (self.form[i].isdigit()):
                ss.append(self.form[i])
            elif i < len(self.form) - 1 and self.form[i + 1].isdigit():
                ss.append("_")
        if self.form[-1].isdigit():
            ss.append("_")
        return ss

    def __str__(self) -> str:
        ms = []
        for (t, v) in self.msd:
            if t is not None:
                if v is not None:
                    ms.append("%s=%s" % (t, v))
                else:
                    ms.append(t)
            else:
                if v is not None:
                    ms.append(v)
        if len(ms) == 0:
            return "+".join(self.form)
        else:
            return "%s::%s" % ("+".join(self.form), ",,".join(ms))
