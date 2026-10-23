#!/usr/bin/env python3
"""Build the Cheers living list from Laura's 2026-10-22 draft. Do not invent rows."""
import json
from pathlib import Path

# word, pronunciation, where. Notes in parentheses stay notes, not silent corrections.
RAW = """
gëzuar	guh-ZOO-ar	Albania — Albanian
Saúde	sah-OO-jee	Angola — Portuguese
صحتين	sahh-TAYN	Arabic-speaking Levant — Arabic (colloquial toast; varies by dialect)
في صحتك	fi sahh-tak	Arabic-speaking countries — Arabic (to your health; dialect varies)
¡Salud!	sah-LOOD	Argentina — Spanish
Cheers	cheerz	Australia — English
Prost	prohst	Austria — German
Na zdravje	nah ZDRAHV-yeh	Austria — Slovenian-speaking communities
Topa!	TOH-pah	Basque Country — Basque (toast expression; verify regional usage)
Na zdrowie	nah zdroh-VYEH	Belarus — Polish-speaking communities
Proost	prohst	Belgium — Dutch
Santé	sahn-TAY	Belgium — French
¡Salud!	sah-LOOD	Bolivia — Spanish
Živjeli!	ZHEE-vyeh-lee	Bosnia and Herzegovina — Bosnian/Croatian/Serbian usage
Saúde	sah-OO-jee	Brazil — Portuguese
Yec’hed mat	YEH-het maht	Brittany, France — Breton
Nazdrave	naz-DRAH-veh	Bulgaria — Bulgarian
Cheers	cheerz	Canada — English
Santé	sahn-TAY	Canada — French
Yām seng	yahm seng	Cantonese-speaking communities — Cantonese (especially Malaysia/Singapore contexts)
¡Salud!	sah-LOOD	Chile — Spanish
乾杯	gon¹ bui¹	China — Cantonese
乾杯	gān bēi	China — Mandarin
¡Salud!	sah-LOOD	Colombia — Spanish
Yec’hed mat	YEH-het maht	Cornwall, United Kingdom — Cornish (toast expression; verify usage)
¡Salud!	sah-LOOD	Costa Rica — Spanish
Na zdravlje	nah ZDRAHV-lyeh	Croatia — Croatian
¡Salud!	sah-LOOD	Cuba — Spanish
Skål	skohl	Denmark — Danish
¡Salud!	sah-LOOD	Dominican Republic — Spanish
Maisha marefu	mah-EE-shah mah-REH-foo	East Africa — Swahili (“long life”; toast phrase)
¡Salud!	sah-LOOD	Ecuador — Spanish
je vian sanon	yeh vee-ahn SAH-non	Esperanto — “to your health”
Terviseks	TEHR-vee-seks	Estonia — Estonian
Skål	skohl	Faroe Islands — Faroese
Kippis	KEEP-pees	Finland — Finnish
Skål	skohl	Finland — Swedish-speaking communities
Kippis	KEEP-pees	Finnish-speaking communities worldwide — Finnish
À votre santé	ah vot-ruh sahn-TAY	France — French (formal)
Santé	sahn-TAY	France — French (informal)
Santé	sahn-TAY	French-speaking Switzerland — French
Tsjoch!	tsohk	Friesland, Netherlands — West Frisian
გაუმარჯოს	gow-MAR-jos	Georgia — Georgian
Prost	prohst	German-speaking Switzerland — Swiss German/German
Prost	prohst	Germany — German
Zum Wohl	tsoom vohl	Germany — German (formal)
Anogyeɛ	ah-noh-JEH	Ghana — Akan/Twi (joy; toast usage varies)
Cheers	cheerz	Ghana — English
Γεια μας	YAH mahs	Greece — Greek
¡Salud!	sah-LOOD	Guatemala — Spanish
Egészségedre	eh-GAYSH-shay-ged-reh	Hungary — Hungarian
Skál	skowl	Iceland — Icelandic
Cheers	cheerz	India — English (urban/social usage)
शुभ स्वास्थ्य के लिए	shubh svaasthya ke liye	India — Hindi (formal “to good health”; not necessarily everyday toast)
அரோக்கியத்திற்கு	a-rohk-kee-yat-thir-ku	India / Sri Lanka — Tamil (formal “to health”; verify regional toast usage)
Selamat minum	suh-LAH-maht MEE-noom	Indonesia — Indonesian (roughly “enjoy your drink”; context-dependent)
به سلامتی	beh sah-lah-mah-tee	Iran — Persian
Sláinte	SLAHN-chuh	Ireland — Irish
לחיים	l’chaim	Israel — Hebrew
Cin cin	cheen cheen	Italian-speaking Switzerland — Italian
Cin cin	cheen cheen	Italy — Italian
Salute	sah-LOO-teh	Italy — Italian
乾杯	kan-pai	Japan — Japanese
Cheers	cheerz	Kenya — English
HIq	[xɪqʰ]	Klingon — constructed language (alcoholic drink including wine; not “cheers”)
Qapla’!	qap-LAH	Klingon — constructed language (“success!”; celebratory exclamation, not literal “cheers”)
건배	geon-bae	Korea — Korean
vīvat	VEE-vaht	Latin — later/ceremonial toast-like exclamation; not a standard Classical Latin equivalent
bene tibi	BEH-neh TEE-bee	Latin — “for your good”; explanatory approximation, not a fixed everyday toast
Į sveikatą	ee svei-KAH-tah	Lithuania — Lithuanian
Saħħa	SAH-hah	Malta — Maltese (literally “health”; toast use)
¡Salud!	sah-LOOD	Mexico — Spanish
Noroc	no-ROK	Moldova — Romanian
Saúde	sah-OO-jee	Mozambique — Portuguese
Proost	prohst	Netherlands — Dutch
Cheers	cheerz	New Zealand — English
Cheers	cheerz	Nigeria — English
Àláfíà	ah-LAH-fee-ah	Nigeria — Yoruba (“peace/well-being”; toast context varies)
Наздраве	naz-DRAH-veh	North Macedonia — Macedonian
Skål	skohl	Norway — Norwegian
¡Salud!	sah-LOOD	Peru — Spanish
Mabuhay!	mah-boo-HIGH	Philippines — Filipino/Tagalog (celebratory greeting/toast-like use)
Tagay!	TAH-guy	Philippines — Filipino/Tagalog (colloquial toast)
Na zdrowie	nah zdroh-VYEH	Poland — Polish
Saúde	sah-OO-jee	Portugal — Portuguese
¡Salud!	sah-LOOD	Puerto Rico — Spanish
Noroc	no-ROK	Romania — Romanian
За здоровье	za zda-ROV-yeh	Russia — Russian (to your health)
За здоровье	za zda-ROV-yeh	Russia — Russian (used toast; context-dependent)
Slàinte mhath	SLAHN-chuh vah	Scotland — Scottish Gaelic
Živeli!	ZHEE-veh-lee	Serbia — Serbian
乾杯	gān bēi	Singapore — Mandarin
Na zdravie	nah ZDRAH-vyeh	Slovakia — Slovak
Na zdravje	nah ZDRAHV-yeh	Slovenia — Slovene
Gesondheid	khuh-SOONT-hayt	South Africa — Afrikaans
Impilo	im-PEE-loh	South Africa — isiXhosa (health/life; toast usage varies)
¡Salud!	sah-LOOD	Spain — Spanish
Salud	sah-LOOD	Spanish-speaking communities worldwide — Spanish
Skål	skohl	Sweden — Swedish
ชนแก้ว	chon gâew	Thailand — Thai (“clink glasses”)
Şerefe	sheh-reh-FEH	Turkey — Turkish
Afiyet olsun	ah-fee-YET ol-SOON	Turkey — Turkish (usually “enjoy your meal”; not a direct equivalent of cheers)
Cheers	cheerz	Uganda — English
Будьмо!	BOOD-mo	Ukraine — Ukrainian
Cheers	cheerz	United Kingdom — English
Cheers	cheerz	United States — English
¡Salud!	sah-LOOD	Uruguay — Spanish
¡Salud!	sah-LOOD	Venezuela — Spanish
Một, hai, ba, dô!	moht hi bah zoh	Vietnam — Vietnamese (group drinking cheer)
Chúc sức khỏe	chook sook kweh	Vietnam — Vietnamese (“to health”; toast wording)
Terviseks	TEHR-vee-seks	Võro-speaking region, Estonia — Võro
Iechyd da	YAY-khid dah	Wales — Welsh
Cheers	cheerz	Zimbabwe — English
Skål	skohl	Åland Islands — Swedish
""".strip().splitlines()


