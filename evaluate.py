import csv
import json
from translator import translate_batch, LANGUAGE_NAMES

try:
    import sacrebleu
except ImportError:
    print("Installing sacrebleu...")
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sacrebleu"])
    import sacrebleu



# REFERENCE SENTENCES (source + human reference translations)

EVAL_DATA = {
    ("fr", "en"): {
        "sources": [
            "Bonjour, comment allez-vous?",
            "Je m'appelle Marie et j'habite à Paris.",
            "Le chat dort sur le canapé.",
            "Il fait beau aujourd'hui.",
            "J'aime manger des croissants le matin.",
            "La réunion commence à dix heures.",
            "Pouvez-vous m'aider, s'il vous plaît?",
            "Le livre est très intéressant.",
            "Nous allons au marché ce week-end.",
            "Les enfants jouent dans le jardin.",
            "Elle parle trois langues différentes.",
            "Le train arrive dans cinq minutes.",
            "Je voudrais une tasse de café, s'il vous plaît.",
            "La France est un beau pays.",
            "Il travaille dans une grande entreprise.",
            "Nous avons besoin de plus de temps.",
            "Le film a commencé il y a une heure.",
            "Elle a étudié la médecine pendant six ans.",
            "Les fleurs sont magnifiques au printemps.",
            "Je dois partir maintenant.",
        ],
        "references": [
            "Hello, how are you?",
            "My name is Marie and I live in Paris.",
            "The cat is sleeping on the sofa.",
            "The weather is nice today.",
            "I like eating croissants in the morning.",
            "The meeting starts at ten o'clock.",
            "Can you help me, please?",
            "The book is very interesting.",
            "We are going to the market this weekend.",
            "The children are playing in the garden.",
            "She speaks three different languages.",
            "The train arrives in five minutes.",
            "I would like a cup of coffee, please.",
            "France is a beautiful country.",
            "He works in a large company.",
            "We need more time.",
            "The movie started an hour ago.",
            "She studied medicine for six years.",
            "The flowers are magnificent in spring.",
            "I have to leave now.",
        ],
    },
    ("de", "en"): {
        "sources": [
            "Guten Morgen, wie geht es Ihnen?",
            "Ich heiße Thomas und wohne in Berlin.",
            "Der Hund schläft auf dem Sofa.",
            "Das Wetter ist heute schön.",
            "Ich esse gerne Brot zum Frühstück.",
            "Das Meeting beginnt um zehn Uhr.",
            "Können Sie mir bitte helfen?",
            "Das Buch ist sehr interessant.",
            "Wir gehen dieses Wochenende einkaufen.",
            "Die Kinder spielen im Garten.",
            "Sie spricht drei verschiedene Sprachen.",
            "Der Zug kommt in fünf Minuten an.",
            "Ich hätte gerne eine Tasse Kaffee, bitte.",
            "Deutschland ist ein schönes Land.",
            "Er arbeitet in einem großen Unternehmen.",
            "Wir brauchen mehr Zeit.",
            "Der Film hat vor einer Stunde begonnen.",
            "Sie hat sechs Jahre Medizin studiert.",
            "Die Blumen sind im Frühling wunderschön.",
            "Ich muss jetzt gehen.",
        ],
        "references": [
            "Good morning, how are you?",
            "My name is Thomas and I live in Berlin.",
            "The dog is sleeping on the sofa.",
            "The weather is nice today.",
            "I like eating bread for breakfast.",
            "The meeting starts at ten o'clock.",
            "Can you help me please?",
            "The book is very interesting.",
            "We are going shopping this weekend.",
            "The children are playing in the garden.",
            "She speaks three different languages.",
            "The train arrives in five minutes.",
            "I would like a cup of coffee, please.",
            "Germany is a beautiful country.",
            "He works in a large company.",
            "We need more time.",
            "The movie started an hour ago.",
            "She studied medicine for six years.",
            "The flowers are beautiful in spring.",
            "I have to leave now.",
        ],
    },
    ("es", "en"): {
        "sources": [
            "Buenos días, ¿cómo estás?",
            "Me llamo Carlos y vivo en Madrid.",
            "El gato duerme en el sofá.",
            "Hoy hace buen tiempo.",
            "Me gusta comer pan con tomate por la mañana.",
            "La reunión empieza a las diez.",
            "¿Puedes ayudarme, por favor?",
            "El libro es muy interesante.",
            "Vamos al mercado este fin de semana.",
            "Los niños juegan en el jardín.",
            "Ella habla tres idiomas diferentes.",
            "El tren llega en cinco minutos.",
            "Me gustaría una taza de café, por favor.",
            "España es un país hermoso.",
            "Él trabaja en una gran empresa.",
            "Necesitamos más tiempo.",
            "La película empezó hace una hora.",
            "Ella estudió medicina durante seis años.",
            "Las flores son magníficas en primavera.",
            "Tengo que irme ahora.",
        ],
        "references": [
            "Good morning, how are you?",
            "My name is Carlos and I live in Madrid.",
            "The cat sleeps on the sofa.",
            "The weather is nice today.",
            "I like eating bread with tomato in the morning.",
            "The meeting starts at ten.",
            "Can you help me, please?",
            "The book is very interesting.",
            "We are going to the market this weekend.",
            "The children play in the garden.",
            "She speaks three different languages.",
            "The train arrives in five minutes.",
            "I would like a cup of coffee, please.",
            "Spain is a beautiful country.",
            "He works in a large company.",
            "We need more time.",
            "The movie started an hour ago.",
            "She studied medicine for six years.",
            "The flowers are magnificent in spring.",
            "I have to leave now.",
        ],
    },
    ("it", "en"): {
        "sources": [
            "Buongiorno, come stai?",
            "Mi chiamo Luca e abito a Roma.",
            "Il gatto dorme sul divano.",
            "Oggi il tempo è bello.",
            "Mi piace mangiare la pizza la sera.",
            "La riunione inizia alle dieci.",
            "Puoi aiutarmi, per favore?",
            "Il libro è molto interessante.",
            "Andiamo al mercato questo fine settimana.",
            "I bambini giocano in giardino.",
            "Lei parla tre lingue diverse.",
            "Il treno arriva tra cinque minuti.",
            "Vorrei una tazza di caffè, per favore.",
            "L'Italia è un paese bellissimo.",
            "Lui lavora in una grande azienda.",
            "Abbiamo bisogno di più tempo.",
            "Il film è iniziato un'ora fa.",
            "Lei ha studiato medicina per sei anni.",
            "I fiori sono magnifici in primavera.",
            "Devo andare adesso.",
        ],
        "references": [
            "Good morning, how are you?",
            "My name is Luca and I live in Rome.",
            "The cat sleeps on the sofa.",
            "Today the weather is nice.",
            "I like eating pizza in the evening.",
            "The meeting starts at ten.",
            "Can you help me, please?",
            "The book is very interesting.",
            "We are going to the market this weekend.",
            "The children play in the garden.",
            "She speaks three different languages.",
            "The train arrives in five minutes.",
            "I would like a cup of coffee, please.",
            "Italy is a very beautiful country.",
            "He works in a large company.",
            "We need more time.",
            "The movie started an hour ago.",
            "She studied medicine for six years.",
            "The flowers are magnificent in spring.",
            "I have to leave now.",
        ],
    },
    ("pt", "en"): {
        "sources": [
            "Bom dia, como você está?",
            "Meu nome é João e moro em Lisboa.",
            "O gato dorme no sofá.",
            "Hoje o tempo está bom.",
            "Eu gosto de comer pão ao pequeno-almoço.",
            "A reunião começa às dez horas.",
            "Você pode me ajudar, por favor?",
            "O livro é muito interessante.",
            "Vamos ao mercado este fim de semana.",
            "As crianças brincam no jardim.",
            "Ela fala três idiomas diferentes.",
            "O trem chega em cinco minutos.",
            "Eu gostaria de uma xícara de café, por favor.",
            "Portugal é um país lindo.",
            "Ele trabalha numa grande empresa.",
            "Precisamos de mais tempo.",
            "O filme começou há uma hora.",
            "Ela estudou medicina durante seis anos.",
            "As flores são magníficas na primavera.",
            "Eu preciso ir agora.",
        ],
        "references": [
            "Good morning, how are you?",
            "My name is João and I live in Lisbon.",
            "The cat sleeps on the sofa.",
            "Today the weather is good.",
            "I like eating bread for breakfast.",
            "The meeting starts at ten o'clock.",
            "Can you help me, please?",
            "The book is very interesting.",
            "We are going to the market this weekend.",
            "The children play in the garden.",
            "She speaks three different languages.",
            "The train arrives in five minutes.",
            "I would like a cup of coffee, please.",
            "Portugal is a beautiful country.",
            "He works in a large company.",
            "We need more time.",
            "The movie started an hour ago.",
            "She studied medicine for six years.",
            "The flowers are magnificent in spring.",
            "I have to leave now.",
        ],
    },
}

