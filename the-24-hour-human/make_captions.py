"""Gera o .vtt de um video de persona transcrevendo o audio do proprio video.

Legenda e requisito WCAG 1.2.2 (nivel A) para fala gravada, e era o unico
criterio basico que a pagina ainda quebrava. O texto vem da transcricao real,
nunca escrito a mao: legenda errada e pior que legenda nenhuma, porque quem
depende dela nao tem como saber que esta errada.

Uso:
    python3 -m venv /tmp/vtt-venv
    /tmp/vtt-venv/bin/pip install faster-whisper
    /tmp/vtt-venv/bin/python make_captions.py assets/video/jpn.mp4

Escreve o .vtt ao lado do .mp4, que e onde o dashboard procura. Depois disso
o venv e o cache do modelo (~/.cache/huggingface) podem ser apagados.

Regras de legendagem aplicadas sobre a transcricao:
- uma frase por cue, para o texto nao adiantar a fala
- cada cue segura a tela ate pouco antes do proximo, ocupando a pausa
- no maximo 2 linhas por cue, 37 caracteres por linha
- nenhum cue passa de 6s (recomendacao para leitor adulto) nem de 24 car/s
- quebra de linha equilibrada, preferindo cair depois de pontuacao
- corte de frase longa so em fronteira de palavra, com o tempo real da palavra
"""
import re
import sys
from pathlib import Path

MAX_LINE, MAX_LINES, MAX_DUR, MAX_CPS = 37, 2, 6.0, 24.0
LEAD_OUT = 0.08          # intervalo minimo entre um cue e o proximo
MAX_CHARS = MAX_LINE * MAX_LINES

# Whisper escreve o que ouve; estas trocas so acertam grafia, nunca palavra: a
# pagina usa ortografia britanica ("organises"), e numero de quatro digitos
# aparece com separador de milhar em todo o resto do dashboard.
FIX = {"1487": "1,487", "2181": "2,181", "cafe": "café",
       "neighbor": "neighbour", "favor": "favour", "color": "colour",
       "organize": "organise"}

# Erros de reconhecimento, nao de escrita: sao trocas de palavra que mudam o
# sentido, e cada uma foi conferida contra os CSVs antes de entrar aqui. Sem
# elas a pagina afirma coisa errada na tela.
PHRASE_FIX = [
    # Camille falava do trabalho invisivel; FRA tem upw = 3h01, "on paid" nao existe
    ("three hours on paid work", "three hours of unpaid work"),
    # ZAF tem paw = 4h01, entao e "four", nao a preposicao
    ("For hours and 1 minute", "Four hours and 1 minute"),
    # o assunto e 2.181 horas por ano
    ("longest work here of", "longest work year of"),
    # o lazer do Thabo (5h06) e o maior dos cinco, entao a comparacao e com as
    # outras quatro pessoas e nao com anos
    ("any of the other 4 years", "any of the other four"),
    # frase que o Whisper cortou no meio
    ("The morning is my.", "The morning is mine."),
    # nomes
    ("Ruto and Sofia", "Haruto and Sofía"),
    ("Sophia", "Sofía"),
    ("Sofia", "Sofía"),
]


def norm(word):
    """Normaliza grafia de uma palavra sem trocar a palavra."""
    bare = word.strip()
    core = bare.strip('.,!?"\u2019')
    repl = FIX.get(core.lower())
    if repl:
        if core[:1].isupper():
            repl = repl[:1].upper() + repl[1:]
        return bare.replace(core, repl)
    return bare


FIRED = set()


def text_of(words):
    """Junta as palavras e limpa artefatos de tokenizacao.

    Whisper as vezes devolve um numero decimal em dois tokens ("5" + ".6"), solta
    a pontuacao da palavra ou separa o hifen, e isso vaza para a tela como
    "5 .6 years" ou "24 -hour".
    """
    t = " ".join(norm(w.word) for w in words)
    t = re.sub(r"(\d)\s+\.\s*(\d)", r"\1.\2", t)      # 5 .6  -> 5.6
    t = re.sub(r"\s+-\s*(\w)", r"-\1", t)             # 24 -hour -> 24-hour
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)            # word , -> word,
    t = re.sub(r"\s{2,}", " ", t).strip()
    for wrong, right in PHRASE_FIX:
        if wrong in t:
            t = t.replace(wrong, right)
            FIRED.add(wrong)
    return t


def wrap(text):
    """Duas linhas equilibradas, preferindo quebrar depois de pontuacao."""
    if len(text) <= MAX_LINE:
        return [text]
    words = text.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) > MAX_LINE or len(b) > MAX_LINE:
            continue
        score = abs(len(a) - len(b)) - (6 if a[-1] in ".,;:!?" else 0)
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1] if best else None


