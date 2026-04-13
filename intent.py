def parse_intent(user_input):
    user_input = user_input.lower()
    words = user_input.split()

    app_keywords = ["youtube","notepad"]
    action_keywords = ["play","write","open", "type","search", "watch","listen"]
    stopwords = ["i", "want", "to", "wish", "would", "like", "please", "me"]

    words = user_input.lower().split()
    clean_words = [w for w in words if w not in stopwords]

    if any(w in clean_words for w in action_keywords):
          query_words = [w for w in clean_words if w not in action_keywords]
          query = " ".join(query_words)
    if query:
            return f"open chrome, type youtube.com, enter, wait 5, focus, type {query}, enter"
    else:
            return "open chrome, type youtube.com, enter, wait 5, focus"
        
    return None