def split_where(where: str) -> tuple[str, str, str]:
    country, rest = where.split(" — ", 1)
    if country == "Esperanto":
        return country, "Esperanto", rest.strip("“”")
    if country == "Latin":
        return country, "Latin", rest
    note = ""
    language = rest
    if " (" in rest and rest.endswith(")"):
        language, note = rest.rsplit(" (", 1)
        note = note[:-1]
    return country, language, note


def kind_for(country: str, language: str) -> str:
    blob = f"{country} {language}".lower()
    if "constructed" in blob or country in {"Klingon", "Esperanto"}:
        return "constructed"
    if country == "Latin":
        return "historical"
    return "modern"


rows = []
for line in RAW:
    word, pronunciation, where = line.split("\t")
    country, language, note = split_where(where)
    rows.append(
        {
            "word": word,
            "pronunciation": pronunciation,
            "where": where,
            "country": country,
            "language": language,
            "note": note,
            "kind": kind_for(country, language),
        }
    )

rows.sort(key=lambda row: (row["country"].casefold(), row["language"].casefold(), row["word"].casefold()))
out = Path("/Users/executer/bellieacreswine/src/data/cheers-around-the-world.json")
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("rows", len(rows))
print("countries", len({row["country"] for row in rows}))
print("notes", sum(1 for row in rows if row["note"]))
print("kinds", {row["kind"] for row in rows})
