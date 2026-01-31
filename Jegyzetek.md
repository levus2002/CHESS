Ez nem a doksi, csak ami eszembe jut, hogy ne felejtsem el később. Meg doksi írásnál remélhetőleg használható lesz.

Szabályok:
Nincs lépéskötelezettség sakkadás miatt, például sakkban lévő király, nem kötelező feloldani a sakkot, de ha nemteszed leüthetik a királyod és vesztettél. Vagy lekötött figuráddal ellépsz és így sakkba kerül a királyod. Ez, ha nem is szükséges de rengeteg szélsőeset feloldását nyújtja, minimális negatívumokkal.
Pozitívumok illetve negatívumok(érzésre/hipotézis):
implicit csapatjáték
Kötésláncok elkerülése
1 lépés "grace period" ha többen támadnak egy játékost, ezt ábrával egyszerűbb lenne magyarázni
Király player1 most lépett és most következik, a 3 bástya a 3 másik player egy egy bástyája
BB    B     BB               B                Ez már matt lenne, de player1 kap még egy lépést
||    |     ||               |                
ˇˇ    ˇ     ˇˇ 
PP          PP              BP                BB

K           K     B         K      B          K        B


Evaluations fájlok, betanítás közben az ágens lépéseit kiértékelni az anyag nyereség/veszteség nem elégséges, a különböző figuráknak különböző heurisztikus módszerekkel megpróbálom közelíteni az értékét. Vigyázva, hogy alacsonyan tartsam a szükséges komputációt, és elkerüljem a túltanulást.

gyalog:
    centrumban értékesebb
    szabadgyalog
    izolált gyalog
    szabad gyalog
    dupla gyalog

huszár:
    hány érintett mező van a táblán belül, 2 személyes sakkban pálya szélén lévő huszár, csak 4 mezőt támad. 4 személyes sakktáblán van mező ahonnan csak 2 mezőt tud támadni.

Futó:
    hány mezőt támad, végjáték elméletben még szerepet szokott játszani, hogy másik játékosok bábui milyen színű mezőkön állnak, de ennek a figyelembevétele túlzásnak érződik 

Bástya:
    hány mezőt támad, 

Vezér:
    hány mezőt támad

Király:
    ütésben van e
    hány irányból védett