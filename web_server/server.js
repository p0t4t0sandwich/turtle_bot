// jerry   = 456968532601
// builder = 1816241331776982748426
// BAS     = 800934783541968916

// ENV
import { config } from "dotenv";
config()


// Misc Functions
// Function to introduce sleep()
export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Get the x and z offset for the "front" of the turtle.
export function get_offset(facing) {
    var xo = 0;
    var zo = 0;
    if (facing == 0) {
        zo = -1;
    } else if (facing == 90) {
        xo = -1;
    } else if (facing == 180) {
        zo = 1;
    } else if (facing == 270) {
        xo = 1;
    }
    return { xo, zo };
}

// AMPAPI -- Replace with an Rcon module if needed.
import ampapi from "@cubecoders/ampapi";

export let AMPAPI = new ampapi.AMPAPI(process.env.AMP_URL);
async function start_ampapi() {
    try {
        var APIInitOK = await AMPAPI.initAsync();
        if (!APIInitOK) {
            console.log("AMPAPI Init failed");
            return;
        }

        var loginResult = await AMPAPI.Core.LoginAsync(process.env.AMP_USER, process.env.AMP_PASSWORD, "", false);
        if (loginResult.success)
        {
            console.log("AMP Login successful");
            AMPAPI.sessionId = loginResult.sessionID;
            
            APIInitOK = await AMPAPI.initAsync();
            
            if (!APIInitOK) {
                console.log("AMPAPI Stage 2 Init failed");
                return;
            }
        } else {
            console.log("AMP Login failed");
            console.log(loginResult);
        }
    }
    catch (err) {
        console.log(err);
    }
}
start_ampapi();


import { WebSocketServer } from "ws";
// Web Sockets
let webSockets = {};
let init_queue = [];

export const wss = new WebSocketServer({ port: 8081 }, () => {
    console.log("Web Socket running on port 8081");
});

// Web Socket events
wss.on('connection', (ws, req) => {
    var url = req.url;
    var userID = url.slice(1);
    webSockets[userID] = ws;
    console.log('Connected: ' + userID);

    ws.on('message', async (message) => {
        console.log('received from ' + userID + ': ' + message);
        let json = JSON.parse(message);

        await update_tables(json);

        await init_new_turtle(json);

        await log_payload(json);
    });

    ws.on('close', () => {
        delete webSockets[userID]
        console.log('Disconnected: ' + userID)
    });
});

// Function to send a command to the turtle
export async function send_command(label, command) {
    if (webSockets[label]) {
        webSockets[label].send("{\"label\":\"" + label + "\",\"func\":\"return "+ command +"\"}");
        await sleep(570);
    }
}

// Public API
import { publicAPI } from "./publicAPI.js";

publicAPI.listen(8082, () => {
    console.log("Public REST API running on port 8082");
});

// Private API
import { privateAPI } from "./privateAPI.js";

privateAPI.listen(8083, () => {
    console.log("Private REST API running on port 8083");
});

// Supabase
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function update_block(x, y, z, block, metadata) {
    // Check for and alter nil values
    const curr_block = block != "nil" ? block : "minecraft:air";
    const curr_metadata = metadata != "nil" ? metadata : "";

    const { data, error } = await supabase
        .from('world')
        .upsert({
            x_pos: x,
            y_pos: y,
            z_pos: z
        })

    const { data2, error2 } = await supabase
        .from('world')
        .update({
            block: curr_block,
            metadata: curr_metadata
        })
        .eq("x_pos", x)
        .eq("y_pos", y)
        .eq("z_pos", z);
}

