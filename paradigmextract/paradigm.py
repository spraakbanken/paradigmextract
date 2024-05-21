"""Paradigm."""

import logging
import operator
import re
from collections import defaultdict
from collections.abc import Sequence
from itertools import starmap
from typing import Any, Optional

from paradigmextract import genregex, regexmatcher

logger = logging.getLogger(__name__)


class Paradigm:
    """A class representing a paradigm.

    Args:
       form_msds:list(tuple)
            Ex: [('1+en',[('tense','pres')]), ...,
       var_insts:list(tuple)
            Ex: [[('1','dimm')],[('1','dank')], ...]
    """

    def __init__(  # noqa: D107
        self,
        form_msds: list[tuple[str, list[tuple[Optional[str], str]]]],
        var_insts: list[list[tuple[str, str]]],
        p_id: str = "",
        pos: str = "",
        uuid: str = "",
    ) -> None:
        logger.debug("make paradigm %s %s", p_id, uuid)
        self._p_info: dict[str, Any] = {}
        self.forms = []
        self.pos = pos
        self.uuid = uuid
        self.var_insts = var_insts
        self.p_id = p_id

        self.forms.extend(Form(f, msd, var_insts) for f, msd in form_msds)

    def __getattr__(self, attr):  # noqa: ANN204, ANN001
        """Cache information about paradigm.

        NOTE: Stuff gets weird when the paradigm has no members,
        TODO: should naming of a paradigm really be done here?
        """
        if len(self._p_info) > 0:
            return self._p_info[attr]
        if self.p_id:
            self._p_info["name"] = self.p_id
        if len(self.var_insts) == 0:
            if not self.p_id:
                self._p_info["name"] = f"p_{self.__call__()[0][0]}"
            self._p_info["members"] = []
            self._p_info["count"] = 0
        else:
            if not self.p_id:
                self._p_info["name"] = (
                    f"p_{self.__call__(*[s for _, s in self.var_insts[0][1:]])[0][0]}"
                )
            self._p_info["count"] = len(self.var_insts)
            self._p_info["members"] = [var[0][1] for var in self.var_insts]
        self._p_info["slots"] = self.__slots()
        return self._p_info[attr]

    def __slots(self) -> list[tuple[bool, Any]]:
        """Compute the content of the slots."""
        slts: list = []
        # string slots
        fs: list[list[str]] = [f.strs() for f in self.forms]
        str_slots: list[tuple[str, ...]] = list(zip(*fs))
        # var slots
        vt: dict[str, list[str]] = defaultdict(list)
        for vs in self.var_insts:
            for v, s in vs:
                vt[v].append(s)
        var_slots = list(vt.items())
        var_slots.sort(key=operator.itemgetter(0))
        (s_index, v_index) = (0, 0)
        for i in range(len(str_slots) + len(var_slots)):  # interleave strings and variables
            if i % 2 == 0:
                slts.append((False, str_slots[s_index]))
                s_index += 1
            elif var_slots:  # handle empty paradigms
                slts.append((True, var_slots[v_index][1]))
                v_index += 1
        return slts

    def fits_paradigm(  # noqa: D102
        self, w: str, tag: str = "", constrained: bool = True, baseform: bool = False
    ) -> bool:
        for f in self.forms:
            if f.match(w, tag=tag, constrained=constrained):
                return True
            if baseform:
                break
        return False

    def match(  # noqa: D102
        self,
        w: str,
        selection: Optional[Sequence[int]] = None,
        constrained: bool = True,
        tag: str = "",
        baseform: bool = False,
    ) -> list[Optional[list[tuple[int, Any]]]]:
        print(  # noqa: T201
            f"paradigm.Paradigm.match(w={w},selection={selection},constrained={constrained},tag={tag},baseform={baseform})"
        )
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
            print(f"paradigm.Paradigm.match: xs = {xs}")  # noqa: T201
            if xs and len(self.var_insts) >= 1 and len(self.var_insts[0]) > 1:
                print(f"paradigm.Paradigm.match: sorting, {xs[0][1][1]}")  # noqa: T201
                result.append(sorted(xs, key=lambda x: len(x[1][1])))
            else:
                result.append(xs)
        return result

    def __call__(self, *insts):  # noqa: ANN204, D102, ANN002
        table = []
        for f in self.forms:
            (w, msd) = f(*insts)
            table.append(("".join(w), msd))
        return table

    def __str__(self) -> str:  # noqa: D105
        p = "#".join([f.__str__() for f in self.forms])
        v = "#".join([",,".join(list(starmap("{}={}".format, vs))) for vs in self.var_insts])
        return f"{p}\t{v}"


class Form:
    """A class representing a paradigmatic wordform and, possibly, its morphosyntactic description.

    Args:
       form:str
            Ex: 1+a+2
       msd:list(tuple)
            Ex: [('num','sg'),('case':'nom') .. ]
                [] no msd available
                [(None,'SGNOM')] no msd type available
    """  # noqa: E501

    def __init__(  # noqa: D107
        self,
        form: str,
        msd: list[tuple[Optional[str], str]] = (),
        v_insts: Sequence[list[tuple[str, Any]]] = (),
    ) -> None:
        self.form: list[str] = form.split("+")
        self.msd = msd
        self.scount: int = 0
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
        collect_vars: dict[str, set[str]] = defaultdict(set)
        for vs in v_insts:
            for i, v in vs:
                collect_vars[i].add(v)
        self.v_regex = []
        for ss in collect_vars.values():
            try:
                self.v_regex.append(re.compile(genregex.Genregex(ss, pvalue=0.05).pyregex()))
            except:  # noqa: PERF203
                logging.error("error reading ss=%s!", ss)
                raise

    def __call__(self, *insts):  # noqa: ANN204, ANN002
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

    def match(self, w: str, tag: str = "", constrained: bool = True) -> bool:  # noqa: D102
        if tag and self.msd != tag:
            return False
        return self.match_vars(w, constrained) is not None

    def match_vars(self, w: str, constrained: bool = True) -> Optional[list[tuple[int, Any]]]:  # noqa: D102
        print(f"paradigm.Form.match_vars(w={w},constrained={constrained})")  # noqa: T201
        print(f"paradigm.Form.match_vars: self.regex = {self.regex}")  # noqa: T201
        matcher = regexmatcher.MRegex(self.regex)
        ms = matcher.findall(w)
        if ms is None:
            return None
        if not ms:
            return []
        if not constrained:
            return [(self.scount, m) for m in ms]
        result = []
        for vs in ms:
            var_and_reg = (
                [(vs, self.v_regex[0])] if isinstance(vs, str) else zip(vs, self.v_regex)
            )
            vcount = 0
            m_all = True
            for s, r in var_and_reg:
                m = r.match(s)
                if m is None:
                    return None
                xs = m.groups()  # .+-matches have no grouping
                if len(xs) > 0 or r.pattern == ".+":
                    if r.pattern != ".+":
                        vcount += len("".join(xs))  # select the variable specificity
                else:
                    m_all = False
                    break
            if m_all:
                result.append((self.scount + vcount, vs))
        return result or None

    def strs(self) -> list[str]:
        """Collect the strings in a wordform.

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

    def __str__(self) -> str:  # noqa: D105
        ms = []
        for t, v in self.msd:
            if t is None:
                if v is not None:
                    ms.append(v)
            elif v is not None:
                ms.append(f"{t}={v}")
            else:
                ms.append(t)
        return f'{"+".join(self.form)}::{",,".join(ms)}' if ms else "+".join(self.form)
