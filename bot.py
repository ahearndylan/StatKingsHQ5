import tweepy
import random
import time
from datetime import datetime, timedelta

# ======================= #
# TWITTER AUTHENTICATION  #
# ======================= #

bearer_token = "AAAAAAAAAAAAAAAAAAAAAPztzwEAAAAAvBGCjApPNyqj9c%2BG7740SkkTShs%3DTCpOQ0DMncSMhaW0OA4UTPZrPRx3BHjIxFPzRyeoyMs2KHk6hM"
api_key = "uKyGoDr5LQbLvu9i7pgFrAnBr"
api_secret = "KGBVtj1BUmAEsyoTmZhz67953ItQ8TIDcChSpodXV8uGMPXsoH"
access_token = "1901441558596988929-WMdEPOtNDj7QTJgLHVylxnylI9ObgD"
access_token_secret = "9sf83R8A0MBdijPdns6nWaG7HF47htcWo6oONPmMS7o98"

client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
    wait_on_rate_limit=False  # <-- We handle rate limits ourselves now
)

# ======================= #
#     BRANDED REPLIES     #
# ======================= #

REPLY_BANK = [
    "Crowned. 👑 #CourtKingsHQ",
    "Court Kings certified. ✅👑",
    "On the throne tonight. 🏀👑",
    "Another royal performance. 📊👑",
    "#CourtKingsHQ sees you 👀👑",
    "Court royalty. 📈👑",
    "Kings of the box score. 📊👑",
    "#CourtKingsHQ recognized the numbers.",
    "Hoop math checks out. 🧠📊👑",
    "This is crown-worthy. 👑",
    "Give this man his flowers and his crown. 🌺👑",
    "Don't sleep on royalty. 😴👑",
    "He wears the crown. 🏀💼👑",
    "Court Kings got next on this one. ⏳👑"
]

reply_queue = REPLY_BANK * 2
random.shuffle(reply_queue)

WHITELIST = {
    "1295856186749689857",
    "1462950412225662983",
    "38433752",
}

# ======================= #
#        FIND TWEETS      #
# ======================= #

def find_tweets():
    query = (
        '"dropped 50" OR "triple double" OR "career high" OR "monster game" OR '
        '"clutch performance" OR "stat line" OR "box score" OR "efficiency" OR '
        '"plus-minus" OR "defensive stats" OR "stat leaders" OR '
        '#NBATwitter OR #NBA '
        '-is:retweet lang:en '
        '-gambling -bet -odds -parlay -profit -cashapp -giveaway'
    )
    return client.search_recent_tweets(
        query=query,
        max_results=20,
        tweet_fields=["author_id", "text"]
    ).data

# ======================= #
#         MAIN BOT        #
# ======================= #

def run_bot():
    print("🤖 Starting Court Kings HQ Bot (Manual Rate Limit Mode)\n")
    used_ids = set()
    total_sent = 0
    max_replies = len(REPLY_BANK) * 2
    search_cycles = 0
    max_search_cycles = 30

    while reply_queue and total_sent < max_replies and search_cycles < max_search_cycles:
        try:
            print(f"🔁 Search cycle {search_cycles + 1}/{max_search_cycles}")
            tweets = find_tweets()
            search_cycles += 1
            time.sleep(20)
        except tweepy.TooManyRequests:
            resume_time = datetime.now() + timedelta(minutes=16)
            print(f"🚨 Rate limit hit. Sleeping until {resume_time.strftime('%I:%M:%S %p')}...\n")
            time.sleep(960)  # 16 minutes
            continue
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(60)
            continue

        if not tweets:
            print("🕵️ No tweets found. Sleeping for 60 seconds...\n")
            time.sleep(60)
            continue

        for tweet in tweets:
            if total_sent >= max_replies:
                print("✅ All replies sent. Shutting down.\n")
                return

            tweet_id = tweet.id
            tweet_text = tweet.text
            author_id = str(tweet.author_id)

            if tweet_id in used_ids:
                continue

            if author_id not in WHITELIST and random.random() < 0.6:
                continue

            reply_text = reply_queue.pop(0)
            used_ids.add(tweet_id)

            print(f"\n🧠 Tweet: {tweet_text}\n💬 Replying: {reply_text}\n")

            try:
                client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
                total_sent += 1
                print(f"✅ Replied ({total_sent}/{max_replies})")
                time.sleep(random.randint(5, 10))
            except tweepy.TooManyRequests:
                resume_time = datetime.now() + timedelta(minutes=16)
                print(f"🚨 Post limit hit. Sleeping until {resume_time.strftime('%I:%M:%S %p')}\n")
                time.sleep(960)
            except Exception as e:
                print(f"❌ Failed to reply to tweet {tweet_id}: {e}")

    print(f"\n🏁 Done. Sent {total_sent} replies today 👑")

if __name__ == "__main__":
    run_bot()
