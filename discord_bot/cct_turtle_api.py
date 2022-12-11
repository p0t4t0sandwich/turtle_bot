#!/bin/python3

from aiohttp import ClientSession
import json


class Turtle():
    def __init__(self, label, url):
        self.label = label
        self.dataSource = url

    async def APICallAsync(self, endpoint: str, data: dict = {}) -> dict:
        headers = {"Content-Type": "application/json"}
        data = json.dumps({"label": self.label})

        async with ClientSession(headers=headers) as session:
            async with session.post(url=f'{self.dataSource}{endpoint}', data=data) as post:
                response = await post.json()
                post.close()

        return response

    async def status(self):
        return await self.APICallAsync("status")

    async def forward(self):
        return await self.APICallAsync("forward")

    async def back(self):
        return await self.APICallAsync("back")

    async def up(self):
        return await self.APICallAsync("up")

    async def down(self):
        return await self.APICallAsync("down")

    async def turnLeft(self):
        return await self.APICallAsync("turnLeft")

    async def turnRight(self):
        return await self.APICallAsync("turnRight")

    async def dig(self):
        return await self.APICallAsync("dig")

    async def digUp(self):
        return await self.APICallAsync("digUp")

    async def digDown(self):
        return await self.APICallAsync("digDown")

    async def digMoveForward(self):
        return await self.APICallAsync("digMoveForward")

    async def digMoveUp(self):
        return await self.APICallAsync("digMoveUp")

    async def digMoveDown(self):
        return await self.APICallAsync("digMoveDown")

    async def select(self, slot):
        return await self.APICallAsync("select", {"slot": slot})

    async def refuel(self):
        return await self.APICallAsync("refuel")

if __name__ == "__main__":
    import asyncio
    async def test():
        t = Turtle("456968532601", "http://localhost:8082/")
        await t.digUp()
        await t.up()
        await t.digMoveUp()
        await t.down()
        await t.down()
        await t.digDown()
        await t.down()
        await t.digMoveDown()
        await t.up()
        await t.up()

    asyncio.run(test())