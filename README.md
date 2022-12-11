# CCT DISCORD INTERFACE TODO

## NEEDED INFRASTRUCTURE

- [x] websocket handler and REST API -- WIP
- [x] Python wrapper for API -- WIP
- [x] chunk loading
- [x] discord bot
  - [x] a way to view progress
    - [x] generated image based on block data - images gathered from mod assets
    - [x] ~~store images in a table for easy db lookup?~~ Store them in memory
  - [x] buttons to control turtle movement
  - [x] turtle init command/process
    - [x] Save startup.lua to the mod's files, so each new turtle is connected.
    - [x] queue up waiting inits and rename new turtle after it's running.
- [ ] simple auth system to check if a user is in a guild (discord.js)

    ``` javascript
    let guild = client.guilds.get('guild ID here'),
    USER_ID = '123123123';

    if (guild.member.fetch(USER_ID)) {
      // there is a GuildMember with that ID
    }
    // or
    guild.members.fetch(usrID)
      .then((data) => console.log(data));
    ```

- [x] upgrade send/receive on the turtle
  - [x] ~~offload more parsing to storage handler~~ Web-server handles it
- [ ] set up Dynmap
  - [ ] make a mod that can add markers to dynmap?

## REWARD USERS

- [ ] reward all who have helped since last item dump (mine, move, etc) (cached to db)
- [ ] tally up all the recourses (lookup dict in memory, saved to db?)
- [ ] reward them with server currency based on score?
- [ ] Track best score + who helped
