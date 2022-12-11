// Public API
import express from 'express';
import bodyParser from 'body-parser';

import { send_command, sleep, get_turtle, AMPAPI, get_offset } from './server.js';

async function reboot_turtle(label) {
    turtle = await get_turtle(label);
    
    await AMPAPI.Core.SendConsoleMessageAsync("computercraft dump");
    (await AMPAPI.Core.GetUpdatesAsync()).ConsoleEntries.forEach( async (element) => {
        if (element.Contents.includes(`(id ${turtle.id})`)){
            computerId = element.Contents[0] + element.Contents[1];
            await AMPAPI.Core.SendConsoleMessageAsync(`forceload add ${turtle.x_pos} ${turtle.z_pos}`);
            await AMPAPI.Core.SendConsoleMessageAsync(`computercraft shutdown ${computerId}`);
            await AMPAPI.Core.SendConsoleMessageAsync(`computercraft turn-on ${computerId}`);
        }
    });
}

export const publicAPI = express();

publicAPI.use(bodyParser.json());
publicAPI.use(bodyParser.urlencoded({ extended: true }));

publicAPI.post('/status', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/forward', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            const old_turtle = await get_turtle(label);
            const old_x_pos = old_turtle.x_pos;
            const old_z_pos = old_turtle.z_pos;

            const old_x_chunk = old_x_pos > 0 ? Math.ceil(old_x_pos/16) : Math.floor(old_x_pos/16);
            const old_z_chunk = old_z_pos > 0 ? Math.ceil(old_z_pos/16) : Math.floor(old_z_pos/16);

            const { xo, zo } = get_offset(old_turtle.facing);
            const new_x_pos = old_turtle.x_pos + xo;
            const new_z_pos = old_turtle.z_pos + zo;

            const new_x_chunk = new_x_pos > 0 ? Math.ceil(new_x_pos/16) : Math.floor(new_x_pos/16);
            const new_z_chunk = new_z_pos > 0 ? Math.ceil(new_z_pos/16) : Math.floor(new_z_pos/16);

            if (new_x_chunk != old_x_chunk || new_z_chunk != old_z_chunk) {
                await AMPAPI.Core.SendConsoleMessageAsync(`forceload add ${new_x_pos} ${new_z_pos}`);
            }

            await send_command(label, "turtle.forward()");

            if (new_x_chunk != old_x_chunk || new_z_chunk != old_z_chunk) {
                await AMPAPI.Core.SendConsoleMessageAsync(`forceload remove ${old_x_pos} ${old_z_pos}`);
            }

            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/back', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            const old_turtle = await get_turtle(label);
            const old_x_pos = old_turtle.x_pos;
            const old_z_pos = old_turtle.z_pos;

            const old_x_chunk = old_x_pos > 0 ? Math.ceil(old_x_pos/16) : Math.floor(old_x_pos/16);
            const old_z_chunk = old_z_pos > 0 ? Math.ceil(old_z_pos/16) : Math.floor(old_z_pos/16);

            const { xo, zo } = get_offset(old_turtle.facing);
            const new_x_pos = old_turtle.x_pos - xo;
            const new_z_pos = old_turtle.z_pos - zo;

            const new_x_chunk = new_x_pos > 0 ? Math.ceil(new_x_pos/16) : Math.floor(new_x_pos/16);
            const new_z_chunk = new_z_pos > 0 ? Math.ceil(new_z_pos/16) : Math.floor(new_z_pos/16);

            if (new_x_chunk != old_x_chunk || new_z_chunk != old_z_chunk) {
                await AMPAPI.Core.SendConsoleMessageAsync(`forceload add ${new_x_pos} ${new_z_pos}`);
            }

            await send_command(label, "turtle.back()");

            if (new_x_chunk != old_x_chunk || new_z_chunk != old_z_chunk) {
                await AMPAPI.Core.SendConsoleMessageAsync(`forceload remove ${old_x_pos} ${old_z_pos}`);
            }

            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/up', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.up()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/down', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.down()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/turnLeft', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.turnLeft()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/turnRight', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.turnRight()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/dig', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "safeDig()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/digUp', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "safeDigUp()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/digDown', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "safeDigDown()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/digMoveForward', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            const old_turtle = await get_turtle(label);
            const old_x_pos = old_turtle.x_pos;
            const old_z_pos = old_turtle.z_pos;

            const old_x_chunk = old_x_pos > 0 ? Math.ceil(old_x_pos/16) : Math.floor(old_x_pos/16);
            const old_z_chunk = old_z_pos > 0 ? Math.ceil(old_z_pos/16) : Math.floor(old_z_pos/16);

            const { xo, zo } = get_offset(old_turtle.facing);
            const new_x_pos = old_turtle.x_pos + xo;
            const new_z_pos = old_turtle.z_pos + zo;

            const new_x_chunk = new_x_pos > 0 ? Math.ceil(new_x_pos/16) : Math.floor(new_x_pos/16);
            const new_z_chunk = new_z_pos > 0 ? Math.ceil(new_z_pos/16) : Math.floor(new_z_pos/16);

            if (new_x_chunk != old_x_chunk || new_z_chunk != old_z_chunk) {
                await AMPAPI.Core.SendConsoleMessageAsync(`forceload add ${new_x_pos} ${new_z_pos}`);
            }

            await send_command(label, "digMoveForward()");

            if (new_x_chunk != old_x_chunk || new_z_chunk != old_z_chunk) {
                await AMPAPI.Core.SendConsoleMessageAsync(`forceload remove ${old_x_pos} ${old_z_pos}`);
            }

            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/digMoveUp', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "digMoveUp()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/digMoveDown', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.digMoveDown()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/select', async (request, response) => {
    const label = request.body.label;
    const slot = request.body.slot;
    response.type("application/json");
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.select(" + slot + ")");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/refuel', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "turtle.refuel()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/reboot', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await reboot_turtle(label);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.post('/dumpInventory', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({"status": false, "error": 422, "message": "Turtle not found"});
        } else {
            await send_command(label, "dumpInventory()");
            await sleep(50);
            response.json(await get_turtle(label));
        }
    } catch (err) {
        response.status(500).send(err);
    }
});

publicAPI.get('/download_texture', async (request, response) => {
    const block_data = request.body.block.split(":");
    const mod = block_data[0];
    const block = block_data[1];
    try {
        if(!request.body.block) {
            response.send({
                status: false,
                message: 'No block specified'
            });
        } else {
            const { data, error } = await supabase.storage
                .from('textures')
                .download(mod + "/" + block + ".png");

            response.contentType('image/png');
            response.send(Buffer.from(await data.arrayBuffer()));
        }
    } catch (err) {
        response.type("application/json");
        response.status(500).send({error: err});
    }
});