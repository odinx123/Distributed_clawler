import redis
import time

# 1. 連線到 Redis (因為是 Docker 跑在本地，host 用 localhost)
# port 6379 是我們當初 docker run 指令中設定的
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

try:
    # 2. 測試存入與讀取
    print("--- 基礎測試 ---")
    r.set('user:123', 'Gemini AI')
    name = r.get('user:123')
    print(f"存入的名稱是: {name}")

    # 3. 測試數字遞增 (適合做計數器)
    print("\n--- 計數器測試 ---")
    r.set('page_view', 100)
    r.incr('page_view') # 自動 +1
    print(f"目前的瀏覽次數: {r.get('page_view')}")

    # 4. 測試資料自動過期 (TTL)
    print("\n--- 自動過期測試 ---")
    r.setex('temp_token', 5, 'ABC-123') # 5秒後自動消失
    print(f"Token 目前還在: {r.get('temp_token')}")
    
    print("等待 6 秒鐘...")
    time.sleep(6)
    
    token = r.get('temp_token')
    if token is None:
        print("Token 已自動過期並刪除！")
    else:
        print(f"Token 竟然還在: {token}")

except redis.exceptions.ConnectionError:
    print("錯誤：無法連線到 Redis！請確認 Docker 中的 my-redis 容器是否有啟動。")