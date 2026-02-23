import hashlib
import redis.asyncio as redis # 使用非同步的 Redis 套件

class TaskManager:
    def __init__(self, redis_url='redis://localhost:6379'):
        # 建立連線池
        self.redis = redis.from_url(redis_url, decode_responses=True)
        # 定義 Redis 裡的 Key 名稱
        self.queue_key = "crawler:queue"   # 待爬清單 (List)
        self.seen_key = "crawler:seen"     # 已爬集合 (Set)

    async def add_url(self, url: str):
        """
        核心邏輯：先去重，再入列
        """
        # 把網址變成 MD5 (節省 Redis 記憶體)
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # 檢查 MD5 是否已存在 (SISMEMBER 是 O(1) 操作)
        is_exist = await self.redis.sismember(self.seen_key, url_hash)
        
        if not is_exist:
            # 如果是新的，開啟 Pipeline (交易模式)
            async with self.redis.pipeline() as pipe:
                await pipe.sadd(self.seen_key, url_hash)  # 標記為已見
                await pipe.rpush(self.queue_key, url)     # 加入待爬隊列
                await pipe.execute()                      # 執行！
            print(f"[TaskManager] 新增任務: {url}")
            return True
        else:
            # print(f"[TaskManager] 重複忽略: {url}") # 除錯用
            return False

    async def get_url(self):
        """
        工作者來領任務了：從隊列左邊拿出一個
        """
        return await self.redis.lpop(self.queue_key)

    async def size(self):
        """查詢現在還有多少任務在排隊"""
        return await self.redis.llen(self.queue_key)