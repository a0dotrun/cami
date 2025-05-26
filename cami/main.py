import asyncio

import hypercorn
import restate

from cami.session import chat

services: list[restate.Workflow | restate.Service | restate.VirtualObject] = []


services.append(chat)


app = restate.app(services)


if __name__ == "__main__":
    conf = hypercorn.Config()
    conf.bind = ["0.0.0.0:9080"]
    asyncio.run(hypercorn.asyncio.serve(app, conf))