def split_words(words):
    """Fatia uma fala em pedacos que todos caibam nas regras, cortando em palavra.

    So corta quando o texto realmente nao couber: e o proprio wrap() que decide,
    nao uma contagem de caracteres. Contar caracteres erra, porque 74 caracteres
    cabem em duas linhas de 37 apenas se existir fronteira de palavra no lugar
    certo -- "But here's something important. Japanese women carry a much bigger
    share," tem 73 e nao cabe, ja que a primeira linha so pode fechar em
    "important." e o resto passa de 37.

    Cortar por velocidade de leitura foi tentado e sai pior: as falas aqui sao
    frases curtas, e dividir uma delas deixa um orfao de duas palavras na tela
    por menos de um segundo, que le pior do que a frase inteira um pouco rapida.
    """
    text = text_of(words)
    dur = words[-1].end - words[0].start
    if len(words) < 2 or (wrap(text) is not None and dur <= MAX_DUR):
        return [words]
    # Melhor ponto de corte: o mais perto do meio, com desconto forte para
    # pontuacao e penalidade para cortar dentro de uma quantidade. Sem essa
    # penalidade sai "leisure is 1" / "hour and 19 minutes" e "works 2,181" /
    # "hours a year", com o numero numa tela e a unidade na seguinte.
    target, acc, best = len(text) / 2, 0, None
    for i, w in enumerate(words[:-1]):
        here, nxt = norm(w.word), norm(words[i + 1].word)
        acc += len(here) + 1
        score = abs(acc - target)
        if here[-1:] in ".,;:!?":
            score -= 14
        if re.search(r"\d$", here) or re.match(r"^(and|of|a|the|per|to)$", nxt, re.I) \
                or re.match(r"^(hour|hours|minute|minutes|day|days|year|years)\b", nxt, re.I):
            score += 40
        if best is None or score < best[0]:
            best = (score, i + 1)
    cut = best[1]
    return split_words(words[:cut]) + split_words(words[cut:])


def sentences(words):
    """Agrupa palavras em frases. Um cue que comeca e termina numa frase le muito
    melhor do que um cue cortado no meio dela, e o tamanho dos segmentos que o
    Whisper devolve varia demais entre videos para servir de fronteira: no de
    Camille vieram frases inteiras, no de Haruto vieram corridas de tres frases.
    """
    out, buf = [], []
    for w in words:
        buf.append(w)
        token = norm(w.word)
        # ".6" de um decimal nao fecha frase; letra ou ) antes do ponto, sim
        if re.search(r"[A-Za-z0-9)\"'\u2019][.!?]+[\"'\u2019]?$", token) \
                and not re.match(r"^\.\d", token):
            out.append(buf)
            buf = []
    if buf:
        out.append(buf)
    return out


def hold(cues, media_end):
    """Estica cada cue ate pouco antes do proximo comecar.

    Whisper devolve o intervalo em que a palavra soa, e nada mais. Usar isso como
    duracao do cue faz "You want to know how my day goes?" caber em 1,24s, ou seja
    27 caracteres por segundo, ilegivel -- quando na verdade existe meio segundo de
    respiro antes da frase seguinte que ninguem esta usando. Legendagem normal
    ocupa esse respiro e deixa so um intervalo minimo entre cues.

    Isso resolve a velocidade de leitura sem juntar frases, que era a alternativa
    e sai pior: juntar por cima de uma pausa faz a segunda frase aparecer escrita
    antes de ser dita.
    """
    out = []
    for i, (start, end, text) in enumerate(cues):
        # o ultimo cue tambem para antes do fim: a duracao que o Whisper reporta
        # arredonda para cima e passa alguns milissegundos do container, o que
        # deixaria o .vtt terminando depois do video
        limit = (cues[i + 1][0] if i + 1 < len(cues) else media_end) - LEAD_OUT
        out.append((start, max(end, min(limit, start + MAX_DUR)), text))
    return out


def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def build(src: Path, model_size="small"):
    from faster_whisper import WhisperModel

    out = src.with_suffix(".vtt")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(src), beam_size=5, vad_filter=True,
                                      word_timestamps=True)
    print(f"{src.name}: language={info.language} ({info.language_probability:.2f}), "
          f"{info.duration:.1f}s")

    words = [w for seg in segments for w in (seg.words or []) if w.word.strip()]
    if not words:
        sys.exit(f"{src.name}: no speech found, nothing written")

    cues = []
    for group in sentences(words):
        for chunk in split_words(group):
            cues.append((chunk[0].start, chunk[-1].end, text_of(chunk)))
    cues = hold(cues, info.duration)

    # nenhum cue pode comecar antes do anterior terminar
    for i in range(1, len(cues)):
        prev, cur = cues[i - 1], cues[i]
        if cur[0] < prev[1]:
            cues[i] = (prev[1], max(cur[1], prev[1] + .4), cur[2])

    body = ["WEBVTT", "", "NOTE",
            "Transcribed from the narration in this video. Every figure the",
            "speaker states matches the OECD time-use data behind this page.", ""]
    worst = 0.0
    for i, (start, end, text) in enumerate(cues, 1):
        lines = wrap(text)
        assert lines, f"cue {i} will not fit two lines: {text!r}"
        cps = len(text) / max(end - start, .01)
        worst = max(worst, cps)
        assert end - start <= MAX_DUR + .01, f"cue {i} runs {end - start:.1f}s"
        assert cps <= MAX_CPS, f"cue {i} reads at {cps:.1f} chars/s: {text!r}"
        body += [str(i), f"{ts(start)} --> {ts(end)}", *lines, ""]

    # gravar por ultimo, depois de todos os asserts: um assert que falha antes do
    # write descarta o trabalho todo em silencio
    out.write_text("\n".join(body), encoding="utf-8")
    print(f"{len(cues)} cues, worst reading rate {worst:.1f} chars/s -> {out}")
    if FIRED:
        print("  correcoes aplicadas: " + "; ".join(sorted(FIRED)))
    print("Check the text against the audio before committing: the transcription "
          "is good, not perfect.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"not found: {path}")
    build(path.resolve())
