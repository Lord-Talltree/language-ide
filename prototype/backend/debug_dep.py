import spacy

nlp = spacy.load("en_core_web_sm")
text = "The bank is closed."
doc = nlp(text)

for token in doc:
    print(f"{token.text}: {token.pos_} ({token.tag_}) - dep: {token.dep_} -> head: {token.head.text}")
