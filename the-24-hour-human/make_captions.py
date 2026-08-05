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
- no maximo 2 linhas por cue, 37 caracteres por linha
- nenhum cue passa de 6s (recomendacao para leitor adulto)
- quebra de linha equilibrada, preferindo cair depois de pontuacao
- corte de cue so em fronteira de palavra, com o tempo real daquela palavra
"""
import math
import sys
from pathlib import Path

MAX_LINE, MAX_LINES, MAX_DUR, MAX_CPS = 37, 2, 6.0, 24.0
MAX_CHARS = MAX_LINE * MAX_LINES

# Whisper escreve o que ouve; estas trocas so acertam grafia, nunca palavra: a
# pagina usa ortografia britanica ("organises"), e numero de quatro digitos
# aparece com separador de milhar em todo o resto do dashboard.
FIX = {"1487": "1,487", "cafe": "café", "neighbor": "neighbour",
       "favor": "favour", "color": "colour", "organize": "organise"}


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
    """Fatia uma fala em pedacos que caibam nas regras, cortando em palavra.

    So corta quando o texto nao cabe em duas linhas ou o cue fica longo demais.
    Cortar por velocidade de leitura foi tentado e sai pior: as falas aqui sao
    frases curtas, e dividir uma delas deixa um orfao de duas palavras na tela
    por menos de um segundo, que le pior do que a frase inteira um pouco rapida.
    """
    text = " ".join(norm(w.word) for w in words)
    dur = words[-1].end - words[0].start
    n = max(math.ceil(len(text) / MAX_CHARS), math.ceil(dur / MAX_DUR))
    if n <= 1:
        return [words]
    target = len(text) / n
    chunks, buf, acc = [], [], 0
    for w in words:
        buf.append(w)
        acc += len(norm(w.word)) + 1
        ends_clause = norm(w.word)[-1:] in ".,;:!?"
        if len(chunks) < n - 1 and acc >= target * .72 and (ends_clause or acc >= target * 1.15):
            chunks.append(buf)
            buf, acc = [], 0
    if buf:
        chunks.append(buf)
    return [c for c in chunks if c]


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

    cues = []
    for seg in segments:
        words = [w for w in (seg.words or []) if w.word.strip()]
        if not words:
            continue
        for chunk in split_words(words):
            cues.append((chunk[0].start, chunk[-1].end,
                         " ".join(norm(w.word) for w in chunk)))
    if not cues:
        sys.exit(f"{src.name}: no speech found, nothing written")

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
    print("Check the text against the audio before committing: the transcription "
          "is good, not perfect.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"not found: {path}")
    build(path.resolve())
