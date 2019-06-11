from pextract import collapse_tables


def test1():
    filteredtables = []

    idform = 'stad'
    idtag = ('msd', 'sg indef nom')
    table = ['stad', 'städer', 'stads']
    c = ('[st]a[d]', '[st]ä[d]er', '[st]a[d]s')
    variable_table = ['1+a+2', '1+ä+2+er', '1+a+2+s']
    variablelist = ['st', 'd']
    numvars = 2
    infixcount = 3
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]
    filteredtables.append((idform, idtag, [table, c, variable_table, variablelist, numvars, infixcount], tags))

    idform = 'bad'
    idtag = ('msd', 'sg indef nom')
    table = ['bad', 'bäder', 'bads']
    c = ('[b]a[d]', '[b]ä[d]er', '[b]a[d]s')
    variable_table = ['1+a+2', '1+ä+2+er', '1+a+2+s']
    variablelist = ['b', 'd']
    numvars = 2
    infixcount = 3
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]
    filteredtables.append((idform, idtag, [table, c, variable_table, variablelist, numvars, infixcount], tags))

    paradigmlist = collapse_tables(filteredtables)
    assert len(paradigmlist) == 1
    var_insts = paradigmlist[0].var_insts
    assert ('1', 'b') in var_insts[0]
    assert ('2', 'd') in var_insts[0]
    assert ('1', 'st') in var_insts[1]
    assert ('2', 'd') in var_insts[1]


def test2():
    filteredtables = []

    idform = 'bord'
    idtag = ('msd', 'sg indef nom')
    table = ['bord', 'bord', 'bords']
    c = ('[bord]', '[bord]', '[bord]s')
    variable_table = ['1', '1', '1+s']
    variablelist = ['bord']
    numvars = 1
    infixcount = 0
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]
    filteredtables.append((idform, idtag, [table, c, variable_table, variablelist, numvars, infixcount], tags))

    idform = 'bad'
    idtag = ('msd', 'sg indef nom')
    table = ['bad', 'bäder', 'bads']
    c = ('[b]a[d]', '[b]ä[d]er', '[b]a[d]s')
    variable_table = ['1+a+2', '1+ä+2+er', '1+a+2+s']
    variablelist = ['b', 'd']
    numvars = 2
    infixcount = 3
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]
    filteredtables.append((idform, idtag, [table, c, variable_table, variablelist, numvars, infixcount], tags))

    paradigmlist = collapse_tables(filteredtables)
    assert len(paradigmlist) == 2
    var_insts = paradigmlist[0].var_insts
    assert ('1', 'bord') in var_insts[0]

    var_insts = paradigmlist[1].var_insts
    assert ('1', 'b') in var_insts[0]
    assert ('2', 'd') in var_insts[0]


