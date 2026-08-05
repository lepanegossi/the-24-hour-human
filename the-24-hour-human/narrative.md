# The 24-Hour Human — Narrative Script

**Objetivo:** dar ao dashboard um arco com começo, meio e fim (critério Storytelling = 30%).
Textos em inglês (idioma da submissão). Revisar/ajustar antes de eu colar no `build_dashboard.py`.

## A tese (o fio condutor)
> Every person on Earth is handed the exact same thing each morning: **1,440 minutes**. It is the one resource the world shares perfectly equally. But *where* you are born quietly rewrites how you spend them — how long you work, rest, care for others, and play. And when we follow the data, one truth stands out: growing richer buys back free time… but it doesn't share the load equally between women and men.

Arco: **pessoal → mundo → trabalho → o fardo invisível (clímax) → o tempo de uma vida → o futuro → reflexão**.

---

## 1. HERO — "The 24-Hour Human" ✅ IMPLEMENTADO
**Kicker:** An interactive data story · VizCon 2026
**Elemento visual:** relógio analógico girando (SVG animado) no topo.
**Texto (final):**
> What can you do in 24 hours? And what does the rest of the world do with theirs? Discover how many hours we work, how much time we keep for leisure, and how the place you live shapes what your day looks like. All inside the same 1,440 minutes each of us is given, every single day.

## 2. QUIZ — "Which human are you?" ✅ IMPLEMENTADO (estilo Tinder)
**Intro (final):**
> Before we begin, let's figure out your ideal day. Slide each bar to what feels best for you: give more time to what matters most, and less to what matters least. Think about what motivates you and makes you happiest. Then, just like Tinder, we'll reveal your perfect match: which of the 35 countries around the world would give you your 'perfect day'. So... who's your match?

**Resultado = card "It's a match!" (estilo Tinder):** banner rosa/laranja com coração pulsando, bandeira do país como foto de perfil, "You matched with {country}!", badge de % de compatibilidade (`max(80, min(99, 100 - dist*6))`), stats + relógio de 24h. Botão: "Who's my match? 💘".

**Texto pós-resultado (aparece junto do match):**
> Your day isn't just yours. Millions of people half a world away wake to almost the same rhythm. Time use is personal, but it's also deeply cultural. Keep that in mind as we zoom out.

## 3. PERSONAS — "One day, five lives" ✅ IMPLEMENTADO (intro sem citar as pessoas)
**Texto (final):**
> Meet our neighbors from around the world, one from each continent. Here's where you'll see how a single day can look completely different depending on where you stand, and how that everyday routine really plays out across the globe. What could each place add to your own day? (Each ring is one real 24-hour day; hover to explore the hours.)

**Cards das personas (final):** cada card tem assinatura (traço em destaque) + mini-bio com ficção leve ancorada no dado real:
- 🇫🇷 Camille: croissant + café sem pressa; as refeições mais longas do mundo, manhãs sem pressa, aposenta ~61.
- 🇯🇵 Haruto: alarme cedo, ramen entre turnos; mais trabalho pago que todos, trabalha até ~71.
- 🇲🇽 Sofía: mal senta entre trabalho e casa; o dia mais cheio, merece um spa day; aposenta início dos 70.
- 🇦🇺 Mia: trabalho de manhã, ondas ao pôr do sol; dia equilibrado, para ~65.
- 🇿🇦 Thabo: ano mais longo, mas encontra amigos após o expediente; maior carga anual, menor renda, aposenta ~63.

## 4. GLOBE — "Where people spend their time" ✅ IMPLEMENTADO
**Texto (final):**
> So, how's the world out there? Each dot is a country we mapped, colored from yellow (fewer work hours) to red (more) across the year. Spin it and a pattern shows up: the busy red dots cluster where incomes are lower, while the calmer yellow ones sit among the wealthy. Find the country you're curious about and dive deep: click it to open its 24-hour day. (It's a little sad, but you'll spot a gap over South America. The honest limit of our data.)

## 5. SCREEN 1 — "Who works the most?"
**Texto:**
> Here's the first surprise. People in Mexico, China, Japan and South Korea spend nearly twice as long at paid work each day as those in Italy, France or Spain. It flips the usual assumption: the hardest-working nations aren't the richest — they're often the ones still climbing. Wealth, it turns out, is what lets a country ease off the clock.

## 6. SCREEN 2 — "The double shift" (CLÍMAX) ✅ IMPLEMENTADO
**Texto (final, une PT da leiteca + dados):**
> The double shift, and one stubborn question: why is it almost always women? There's a second shift, the invisible one: cooking, cleaning, raising children, caring for elders. It never shows on a payslip, it sits outside policy indicators, and it stays out of the conversation. Around the world it lands overwhelmingly on women. In India, women do about five more hours of unpaid work every single day than men. Turkey, Portugal and Mexico aren't far behind, while only the Nordics come close to sharing it evenly. Calling women strong and empowered doesn't erase those extra hours. This is the part of the day the economy never counts, the part that shapes millions of lives most, and it's long past time we talked about it as a society.

## 7. SCREEN 3 — "Working until when?"
**Texto:**
> A day is a life in miniature. Stretch it out and the same divide appears in when people finally stop working. A man in South Korea works, on average, until 72; in Luxembourg or France, until barely 60 — nearly twelve years apart. The same 1,440 minutes, repeated across a lifetime, add up to very different lives.

