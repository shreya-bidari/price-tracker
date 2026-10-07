import sqlite3
import sys

# usage: python simulate_drop.py "Product Name 1" "Product Name 2"
names = sys.argv[1:] or ["Asus VivoBook X441NA-GA190"]

conn = sqlite3.connect("price_tracker.db")
for name in names:
    cur = conn.execute(
        "UPDATE prices SET price = price + 50 "
        "WHERE id = (SELECT MAX(id) FROM prices WHERE product_name = ?)",
        (name,),
    )
    print(f"{name}: {'raised by 50' if cur.rowcount else 'NOT FOUND (check the name)'}")
conn.commit()
conn.close()
print("Now run: python main.py --once")