def test_transient():
    filtered_tables = [('sopar bort', ('msd', 'pres ind aktiv'), [
        ['sopar bort', 'sopas bort', 'sopade bort', 'sopades bort', 'sopa bort', 'sopa bort', 'sopas bort',
         'sopat bort', 'sopats bort', 'sopande bort', 'sopandes bort', 'sopad bort', 'bortsopad', 'sopads bort',
         'bortsopads', 'sopat bort', 'bortsopat', 'sopats bort', 'bortsopats', 'sopade bort', 'bortsopade',
         'sopades bort', 'bortsopades', 'sopade bort', 'bortsopade', 'sopades bort', 'bortsopades', 'sopade bort',
         'bortsopade', 'sopades bort', 'bortsopades', 'sopade bort', 'bortsopade', 'sopades bort', 'bortsopades'], (
        '[sopa]r bort', '[sopa]s bort', '[sopa]de bort', '[sopa]des bort', '[sopa] bort', '[sopa] bort', '[sopa]s bort',
        '[sopa]t bort', '[sopa]ts bort', '[sopa]nde bort', '[sopa]ndes bort', '[sopa]d bort', 'bort[sopa]d',
        '[sopa]ds bort', 'bort[sopa]ds', '[sopa]t bort', 'bort[sopa]t', '[sopa]ts bort', 'bort[sopa]ts',
        '[sopa]de bort', 'bort[sopa]de', '[sopa]des bort', 'bort[sopa]des', '[sopa]de bort', 'bort[sopa]de',
        '[sopa]des bort', 'bort[sopa]des', '[sopa]de bort', 'bort[sopa]de', '[sopa]des bort', 'bort[sopa]des',
        '[sopa]de bort', 'bort[sopa]de', '[sopa]des bort', 'bort[sopa]des'),
        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort', '1+t bort', '1+ts bort',
         '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort', 'bort+1+ds', '1+t bort', 'bort+1+t',
         '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des'], ['sopa'], 1, 0],
                     [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'), ('msd', 'pret ind aktiv'),
                      ('msd', 'pret ind s-form'), ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                      ('msd', 'sup aktiv'), ('msd', 'sup s-form'), ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                      ('msd', 'pret_part indef sg u nom'), ('msd', 'pret_part indef sg u nom'),
                      ('msd', 'pret_part indef sg u gen'), ('msd', 'pret_part indef sg u gen'),
                      ('msd', 'pret_part indef sg n nom'), ('msd', 'pret_part indef sg n nom'),
                      ('msd', 'pret_part indef sg n gen'), ('msd', 'pret_part indef sg n gen'),
                      ('msd', 'pret_part indef pl nom'), ('msd', 'pret_part indef pl nom'),
                      ('msd', 'pret_part indef pl gen'), ('msd', 'pret_part indef pl gen'),
                      ('msd', 'pret_part def sg no_masc nom'), ('msd', 'pret_part def sg no_masc nom'),
                      ('msd', 'pret_part def sg no_masc gen'), ('msd', 'pret_part def sg no_masc gen'),
                      ('msd', 'pret_part def sg masc nom'), ('msd', 'pret_part def sg masc nom'),
                      ('msd', 'pret_part def sg masc gen'), ('msd', 'pret_part def sg masc gen'),
                      ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl gen'),
                      ('msd', 'pret_part def pl gen')]), ('jagar bort', ('msd', 'pres ind aktiv'), [
        ['jagar bort', 'jagas bort', 'jagade bort', 'jagades bort', 'jaga bort', 'jaga bort', 'jagas bort',
         'jagat bort', 'jagats bort', 'jagande bort', 'jagandes bort', 'jagad bort', 'bortjagad', 'jagads bort',
         'bortjagads', 'jagat bort', 'bortjagat', 'jagats bort', 'bortjagats', 'jagade bort', 'bortjagade',
         'jagades bort', 'bortjagades', 'jagade bort', 'bortjagade', 'jagades bort', 'bortjagades', 'jagade bort',
         'bortjagade', 'jagades bort', 'bortjagades', 'jagade bort', 'bortjagade', 'jagades bort', 'bortjagades'], (
        '[jaga]r bort', '[jaga]s bort', '[jaga]de bort', '[jaga]des bort', '[jaga] bort', '[jaga] bort', '[jaga]s bort',
        '[jaga]t bort', '[jaga]ts bort', '[jaga]nde bort', '[jaga]ndes bort', '[jaga]d bort', 'bort[jaga]d',
        '[jaga]ds bort', 'bort[jaga]ds', '[jaga]t bort', 'bort[jaga]t', '[jaga]ts bort', 'bort[jaga]ts',
        '[jaga]de bort', 'bort[jaga]de', '[jaga]des bort', 'bort[jaga]des', '[jaga]de bort', 'bort[jaga]de',
        '[jaga]des bort', 'bort[jaga]des', '[jaga]de bort', 'bort[jaga]de', '[jaga]des bort', 'bort[jaga]des',
        '[jaga]de bort', 'bort[jaga]de', '[jaga]des bort', 'bort[jaga]des'),
        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort', '1+t bort', '1+ts bort',
         '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort', 'bort+1+ds', '1+t bort', 'bort+1+t',
         '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des'], ['jaga'], 1, 0], [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'),
                                                        ('msd', 'pret ind aktiv'), ('msd', 'pret ind s-form'),
                                                        ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                                                        ('msd', 'sup aktiv'), ('msd', 'sup s-form'),
                                                        ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                                                        ('msd', 'pret_part indef sg u nom'),
                                                        ('msd', 'pret_part indef sg u nom'),
                                                        ('msd', 'pret_part indef sg u gen'),
                                                        ('msd', 'pret_part indef sg u gen'),
                                                        ('msd', 'pret_part indef sg n nom'),
                                                        ('msd', 'pret_part indef sg n nom'),
                                                        ('msd', 'pret_part indef sg n gen'),
                                                        ('msd', 'pret_part indef sg n gen'),
                                                        ('msd', 'pret_part indef pl nom'),
                                                        ('msd', 'pret_part indef pl nom'),
                                                        ('msd', 'pret_part indef pl gen'),
                                                        ('msd', 'pret_part indef pl gen'),
                                                        ('msd', 'pret_part def sg no_masc nom'),
                                                        ('msd', 'pret_part def sg no_masc nom'),
                                                        ('msd', 'pret_part def sg no_masc gen'),
                                                        ('msd', 'pret_part def sg no_masc gen'),
                                                        ('msd', 'pret_part def sg masc nom'),
                                                        ('msd', 'pret_part def sg masc nom'),
                                                        ('msd', 'pret_part def sg masc gen'),
                                                        ('msd', 'pret_part def sg masc gen'),
                                                        ('msd', 'pret_part def pl nom'),
                                                        ('msd', 'pret_part def pl nom'),
                                                        ('msd', 'pret_part def pl gen'),
                                                        ('msd', 'pret_part def pl gen')]), (
                    'kollrar bort', ('msd', 'pres ind aktiv'), [
                        ['kollrar bort', 'kollras bort', 'kollrade bort', 'kollrades bort', 'kollra bort',
                         'kollra bort', 'kollras bort', 'kollrat bort', 'kollrats bort', 'kollrande bort',
                         'kollrandes bort', 'kollrad bort', 'bortkollrad', 'kollrads bort', 'bortkollrads',
                         'kollrat bort', 'bortkollrat', 'kollrats bort', 'bortkollrats', 'kollrade bort',
                         'bortkollrade', 'kollrades bort', 'bortkollrades', 'kollrade bort', 'bortkollrade',
                         'kollrades bort', 'bortkollrades', 'kollrade bort', 'bortkollrade', 'kollrades bort',
                         'bortkollrades', 'kollrade bort', 'bortkollrade', 'kollrades bort', 'bortkollrades'], (
                        '[kollra]r bort', '[kollra]s bort', '[kollra]de bort', '[kollra]des bort', '[kollra] bort',
                        '[kollra] bort', '[kollra]s bort', '[kollra]t bort', '[kollra]ts bort', '[kollra]nde bort',
                        '[kollra]ndes bort', '[kollra]d bort', 'bort[kollra]d', '[kollra]ds bort', 'bort[kollra]ds',
                        '[kollra]t bort', 'bort[kollra]t', '[kollra]ts bort', 'bort[kollra]ts', '[kollra]de bort',
                        'bort[kollra]de', '[kollra]des bort', 'bort[kollra]des', '[kollra]de bort', 'bort[kollra]de',
                        '[kollra]des bort', 'bort[kollra]des', '[kollra]de bort', 'bort[kollra]de', '[kollra]des bort',
                        'bort[kollra]des', '[kollra]de bort', 'bort[kollra]de', '[kollra]des bort', 'bort[kollra]des'),
                        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort',
                         '1+t bort', '1+ts bort', '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort',
                         'bort+1+ds', '1+t bort', 'bort+1+t', '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de',
                         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort',
                         'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des'],
                        ['kollra'], 1, 0],
                    [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'), ('msd', 'pret ind aktiv'),
                     ('msd', 'pret ind s-form'), ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                     ('msd', 'sup aktiv'), ('msd', 'sup s-form'), ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                     ('msd', 'pret_part indef sg u nom'), ('msd', 'pret_part indef sg u nom'),
                     ('msd', 'pret_part indef sg u gen'), ('msd', 'pret_part indef sg u gen'),
                     ('msd', 'pret_part indef sg n nom'), ('msd', 'pret_part indef sg n nom'),
                     ('msd', 'pret_part indef sg n gen'), ('msd', 'pret_part indef sg n gen'),
                     ('msd', 'pret_part indef pl nom'), ('msd', 'pret_part indef pl nom'),
                     ('msd', 'pret_part indef pl gen'), ('msd', 'pret_part indef pl gen'),
                     ('msd', 'pret_part def sg no_masc nom'), ('msd', 'pret_part def sg no_masc nom'),
                     ('msd', 'pret_part def sg no_masc gen'), ('msd', 'pret_part def sg no_masc gen'),
                     ('msd', 'pret_part def sg masc nom'), ('msd', 'pret_part def sg masc nom'),
                     ('msd', 'pret_part def sg masc gen'), ('msd', 'pret_part def sg masc gen'),
                     ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl gen'),
                     ('msd', 'pret_part def pl gen')]), ('gallrar bort', ('msd', 'pres ind aktiv'), [
        ['gallrar bort', 'gallras bort', 'gallrade bort', 'gallrades bort', 'gallra bort', 'gallra bort',
         'gallras bort', 'gallrat bort', 'gallrats bort', 'gallrande bort', 'gallrandes bort', 'gallrad bort',
         'bortgallrad', 'gallrads bort', 'bortgallrads', 'gallrat bort', 'bortgallrat', 'gallrats bort', 'bortgallrats',
         'gallrade bort', 'bortgallrade', 'gallrades bort', 'bortgallrades', 'gallrade bort', 'bortgallrade',
         'gallrades bort', 'bortgallrades', 'gallrade bort', 'bortgallrade', 'gallrades bort', 'bortgallrades',
         'gallrade bort', 'bortgallrade', 'gallrades bort', 'bortgallrades'], (
        '[gallra]r bort', '[gallra]s bort', '[gallra]de bort', '[gallra]des bort', '[gallra] bort', '[gallra] bort',
        '[gallra]s bort', '[gallra]t bort', '[gallra]ts bort', '[gallra]nde bort', '[gallra]ndes bort',
        '[gallra]d bort', 'bort[gallra]d', '[gallra]ds bort', 'bort[gallra]ds', '[gallra]t bort', 'bort[gallra]t',
        '[gallra]ts bort', 'bort[gallra]ts', '[gallra]de bort', 'bort[gallra]de', '[gallra]des bort', 'bort[gallra]des',
        '[gallra]de bort', 'bort[gallra]de', '[gallra]des bort', 'bort[gallra]des', '[gallra]de bort', 'bort[gallra]de',
        '[gallra]des bort', 'bort[gallra]des', '[gallra]de bort', 'bort[gallra]de', '[gallra]des bort',
        'bort[gallra]des'),
        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort', '1+t bort', '1+ts bort',
         '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort', 'bort+1+ds', '1+t bort', 'bort+1+t',
         '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des'], ['gallra'], 1, 0], [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'),
                                                          ('msd', 'pret ind aktiv'), ('msd', 'pret ind s-form'),
                                                          ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                                                          ('msd', 'sup aktiv'), ('msd', 'sup s-form'),
                                                          ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                                                          ('msd', 'pret_part indef sg u nom'),
                                                          ('msd', 'pret_part indef sg u nom'),
                                                          ('msd', 'pret_part indef sg u gen'),
                                                          ('msd', 'pret_part indef sg u gen'),
                                                          ('msd', 'pret_part indef sg n nom'),
                                                          ('msd', 'pret_part indef sg n nom'),
                                                          ('msd', 'pret_part indef sg n gen'),
                                                          ('msd', 'pret_part indef sg n gen'),
                                                          ('msd', 'pret_part indef pl nom'),
                                                          ('msd', 'pret_part indef pl nom'),
                                                          ('msd', 'pret_part indef pl gen'),
                                                          ('msd', 'pret_part indef pl gen'),
                                                          ('msd', 'pret_part def sg no_masc nom'),
                                                          ('msd', 'pret_part def sg no_masc nom'),
                                                          ('msd', 'pret_part def sg no_masc gen'),
                                                          ('msd', 'pret_part def sg no_masc gen'),
                                                          ('msd', 'pret_part def sg masc nom'),
                                                          ('msd', 'pret_part def sg masc nom'),
                                                          ('msd', 'pret_part def sg masc gen'),
                                                          ('msd', 'pret_part def sg masc gen'),
                                                          ('msd', 'pret_part def pl nom'),
                                                          ('msd', 'pret_part def pl nom'),
                                                          ('msd', 'pret_part def pl gen'),
                                                          ('msd', 'pret_part def pl gen')])]

    paradigmlist = collapse_tables(filtered_tables)
    assert len(paradigmlist) == 1


