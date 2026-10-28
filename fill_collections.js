async (page) => {
  const BASE = [45,60,80,39,58,78,44,59,79,45,50,60,40,45,65,40,63,83,30,55,40,65,35,60,35,60,50,75,55,70,90,46,61,81,70,95,38,73,115,140,40,75,45,60,75,35,60,60,70,10,35,40,65,50,80,40,65,55,90,40,65,90,25,40,55,70,80,90,50,65,80,40,80,40,55,80,40,50,55,90,90,25,50,52,35,60,35,60,65,80,40,55,80,40,50,55,90,100];
  const sets = {};
  sets.dexhp = ['0', ...BASE.map(b => String(Math.round(b / 3) + 13))].join('
');
  const evoMap = {1:[2,16],2:[3,32],4:[5,16],5:[6,36],7:[8,16],8:[9,36],10:[11,7],11:[12,10],13:[14,7],14:[15,10],16:[17,18],17:[18,36],19:[20,20],21:[22,20],23:[24,22],25:[26,30],27:[28,22],29:[30,16],32:[33,16],33:[34,36],35:[36,25],37:[38,25],39:[40,25],41:[42,22],43:[44,21],44:[45,28],46:[47,24],48:[49,31],50:[51,26],52:[53,28],54:[55,33],56:[57,28],58:[59,30],60:[61,25],63:[64,16],64:[65,36],66:[67,28],69:[70,21],70:[71,30],72:[73,30],74:[75,25],75:[76,36],77:[78,40],79:[80,37],81:[82,30],84:[85,31],86:[87,34],88:[89,38],90:[91,36],92:[93,25],93:[94,36],96:[97,26],98:[99,28],100:[101,30],102:[103,30],104:[105,28],109:[110,38],111:[112,42],116:[117,32],118:[119,33],120:[121,36],129:[130,20],138:[139,40],140:[141,40],147:[148,30],148:[149,55]};
  const A = {1: ['0'], 2: ['0'], 3: ['0'], 4: ['0']};
  const P = {1: ['0'], 2: ['0'], 3: ['0'], 4: ['0']};
  const EV = ['0'], EL = ['0'];
  for (let dex = 1; dex <= 151; dex++) {
    const ii = (dex * 7) % 150;
    let aa = [1, (ii % 4) + 2, (dex % 2) ? 3 : 4, (ii % 5) + 1];
    if (dex % 4 === 0) aa = [1, 2, 3, 5];
    for (let k = 1; k <= 4; k++) {
      A[k].push(String(aa[k - 1]));
      P[k].push(String(k === 1 ? ((ii * 3) % 6) + 5 : k === 2 ? (ii % 9) + 14 : k === 3 ? (ii % 5) + 5 : (ii % 3) + 1));
    }
    const e = evoMap[dex];
    EV.push(e ? String(e[0]) : '0');
    EL.push(e ? String(e[1]) : '0');
  }
  sets.dexa1 = A[1].join('
'); sets.dexa2 = A[2].join('
');
  sets.dexa3 = A[3].join('
'); sets.dexa4 = A[4].join('
');
  sets.dexp1 = P[1].join('
'); sets.dexp2 = P[2].join('
');
  sets.dexp3 = P[3].join('
'); sets.dexp4 = P[4].join('
');
  sets.dexev = EV.join('
'); sets.dexel = EL.join('
');
  const roll = ['0'];
  for (let dex = 1; dex <= 150; dex++) roll.push(String(dex));
  sets.dexroll = roll.join('
');
  const d20v = [];
  for (let k = 1; k <= 20; k++) d20v.push(String(k));
  sets.d20 = d20v.join('
');
  const NAMES = ["Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard","Squirtle","Wartortle","Blastoise","Caterpie","Metapod","Butterfree","Weedle","Kakuna","Beedrill","Pidgey","Pidgeotto","Pidgeot","Rattata","Raticate","Spearow","Fearow","Ekans","Arbok","Pikachu","Raichu","Sandshrew","Sandslash","Nidoran F","Nidorina","Nidoqueen","Nidoran M","Nidorino","Nidoking","Clefairy","Clefable","Vulpix","Ninetales","Jigglypuff","Wigglytuff","Zubat","Golbat","Oddish","Gloom","Vileplume","Paras","Parasect","Venonat","Venomoth","Diglett","Dugtrio","Meowth","Persian","Psyduck","Golduck","Mankey","Primeape","Growlithe","Arcanine","Poliwag","Poliwhirl","Poliwrath","Abra","Kadabra","Alakazam","Machop","Machoke","Machamp","Bellsprout","Weepinbell","Victreebel","Tentacool","Tentacruel","Geodude","Graveler","Golem","Ponyta","Rapidash","Slowpoke","Slowbro","Magnemite","Magneton","Farfetchd","Doduo","Dodrio","Seel","Dewgong","Grimer","Muk","Shellder","Cloyster","Gastly","Haunter","Gengar","Onix","Drowzee","Hypno","Krabby","Kingler","Voltorb","Electrode","Exeggcute","Exeggutor","Cubone","Marowak","Hitmonlee","Hitmonchan","Lickitung","Koffing","Weezing","Rhyhorn","Rhydon","Chansey","Tangela","Kangaskhan","Horsea","Seadra","Goldeen","Seaking","Staryu","Starmie","Mr Mime","Scyther","Jynx","Electabuzz","Magmar","Pinsir","Tauros","Magikarp","Gyarados","Lapras","Ditto","Eevee","Vaporeon","Jolteon","Flareon","Porygon","Omanyte","Omastar","Kabuto","Kabutops","Aerodactyl","Snorlax","Articuno","Zapdos","Moltres","Dratini","Dragonair","Dragonite","Mewtwo","Mew"];
  sets.pokenames = NAMES.join('
');
  const order = ['dexhp','dexa1','dexa2','dexa3','dexa4','dexp1','dexp2','dexp3','dexp4','dexev','dexel','dexroll','d20','pokenames'];
  const results = {};
  for (const ref of order) {
    try {
      const search = page.getByRole('textbox', { name: 'Search variables' });
      await search.fill(ref);
      await page.waitForTimeout(300);
      await page.getByRole('button', { name: new RegExp('^' + ref) }).first().click();
      await page.waitForTimeout(300);
      await page.getByRole('button', { name: 'Values', exact: true }).first().click({ timeout: 2500 });
      await page.waitForTimeout(300);
      await page.locator('[aria-labelledby="variable-values-title"] button[title="Edit value"]').first().click({ timeout: 2500 });
      await page.waitForTimeout(250);
      const ta = page.locator('[aria-labelledby="variable-values-title"] textarea').first();
      await ta.fill(sets[ref]);
      await page.getByRole('button', { name: 'Save', exact: true }).first().click({ timeout: 2500 });
      await page.waitForTimeout(500);
      try { await page.locator('[aria-labelledby="variable-values-title"] button[title="Close"]').first().click({ timeout: 2000 }); } catch (e) {}
      await page.waitForTimeout(200);
      results[ref] = 'done';
    } catch (e) {
      results[ref] = 'ERR ' + String(e).slice(0, 60);
      try { await page.evaluate(() => { const d = document.querySelector('[aria-labelledby="variable-values-title"]'); const c = d && [...d.querySelectorAll('button')].find(b => (b.getAttribute('title') || '') === 'Close'); if (c) c.click(); }); } catch (e2) {}
    }
  }
  const check = await page.evaluate(async () => {
    const refs = ['pokenames','dexhp','dexa1','dexa2','dexa3','dexa4','dexp1','dexp2','dexp3','dexp4','dexev','dexel','dexroll','d20'];
    const out = {};
    for (const ref of refs) {
      const r = await fetch('/api/datastorage/entries', {
        method: 'POST', credentials: 'include',
        headers: { 'content-type': 'application/json', 'accept': 'application/json' },
        body: JSON.stringify({ bot_id: '1516431880323338382', reference: ref })
      });
      const j = await r.json();
      const e = j.entries && j.entries[0];
      out[ref] = e && Array.isArray(e.value) ? e.value.length : 'none';
    }
    return out;
  });
  return { results, check };
}