async function update_tables(json) {
    const position = json.turtle.position.split(",");
    const x_pos = parseInt(position[0]);
    const y_pos = parseInt(position[1]);
    const z_pos = parseInt(position[2]);

    // Getting LRB data
    var xo = 0;
    var zo = 0;
    var xl = 0;
    var zl = 0;
    if (json.turtle.facing == 0) {
        zo = -1;
        xl = -1;
    } else if (json.turtle.facing == 270) {
        xo = 1;
        zl = -1;
    } else if (json.turtle.facing == 180) {
        zo = 1;
        xl = 1;
    } else if (json.turtle.facing == 90) {
        xo = -1;
        zl = 1;
    }

    // Normalizing block data
    json.blocks.up.name = json.blocks.up.name != "nil" ? json.blocks.up.name : "minecraft:air";
    json.blocks.front.name = json.blocks.front.name != "nil" ? json.blocks.up.name : "minecraft:air";
    json.blocks.down.name = json.blocks.down.name != "nil" ? json.blocks.up.name : "minecraft:air";

    // Normalize LRB
    var left = (await get_block(x_pos + xl, y_pos, z_pos + zl));
    left = left != undefined ? left.block : "minecraft:air";
    var right = (await get_block(x_pos - xl, y_pos, z_pos - zl));
    right = right != undefined ? right.block : "minecraft:air";
    var back = (await get_block(x_pos - xo, y_pos, z_pos - zo));
    back = back != undefined ? back.block : "minecraft:air";

    const { data, error } = await supabase
        .from('turtles')
        .upsert({ label: json.turtle.label })

    const { data2, error2 } = await supabase
        .from('turtles')
        .update({
            fuel: json.turtle.fuel,
            id: json.turtle.id,
            x_pos: x_pos,
            y_pos: y_pos,
            z_pos: z_pos,
            facing: json.turtle.facing,
            inventory: json.inventory,
            up: json.blocks.up.name,
            front: json.blocks.front.name,
            down: json.blocks.down.name,
            left: left,
            right: right,
            back: back
        })
        .eq("label", json.turtle.label);

    if (json.blocks) {
        const { xo, zo } = get_offset(json.turtle.facing);
        update_block(x_pos, y_pos, z_pos, "minecraft:air", "");
        update_block(x_pos, y_pos + 1, z_pos, json.blocks.up.name, json.blocks.up.metadata);
        update_block(x_pos + xo, y_pos, z_pos + zo, json.blocks.front.name, json.blocks.front.metadata);
        update_block(x_pos, y_pos - 1, z_pos, json.blocks.down.name, json.blocks.down.metadata);
    }
}

export async function get_turtle(label) {
    try {
        let { data: turtles, error2 } = await supabase
            .from('turtles')
            .select('*')
            .eq("label", label);
        return turtles[0];
    } catch (err) {
        return null;
    }
}

async function get_block(x, y, z) {
    try {
        const { data: block, error } = await supabase
            .from('world')
            .select('*')
            .eq("x_pos", x)
            .eq("y_pos", y)
            .eq("z_pos", z)
        return block[0];
    } catch (err) {
        console.log(err);
        return { block: "minecraft:air" };
    }
}

async function get_value(block) {
    try {
        if (block) {
            const { data: value, error } = await supabase
                .from("textures")
                .select("value")
                .eq("block", block);
            if (value[0]) {
                return value[0].value;
            } else {
                return 0;
            }
        }
    } catch (err) {
        console.log(err);
        return 0;
    }
}

// Function to init a new turtle.
async function init_new_turtle(json) {
    try {
        const label = json.turtle.label;
        if (label.search(/[^A-Za-z\s]/) == -1) {
            try {
                var new_label = init_queue.pop();
                if (new_label != undefined) {
                    await send_command(label, "os.setComputerLabel(\'" + new_label + "\')");
                    await send_command(label, "turtle.select(2)");
                    await send_command(label, "turtle.refuel()");
                    await send_command(label, "turtle.select(1)");
                    await send_command(label, "os.reboot()");

                    const { data, error } = await supabase
                        .from('turtles')
                        .delete()
                        .eq("label", label);
                }
            } catch (err) {
                console.log(err);
            }
        }
    } catch (err) {
        console.log(err);
    }
}

async function log_payload(json) {
    try {
        if (json.payload) {
            let count = 0;
            for (var i = 0; i < json.payload.length; i++) {
                count += (await get_value(json.payload[i].name))*json.payload[i].count;
            }
            console.log(count);
        }
    } catch (err) {
        console.log(err);
    }
}
