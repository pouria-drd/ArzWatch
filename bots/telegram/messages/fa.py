def welcome(username: str) -> str:
    return f"""
سلام 👋 <b>{username}</b> عزیز!  
به ربات <b>ArzWatch</b> خوش اومدی 🟢

این ربات برای نمایش قیمت‌های لحظه‌ای بازار طراحی شده 🧠

برای مشاهده دستورات موجود، کافیه از دستور زیر استفاده کنی:
👉 <b>/help</b>
"""


def help() -> str:
    return """
📚 <b>راهنمای دستورات ربات ArzWatch</b>

/gold - قیمت طلا
/coin - قیمت سکه
/crypto - قیمت ارز دیجیتال
/currency - قیمت ارزها
/help - نمایش همین راهنما  

💡 همه‌ی اطلاعات از منابع معتبر و به‌روز جمع‌آوری میشه و ربات هر چند دقیقه یکبار آپدیت میشه!
"""


def gold(misqal, gram_18k, date_part, time_part) -> str:
    return f"""
<b>📊 قیمت لحظه‌ای طلا</b>

🗓️ <b>{date_part}</b>   ⏰ <b>{time_part}</b>
———————————————

<b>🔸 مثقال طلا</b>
💰 قیمت: <b>{misqal['price']} تومان</b>
📈 تغییر: <code>{misqal['change']}</code>
🎈 حباب: <code>{misqal['bubble_amount']}</code> ({misqal['bubble_percentage']})
———————————————

<b>🔸 هر گرم طلای ۱۸ عیار</b>
💰 قیمت: <b>{gram_18k['price']} تومان</b>
📈 تغییر: <code>{gram_18k['change']}</code>
🎈 حباب: <code>{gram_18k['bubble_amount']}</code> ({gram_18k['bubble_percentage']})
———————————————
"""


def coin(coins, date_part, time_part, title_map) -> str:
    response = f"""
<b>🪙 قیمت لحظه‌ای سکه</b>

🗓️ <b>{date_part}</b>   ⏰ <b>{time_part}</b>
———————————————
"""
    for coin in coins:
        fa_title = title_map.get(coin["title"], coin["title"])
        response += f"""
<b>🔹 {fa_title}</b>
💰 قیمت: <b>{coin['price']} تومان</b>
📈 تغییر: <code>{coin['change']}</code>
🎈 حباب: <code>{coin['bubble_amount']}</code> ({coin['bubble_percentage']})
———————————————
"""
    return response


def error() -> str:
    return "❌ خطای داخلی. لطفا دوباره امتحان کن."
