// Private API
import express from 'express';
import fileUpload from 'express-fileupload';
import bodyParser from 'body-parser';

export const privateAPI = express();

privateAPI.use(bodyParser.json());
privateAPI.use(bodyParser.urlencoded({ extended: true }));

privateAPI.post('/upload_texture', fileUpload(), async (request, response) => {
    response.type("application/json");
    try {
        if(!request.files || !request.body.mod) {
            response.send({
                status: false,
                message: 'No file uploaded or mod name'
            });
        } else {
            let texture  = request.files.texture;

            const { data, error } = await supabase.storage
                .from('textures')
                .upload(request.body.mod + "/" + texture.name, texture.data, { contentType: texture.mimetype });

            response.send({
                status: true,
                message: 'File is uploaded',
                data: {
                    name: texture.name,
                    mimetype: texture.mimetype,
                    size: texture.size
                },
                error: error
            });
        }
    } catch (err) {
        console.log(err);
        response.status(500).send(err);
    }
});

privateAPI.post('/initNewTurtle', async (request, response) => {
    response.type("application/json");
    const label = request.body.label;
    try {
        if (!label) {
            response.json({ status: false, error: 422, label: label, message: "Turtle not found!" });
        } else if ((await get_turtle(label)) != null) {
            response.json({ status: false, error: 422, label: label, message: "Turtle must be unique!" });
        } else {
            init_queue.push(label);
            await send_command("1816241331776982748426", "initNewTurtle()");
            response.json({ status: true, label: label, message: "Turtle Initializing!" });
        }
    } catch (err) {
        response.status(500).send(err);
    }
});