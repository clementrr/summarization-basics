import sys, glob, nltk

summary_length = 100
stopwords = nltk.corpus.stopwords.words("english")
lemmatizer = nltk.stem.WordNetLemmatizer()

def tokenize_sentence(sentence):
    tokens = nltk.word_tokenize(sentence)
    tokens = [t.lower() for t in tokens if t not in stopwords]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return tokens

def compute_probs(cluster):
    word_probs = {}
    token_count = 0 
    
    for file_path in cluster:
        with open(file_path) as f:
            tokens = tokenize_sentence(f.read().decode("utf-8"))
            token_count += len(tokens)
        for t in tokens:
            if t not in word_probs:
                word_probs[t] = 1.
            else:
                word_probs[t] += 1.
                
    return {k: (v / token_count) for k, v in word_probs.items()}
    
def extract_sentences(cluster):
    sentences = []
    
    for file_path in cluster:
        with open(file_path) as f:
            sentences += nltk.sent_tokenize(f.read().decode("utf-8"))
            
    return sentences
        
def score_sentence(sentence, word_probs):
    score = 0.
    token_count = 0
    tokens = tokenize_sentence(sentence)
    
    for t in tokens:
        score += word_probs[t]
        token_count += 1
        
    return score / token_count

def best_sentence(sentences, word_probs, non_redundancy):
    best_sentence = sentences[0]
    max_score = score_sentence(best_sentence, word_probs)
    
    for sent in sentences:
        score = score_sentence(sent, word_probs)
        if score > max_score:
            best_sentence = sent
            max_score = score
    
    if non_redundancy:
        tokens = tokenize_sentence(best_sentence)
        for t in tokens:
            word_probs[t] = word_probs[t] ** 2
        
    return best_sentence
            
def sum_basic(cluster, non_redundancy):
    cluster = glob.glob(cluster)
    word_probs = compute_probs(cluster)
    sentences = extract_sentences(cluster)

    summary = []
    word_count = 0
    while word_count < summary_length:
        sent = best_sentence(sentences, word_probs, non_redundancy)
        summary.append(sent)
        word_count += len(nltk.word_tokenize(sent))
        sentences.remove(sent)
        
    return " ".join(summary)

def leading_baseline(cluster):
    cluster = glob.glob(cluster)
    sentences = extract_sentences(cluster)

    summary = []
    word_count = 0
    while word_count < summary_length:
        sent = sentences[0]
        summary.append(sent)
        word_count += len(nltk.word_tokenize(sent))
        sentences.remove(sent)
        
    return " ".join(summary)
    
if __name__ == "__main__":
    algorithm = sys.argv[1]
    cluster = sys.argv[2]

    if algorithm == "orig":
        summary = sum_basic(cluster, True)
    elif algorithm == "simplified":
        summary = sum_basic(cluster, False)
    elif algorithm == "leading":
        summary = leading_baseline(cluster)
    else:
        summary = "Hello world!"
    
    print summary