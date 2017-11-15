### Taggar (bugg?)
- Hanteringa av taggar: de slås i nuläget ihop på ett sätt som tappar kunskap.

Exempelinput:
```
  lyster	msd=V0IPA
  lyster	msd=V0IPX

  månde	msd=V0S**
  månde	msd=V0S*X
  ```
Output:

```1:msd=V0IPA#1:msd=V0IPX	1=månde#1=lyster```

Tabellerna har slagits ihop, trots olika taggar. Taggarna hos det andra ordet är borta.




### Problematiska fall
- Genitiv-s
- Fördubbling/bortfall

   - ofta- ofta(a)st
   - grumla - grum+m+el
   - pryd - prytt vs. brydd - brytt (1+d - 1+tt vs. 1+dd - 1+tt)
   - svagt e: kackla

- Tomma variabler tillåts ej: **and** kan inte höra till samma paradigm som **tand**
pga variabel 1 (tand='.+'+"a"+'.+').

### Extra information i tabellen
- Avstavningsinformation (kan eventuellt hanteras utanför böjningen)
- Ledtexter (kan eventuellt hanteras utanför böjningen)
- Markera vissa former: hantera att vissa ord inte är "bruksenliga" (skillnaden mellan 2- och 3-ställiga bklasser i saol)

### Uppdelning av ingångar i tabeller

#### Sammansättningsformer
Ska de vara med eller ej?

####  Vacklande genus
Egen tabell eller del av en böjning?

#### Variantformer

Enstaka vs. konsekventa varianter som hör till ett lemma/lemgram.

Enstaka: "parti" i bestämd form singular: "partit"/"partiet"

Konsekventa: "café" kan stavas "kafé"

Saldo: enstaka => en tabell, konsekventa => flera tabeller

