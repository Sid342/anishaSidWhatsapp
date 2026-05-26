STOPWORDS_EN = set("""
a an the and or but if then else of for to in on at by from with as is are was were be been being have has had do does did
i you he she we they it me him her us them my your his our their this that these those not no yes ok okay
""".split())

STOPWORDS_HI = set("""
ka ke ki ko ho hu hai hain h se na ne to bhi par mein mei mai me tu tum tujhe mujhe kya kyun kyu kab phir aur lekin
""".split())

ENDEARMENTS = ["baby", "bebu", "beboo", "bebs", "babyy", "babyyy", "babyyyy",
               "anisaa", "anisa", "anisha", "sid", "sidd", "siddy", "babu", "jaan", "love"]

PLACES = ["delhi", "noida", "gurgaon", "gurugram", "lajpat", "rajouri",
          "mandi house", "rajiv chowk", "rajeev chowk", "kashmere gate",
          "saket", "hauz khas", "huda city", "escorts", "mujesar", "metro"]

MENTION_TOPICS = {
    "parents":  ["mummy", "papa", "mom", "dad", "ghar", "parents"],
    "lenovo":   ["lenovo", "office", "boss", "team", "manager"],
    "college":  ["college", "du", "exam", "class", "lecture", "prof"],
    "wedding":  ["shaadi", "marry", "marriage", "ring", "engagement"],
    "money":    ["money", "salary", "rent", "expense", "save", "saving"],
    "food":     ["food", "biryani", "pizza", "dosa", "khana", "zomato", "swiggy"],
}

FOOD_KEYWORDS = ["zomato", "swiggy", "biryani", "pizza", "burger", "dosa",
                 "khana", "lunch", "dinner", "breakfast", "chai"]

TRAVEL_KEYWORDS = ["flight", "irctc", "indigo", "vistara", "spicejet",
                   "airport", "train", "uber", "ola", "metro"]