## 8. SCREEN 4 — "Work vs. free time"
**Texto:**
> Put a whole year on one axis and daily leisure on the other, and the trade-off is undeniable: the more a nation works over the year, the less it plays each day. Our five humans sit at very different points on that line — proof that "a full day" means something different depending on where you stand.

## 9. PREDICTIVE — "The day of 2050"
(intro já existe; manter, é forte). Só reforçar a ponte:
> So what happens if the world grows richer? We taught a simple model the link between income and time, then let each country grow. The good news: prosperity tends to hand back free time. The catch: it barely touches the second shift. Money can shorten the workday — but only people and policy can share the invisible one.

## 10. CLOSING — "How will you spend yours?" (novo — call-to-reflection)
**Seção final (antes ou depois do "How we used AI"):**
> 1,440 minutes. It's the fairest thing the world gives us and the most unequal thing we do with it. Some of that is wealth, some is culture, and a stubborn share of it is who does the unpaid, unseen work that holds everything together. The day is the smallest unit of a life — and how the world spends it is how the world lives. The only question left is the one you started with: how will you spend yours?

---

## Onde detalhar mais (pedido da leiteca)
- **Quiz:** intro expandida + texto pós-resultado (acima). Opcional: micro-frase por faixa (ex: "You're a night-owl worker" conforme os sliders).
- **Cada seção:** subir de "1 linha" pra 1 parágrafo narrativo (textos acima).
- **Fechamento novo (seção 10):** o "so what" que o vencedor tem e o nosso ainda não.
- **Tom:** descoberta + números concretos + uma pergunta que fica na cabeça.

## Próximo passo
Você revisa/ajusta os textos aqui → eu colo no `build_dashboard.py` (cada seção ganha um `<p class="sub">` ou um bloco de narrativa) e regenero.


---

## ATUALIZAÇÃO 2026-08 — reordenação + textos finais das telas 3 e 4
Ordem final das telas: Who works most → The double shift → **Work vs. free time** → **Working until when?** → The day of 2050 → How will you spend yours.
(Aposentadoria movida pra DEPOIS de work vs free time.)

### Work vs. free time (agora Screen 3, tom "amigos")
> Remember our five friends? Here's where each of them lands when we weigh a whole year of work against their daily free time. The more a country works across the year, the less it plays each day. Camille takes it slow, Sofía barely catches a break, and the others fall somewhere in between. Same 24 hours, very different lives.
Gráfico: scatter horas/ano × lazer/dia, personas destacadas.

### Working until when? (agora Screen 4, estrada com placas WORK/RETIRE)
> Do you already know when you'll stop working? With day after day of work piling up over the years, at some point that question arrives. Every choice in your day leads to the moment you'll have to decide between two worlds. Or the blend of both? Across the world, that exit comes nearly twelve years apart: South Korea keeps going until 72, while Luxembourg and France stop at barely 60.
Gráfico: ESTRADA (asfalto + faixa amarela) + placas verdes rodovia (← RETIRE / WORK →) + bandeiras por idade de aposentadoria (beeswarm, 60 a 72).


---

## ATUALIZAÇÃO — Seção final "The takeaway" (com enquete) ✅ IMPLEMENTADO
**Título:** At the end of the day, how do you feel?
**Texto (do PT da leiteca):**
> When your day ends, is it a feeling of a job well done, or of pure exhaustion? Your gender, your culture, and the country you live in can tip that balance, for better or worse. A single day is such a short thing next to a whole life. For the life you want now, and the one you want later, have you ever stopped to think about what really matters? How do you live your day?

**Enquete interativa:** "When your day ends, how do you usually feel?" com 4 opções (😌 Accomplished / 😮‍💨 Exhausted / 🤷 A bit of both / ⏳ Too busy to notice). Ao votar, barras mostram a % e a escolha fica destacada.
- **Persistência:** votos contados por dispositivo via `localStorage` (chaves `tfhh_poll_v1` / `tfhh_poll_mine`).
- ⚠️ **Pra agregação global (todos os visitantes) precisa de um backend simples** (ex: serviço de enquete ou função serverless). Front-end (Let) pode plugar depois.


---

## ATUALIZAÇÃO 2026-08 — gênero no lazer + reordenação personas/quiz ✅ IMPLEMENTADO

### The double shift agora tem gráficos gêmeos (dupla penalização)
Dois gráficos lado a lado (top10 países por gap de trabalho não-pago):
- 🏠 **Unpaid work / day** (women do more)
- 🛋️ **Leisure / day** (men get more)
A simetria deixa visível: as mesmas mulheres que trabalham mais em casa também descansam menos.

**Ponto adicionado ao texto (final):**
> ...only the Nordics come close to sharing it evenly. **And the penalty is double: those same women also get less time to rest. In Portugal and Italy, men enjoy almost an hour and a half more leisure every single day.** Calling women strong and empowered doesn't erase those extra hours...

### Ordem invertida: personas ANTES do quiz
Nova sequência de abertura: **HERO → One day, five lives (personas) → Which human are you? (quiz) → Globe → ...**
(Antes o quiz vinha primeiro. Agora o visitante conhece as 5 pessoas antes de descobrir o próprio match.)

**Textos de transição do quiz ajustados pra nova ordem:**
- Selo: "Start here" → **"Now your turn"**
- Abertura: "Before we begin..." → **"Now that you've met them, let's figure out your ideal day..."**