def test_transient2():
    filtered_tables = [('sopar bort', ('msd', 'pres ind aktiv'), [
        ['sopar bort', 'sopas bort', 'sopade bort', 'sopades bort', 'sopa bort', 'sopa bort', 'sopas bort',
         'sopat bort', 'sopats bort', 'sopande bort', 'sopandes bort', 'sopad bort', 'bortsopad', 'sopads bort',
         'bortsopads', 'sopat bort', 'bortsopat', 'sopats bort', 'bortsopats', 'sopade bort', 'bortsopade',
         'sopades bort', 'bortsopades', 'sopade bort', 'bortsopade', 'sopades bort', 'bortsopades', 'sopade bort',
         'bortsopade', 'sopades bort', 'bortsopades', 'sopade bort', 'bortsopade', 'sopades bort', 'bortsopades'], (
        '[sopa]r bort', '[sopa]s bort', '[sopa]de bort', '[sopa]des bort', '[sopa] bort', '[sopa] bort', '[sopa]s bort',
        '[sopa]t bort', '[sopa]ts bort', '[sopa]nde bort', '[sopa]ndes bort', '[sopa]d bort', 'bort[sopa]d',
        '[sopa]ds bort', 'bort[sopa]ds', '[sopa]t bort', 'bort[sopa]t', '[sopa]ts bort', 'bort[sopa]ts',
        '[sopa]de bort', 'bort[sopa]de', '[sopa]des bort', 'bort[sopa]des', '[sopa]de bort', 'bort[sopa]de',
        '[sopa]des bort', 'bort[sopa]des', '[sopa]de bort', 'bort[sopa]de', '[sopa]des bort', 'bort[sopa]des',
        '[sopa]de bort', 'bort[sopa]de', '[sopa]des bort', 'bort[sopa]des'),
        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort', '1+t bort', '1+ts bort',
         '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort', 'bort+1+ds', '1+t bort', 'bort+1+t',
         '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des'], ['sopa'], 1, 0],
                     [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'), ('msd', 'pret ind aktiv'),
                      ('msd', 'pret ind s-form'), ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                      ('msd', 'sup aktiv'), ('msd', 'sup s-form'), ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                      ('msd', 'pret_part indef sg u nom'), ('msd', 'pret_part indef sg u nom'),
                      ('msd', 'pret_part indef sg u gen'), ('msd', 'pret_part indef sg u gen'),
                      ('msd', 'pret_part indef sg n nom'), ('msd', 'pret_part indef sg n nom'),
                      ('msd', 'pret_part indef sg n gen'), ('msd', 'pret_part indef sg n gen'),
                      ('msd', 'pret_part indef pl nom'), ('msd', 'pret_part indef pl nom'),
                      ('msd', 'pret_part indef pl gen'), ('msd', 'pret_part indef pl gen'),
                      ('msd', 'pret_part def sg no_masc nom'), ('msd', 'pret_part def sg no_masc nom'),
                      ('msd', 'pret_part def sg no_masc gen'), ('msd', 'pret_part def sg no_masc gen'),
                      ('msd', 'pret_part def sg masc nom'), ('msd', 'pret_part def sg masc nom'),
                      ('msd', 'pret_part def sg masc gen'), ('msd', 'pret_part def sg masc gen'),
                      ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl gen'),
                      ('msd', 'pret_part def pl gen')]), ('jagar bort', ('msd', 'pres ind aktiv'), [
        ['jagar bort', 'jagas bort', 'jagade bort', 'jagades bort', 'jaga bort', 'jaga bort', 'jagas bort',
         'jagat bort', 'jagats bort', 'jagande bort', 'jagandes bort', 'jagad bort', 'bortjagad', 'jagads bort',
         'bortjagads', 'jagat bort', 'bortjagat', 'jagats bort', 'bortjagats', 'jagade bort', 'bortjagade',
         'jagades bort', 'bortjagades', 'jagade bort', 'bortjagade', 'jagades bort', 'bortjagades', 'jagade bort',
         'bortjagade', 'jagades bort', 'bortjagades', 'jagade bort', 'bortjagade', 'jagades bort', 'bortjagades'], (
        'jagar [bort]', 'jagas [bort]', 'jagade [bort]', 'jagades [bort]', 'jaga [bort]', 'jaga [bort]', 'jagas [bort]',
        'jagat [bort]', 'jagats [bort]', 'jagande [bort]', 'jagandes [bort]', 'jagad [bort]', '[bort]jagad',
        'jagads [bort]', '[bort]jagads', 'jagat [bort]', '[bort]jagat', 'jagats [bort]', '[bort]jagats',
        'jagade [bort]', '[bort]jagade', 'jagades [bort]', '[bort]jagades', 'jagade [bort]', '[bort]jagade',
        'jagades [bort]', '[bort]jagades', 'jagade [bort]', '[bort]jagade', 'jagades [bort]', '[bort]jagades',
        'jagade [bort]', '[bort]jagade', 'jagades [bort]', '[bort]jagades'),
        ['jagar +1', 'jagas +1', 'jagade +1', 'jagades +1', 'jaga +1', 'jaga +1', 'jagas +1', 'jagat +1', 'jagats +1',
         'jagande +1', 'jagandes +1', 'jagad +1', '1+jagad', 'jagads +1', '1+jagads', 'jagat +1', '1+jagat',
         'jagats +1', '1+jagats', 'jagade +1', '1+jagade', 'jagades +1', '1+jagades', 'jagade +1', '1+jagade',
         'jagades +1', '1+jagades', 'jagade +1', '1+jagade', 'jagades +1', '1+jagades', 'jagade +1', '1+jagade',
         'jagades +1', '1+jagades'], ['bort'], 1, 0], [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'),
                                                       ('msd', 'pret ind aktiv'), ('msd', 'pret ind s-form'),
                                                       ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                                                       ('msd', 'sup aktiv'), ('msd', 'sup s-form'),
                                                       ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                                                       ('msd', 'pret_part indef sg u nom'),
                                                       ('msd', 'pret_part indef sg u nom'),
                                                       ('msd', 'pret_part indef sg u gen'),
                                                       ('msd', 'pret_part indef sg u gen'),
                                                       ('msd', 'pret_part indef sg n nom'),
                                                       ('msd', 'pret_part indef sg n nom'),
                                                       ('msd', 'pret_part indef sg n gen'),
                                                       ('msd', 'pret_part indef sg n gen'),
                                                       ('msd', 'pret_part indef pl nom'),
                                                       ('msd', 'pret_part indef pl nom'),
                                                       ('msd', 'pret_part indef pl gen'),
                                                       ('msd', 'pret_part indef pl gen'),
                                                       ('msd', 'pret_part def sg no_masc nom'),
                                                       ('msd', 'pret_part def sg no_masc nom'),
                                                       ('msd', 'pret_part def sg no_masc gen'),
                                                       ('msd', 'pret_part def sg no_masc gen'),
                                                       ('msd', 'pret_part def sg masc nom'),
                                                       ('msd', 'pret_part def sg masc nom'),
                                                       ('msd', 'pret_part def sg masc gen'),
                                                       ('msd', 'pret_part def sg masc gen'),
                                                       ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl nom'),
                                                       ('msd', 'pret_part def pl gen'),
                                                       ('msd', 'pret_part def pl gen')]), (
                    'kollrar bort', ('msd', 'pres ind aktiv'), [
                        ['kollrar bort', 'kollras bort', 'kollrade bort', 'kollrades bort', 'kollra bort',
                         'kollra bort', 'kollras bort', 'kollrat bort', 'kollrats bort', 'kollrande bort',
                         'kollrandes bort', 'kollrad bort', 'bortkollrad', 'kollrads bort', 'bortkollrads',
                         'kollrat bort', 'bortkollrat', 'kollrats bort', 'bortkollrats', 'kollrade bort',
                         'bortkollrade', 'kollrades bort', 'bortkollrades', 'kollrade bort', 'bortkollrade',
                         'kollrades bort', 'bortkollrades', 'kollrade bort', 'bortkollrade', 'kollrades bort',
                         'bortkollrades', 'kollrade bort', 'bortkollrade', 'kollrades bort', 'bortkollrades'], (
                        '[kollra]r bort', '[kollra]s bort', '[kollra]de bort', '[kollra]des bort', '[kollra] bort',
                        '[kollra] bort', '[kollra]s bort', '[kollra]t bort', '[kollra]ts bort', '[kollra]nde bort',
                        '[kollra]ndes bort', '[kollra]d bort', 'bort[kollra]d', '[kollra]ds bort', 'bort[kollra]ds',
                        '[kollra]t bort', 'bort[kollra]t', '[kollra]ts bort', 'bort[kollra]ts', '[kollra]de bort',
                        'bort[kollra]de', '[kollra]des bort', 'bort[kollra]des', '[kollra]de bort', 'bort[kollra]de',
                        '[kollra]des bort', 'bort[kollra]des', '[kollra]de bort', 'bort[kollra]de', '[kollra]des bort',
                        'bort[kollra]des', '[kollra]de bort', 'bort[kollra]de', '[kollra]des bort', 'bort[kollra]des'),
                        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort',
                         '1+t bort', '1+ts bort', '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort',
                         'bort+1+ds', '1+t bort', 'bort+1+t', '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de',
                         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort',
                         'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des'],
                        ['kollra'], 1, 0],
                    [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'), ('msd', 'pret ind aktiv'),
                     ('msd', 'pret ind s-form'), ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                     ('msd', 'sup aktiv'), ('msd', 'sup s-form'), ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                     ('msd', 'pret_part indef sg u nom'), ('msd', 'pret_part indef sg u nom'),
                     ('msd', 'pret_part indef sg u gen'), ('msd', 'pret_part indef sg u gen'),
                     ('msd', 'pret_part indef sg n nom'), ('msd', 'pret_part indef sg n nom'),
                     ('msd', 'pret_part indef sg n gen'), ('msd', 'pret_part indef sg n gen'),
                     ('msd', 'pret_part indef pl nom'), ('msd', 'pret_part indef pl nom'),
                     ('msd', 'pret_part indef pl gen'), ('msd', 'pret_part indef pl gen'),
                     ('msd', 'pret_part def sg no_masc nom'), ('msd', 'pret_part def sg no_masc nom'),
                     ('msd', 'pret_part def sg no_masc gen'), ('msd', 'pret_part def sg no_masc gen'),
                     ('msd', 'pret_part def sg masc nom'), ('msd', 'pret_part def sg masc nom'),
                     ('msd', 'pret_part def sg masc gen'), ('msd', 'pret_part def sg masc gen'),
                     ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl nom'), ('msd', 'pret_part def pl gen'),
                     ('msd', 'pret_part def pl gen')]), ('gallrar bort', ('msd', 'pres ind aktiv'), [
        ['gallrar bort', 'gallras bort', 'gallrade bort', 'gallrades bort', 'gallra bort', 'gallra bort',
         'gallras bort', 'gallrat bort', 'gallrats bort', 'gallrande bort', 'gallrandes bort', 'gallrad bort',
         'bortgallrad', 'gallrads bort', 'bortgallrads', 'gallrat bort', 'bortgallrat', 'gallrats bort', 'bortgallrats',
         'gallrade bort', 'bortgallrade', 'gallrades bort', 'bortgallrades', 'gallrade bort', 'bortgallrade',
         'gallrades bort', 'bortgallrades', 'gallrade bort', 'bortgallrade', 'gallrades bort', 'bortgallrades',
         'gallrade bort', 'bortgallrade', 'gallrades bort', 'bortgallrades'], (
        '[gallra]r bort', '[gallra]s bort', '[gallra]de bort', '[gallra]des bort', '[gallra] bort', '[gallra] bort',
        '[gallra]s bort', '[gallra]t bort', '[gallra]ts bort', '[gallra]nde bort', '[gallra]ndes bort',
        '[gallra]d bort', 'bort[gallra]d', '[gallra]ds bort', 'bort[gallra]ds', '[gallra]t bort', 'bort[gallra]t',
        '[gallra]ts bort', 'bort[gallra]ts', '[gallra]de bort', 'bort[gallra]de', '[gallra]des bort', 'bort[gallra]des',
        '[gallra]de bort', 'bort[gallra]de', '[gallra]des bort', 'bort[gallra]des', '[gallra]de bort', 'bort[gallra]de',
        '[gallra]des bort', 'bort[gallra]des', '[gallra]de bort', 'bort[gallra]de', '[gallra]des bort',
        'bort[gallra]des'),
        ['1+r bort', '1+s bort', '1+de bort', '1+des bort', '1+ bort', '1+ bort', '1+s bort', '1+t bort', '1+ts bort',
         '1+nde bort', '1+ndes bort', '1+d bort', 'bort+1+d', '1+ds bort', 'bort+1+ds', '1+t bort', 'bort+1+t',
         '1+ts bort', 'bort+1+ts', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de', '1+des bort', 'bort+1+des', '1+de bort', 'bort+1+de',
         '1+des bort', 'bort+1+des'], ['gallra'], 1, 0], [('msd', 'pres ind aktiv'), ('msd', 'pres ind s-form'),
                                                          ('msd', 'pret ind aktiv'), ('msd', 'pret ind s-form'),
                                                          ('msd', 'imper'), ('msd', 'inf aktiv'), ('msd', 'inf s-form'),
                                                          ('msd', 'sup aktiv'), ('msd', 'sup s-form'),
                                                          ('msd', 'pres_part nom'), ('msd', 'pres_part gen'),
                                                          ('msd', 'pret_part indef sg u nom'),
                                                          ('msd', 'pret_part indef sg u nom'),
                                                          ('msd', 'pret_part indef sg u gen'),
                                                          ('msd', 'pret_part indef sg u gen'),
                                                          ('msd', 'pret_part indef sg n nom'),
                                                          ('msd', 'pret_part indef sg n nom'),
                                                          ('msd', 'pret_part indef sg n gen'),
                                                          ('msd', 'pret_part indef sg n gen'),
                                                          ('msd', 'pret_part indef pl nom'),
                                                          ('msd', 'pret_part indef pl nom'),
                                                          ('msd', 'pret_part indef pl gen'),
                                                          ('msd', 'pret_part indef pl gen'),
                                                          ('msd', 'pret_part def sg no_masc nom'),
                                                          ('msd', 'pret_part def sg no_masc nom'),
                                                          ('msd', 'pret_part def sg no_masc gen'),
                                                          ('msd', 'pret_part def sg no_masc gen'),
                                                          ('msd', 'pret_part def sg masc nom'),
                                                          ('msd', 'pret_part def sg masc nom'),
                                                          ('msd', 'pret_part def sg masc gen'),
                                                          ('msd', 'pret_part def sg masc gen'),
                                                          ('msd', 'pret_part def pl nom'),
                                                          ('msd', 'pret_part def pl nom'),
                                                          ('msd', 'pret_part def pl gen'),
                                                          ('msd', 'pret_part def pl gen')])]
    paradigmlist = collapse_tables(filtered_tables)
    assert len(paradigmlist) == 2