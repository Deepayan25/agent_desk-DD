from actions import show_help
def parse_intent(user_input):
    user_input_lower = user_input.lower()
    words = user_input_lower.split()

    if not words:
        return None
    
    primitive_actions = ["open", "wait", "enter", "del", "focus", "prevline","help"]
    if words[0] in primitive_actions:
        return {"action": words[0], "query": " ".join(words[1:]), "platform": None}
    platform_map = {
        "youtube": "youtube",
        "yt": "youtube",
        "google": "google",
        "notepad": "notepad",
        "notes": "notepad",
        "np": "notepad",
        "ggl": "google",
        "xl" : "excel",
        "word": "winword",
        "help" : show_help
    }

    action_keywords = ["play", "write", "open", "type", "search", "watch", "listen", "find"]
    stopwords = ["i", "want", "to", "wish", "would", "like", "please", "me", "can", "you", "could", "in", "on", "at", "from", "the", "a", "an"]
    question_patterns = ["what is", "what are", "how to", "who is", "where is", "why is"]

    # question pattern check before anything else
    for pattern in question_patterns:
        if user_input_lower.startswith(pattern):
            query = user_input_lower.replace(pattern, "").strip()
            return {"action": "search", "query": query, "platform": "google"}

    clean_words = [w for w in words if w not in stopwords]

    noise_words = ["while", "when", "whilst", "during"]
    for i, w in enumerate(clean_words):
        if w in noise_words:
            clean_words = clean_words[:i]
            break
    
    if not clean_words:
        return None

    # extract platform modifier
    platform = None
    for word, mapped in platform_map.items():
        if word in clean_words:
            platform = mapped
            clean_words = [w for w in clean_words if w != word]
            break

    if any(w in clean_words for w in action_keywords):
        
        if "open" in clean_words:
            target_words = [w for w in clean_words if w not in action_keywords]

            if target_words:
                target = " ".join(target_words)
            elif platform:
                target = platform
            else:
                target = None

            return {"action": "open", "query": target, "platform": platform} if target else None        

        if any(w in clean_words for w in ["search", "find"]):
            query = " ".join([w for w in clean_words if w not in action_keywords])
            return {"action": "search", "query": query, "platform": platform or "google"} if query else None

        if any(w in clean_words for w in ["play", "watch", "listen"]):
            query = " ".join([w for w in clean_words if w not in action_keywords])
            return {"action": "play", "query": query, "platform": platform or "youtube"} if query else None
        
        original_words = user_input.split()
        text = " ".join([w for w in original_words if w.lower() not in action_keywords and w.lower() not in platform_map])
        if not text:
            return None
        if platform:
            return [
                {"action": "open", "query": platform, "platform": None},
                {"action": "type", "query": text, "platform": None}
                ]
        return {"action": "type", "query": text, "platform": None}

        return None