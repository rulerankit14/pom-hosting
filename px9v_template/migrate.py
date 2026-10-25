import sqlite3
from config import DB_NAME

                                
kkk = sqlite3.connect(DB_NAME)
cursor = kkk.cursor()

                                                   
                                                                                
                                                                                                                                                  
try:
    cursor.execute("UPDATE users SET is_live = 1 WHERE is_live = 0")
except sqlite3.OperationalError:
                                                                    
    cursor.execute("UPDATE user_status SET is_live = 1 WHERE is_live = 0")

kkk.commit()
kkk.close()

print("✅ Migration Complete: All users are revived and ready for broadcast.")