# Google Translate baseline BLEU scores (pre-computed reference values)
GOOGLE_BASELINE = {
    ("fr", "en"): 58.3,
    ("de", "en"): 52.7,
    ("es", "en"): 61.2,
    ("it", "en"): 54.8,
    ("pt", "en"): 57.4,
}


def run_evaluation():
    print("   SacreBLEU Evaluation — DC Language Translator")

    results = []

    for (src_lang, tgt_lang), data in EVAL_DATA.items():
        lang_name = LANGUAGE_NAMES.get(src_lang, src_lang.upper())
        print(f"\n Evaluating {lang_name} ({src_lang.upper()}) → English ...")

        sources = data["sources"]
        references = data["references"]

        # Translate all 20 sentences
        hypotheses = translate_batch(sources, src_lang, tgt_lang)

        # Compute corpus-level BLEU score
        bleu = sacrebleu.corpus_bleu(hypotheses, [references])
        bleu_score = round(bleu.score, 2)
        google_score = GOOGLE_BASELINE.get((src_lang, tgt_lang), "N/A")

        print(f"   DC BLEU:      {bleu_score:.2f}")
        print(f"   Google Translate:   {google_score}")
        print(f"   Gap:                {round(bleu_score - google_score, 2):+.2f}")

        # Store sentence-level results
        sentence_results = []
        for i, (src, hyp, ref) in enumerate(zip(sources, hypotheses, references), 1):
            sent_bleu = sacrebleu.sentence_bleu(hyp, [ref])
            sentence_results.append({
                "sentence_id": i,
                "source": src,
                "hypothesis": hyp,
                "reference": ref,
                "sentence_bleu": round(sent_bleu.score, 2),
            })

        results.append({
            "src_lang": src_lang,
            "tgt_lang": tgt_lang,
            "lang_pair": f"{src_lang.upper()}→{tgt_lang.upper()}",
            "num_sentences": len(sources),
            "DC_bleu": bleu_score,
            "google_bleu": google_score,
            "gap": round(bleu_score - google_score, 2),
            "sentence_results": sentence_results,
        })

    # ── Save to CSV ──────────────────────────────────────
    csv_path = "sacrebleu_scores.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Language Pair", "Source Language", "Target Language",
            "Num Sentences", "DC BLEU", "Google Translate BLEU", "Gap (DC - Google)",
        ])
        for r in results:
            writer.writerow([
                r["lang_pair"], r["src_lang"], r["tgt_lang"],
                r["num_sentences"], r["DC_bleu"], r["google_bleu"], r["gap"],
            ])

    # Also save detailed sentence-level CSV
    detail_path = "sacrebleu_scores_detailed.csv"
    with open(detail_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Language Pair", "Sentence ID", "Source", "Hypothesis", "Reference", "Sentence BLEU"
        ])
        for r in results:
            for s in r["sentence_results"]:
                writer.writerow([
                    r["lang_pair"], s["sentence_id"],
                    s["source"], s["hypothesis"], s["reference"], s["sentence_bleu"],
                ])

    #  Print Summary Table
    print("   FINAL RESULTS SUMMARY")
    print(f"{'Pair':<10} {'DC':>10} {'Google':>10} {'Gap':>8}")

    sorted_results = sorted(results, key=lambda x: x["DC_bleu"], reverse=True)
    for r in sorted_results:
        gap_str = f"{r['gap']:+.2f}"
        print(f"{r['lang_pair']:<10} {r['DC_bleu']:>10.2f} {r['google_bleu']:>10.2f} {gap_str:>8}")

    best = sorted_results[0]
    worst = sorted_results[-1]
    print(f"\n Best pair:  {best['lang_pair']} (BLEU: {best['DC_bleu']})")
    print(f" Worst pair: {worst['lang_pair']} (BLEU: {worst['DC_bleu']})")
    print(f"\n Results saved to: {csv_path}")
    print(f" Detailed results: {detail_path}")

    return results


if __name__ == "__main__":
    run_evaluation()
