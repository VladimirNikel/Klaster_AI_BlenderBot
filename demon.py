import asyncio
import os
from asyncpg import create_pool
import aiohttp
import json

FIRST_DELAY = 7 * 60
REPEAT_IN_SECONDS = 15 * 60


async def get_users_from_log_event_in_recent_times(pool_messages):
    async with pool_messages.acquire() as conn:
        async with conn.transaction():
            rows = await conn.fetch(
                "SELECT aa.who AS user_id "
                "FROM (SELECT DISTINCT ON (1) a.who, b.datetime "
                "FROM (SELECT DISTINCT from_whom AS who FROM aid.log_messages WHERE from_whom <> 'API') AS a "
                "JOIN aid.log_messages AS b ON b.from_whom = a.who ORDER BY 1, b.datetime DESC) AS aa "
                "WHERE aa.datetime BETWEEN (now() - interval '4 hour 20 min') AND (now() - interval '4 hour');")
            return [row[0] for row in rows]


async def separate_demon():
    await asyncio.sleep(FIRST_DELAY)
    pool_messages = await create_pool(os.getenv("DB_MESSAGES", ""))
    while True:
        list_users = await get_users_from_log_event_in_recent_times(pool_messages)
        if list_users:
            async with aiohttp.ClientSession() as session:
                async with session.delete(f'{os.getenv("API", "")}',
                                          headers={'Content-Type': 'application/json'},
                                          data=json.dumps(list_users)) as resp:
                    print(f'{list_users} - {resp.status}')
        await asyncio.sleep(REPEAT_IN_SECONDS)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(separate_demon())
