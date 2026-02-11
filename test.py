import asyncio

import httpx

class AuthClient:
    def __init__(self):
        self.base_url = "http://localhost:8080"

    async def register(self, user: dict):
        limits = httpx.Limits(max_keepalive_connections=0)

        async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=10.0,
                trust_env=False,
        ) as client:
            r = await client.post("/auth/register", json=user)
            print(r.status_code, r.text)
            r.raise_for_status()
            return r.json()



async def main():
    client = AuthClient()

    result = await client.register({"username":"test_us@mail.ru","password":"b","full_name":"c"})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())