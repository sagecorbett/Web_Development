// Require express and initialize it
const express = require('express')
const app = express()
const port = process.env.PORT || 3000

// Require socket.io and pass the server object to it
const io = require('socket.io')(
    app.listen(port, () => {
        console.log('App listening on port: ', port)
    })
)

// Tell our app to use our client folder as static code
app.use(express.static('client'))

// Set up a home route and send the client folder
app.get('/', (req, res) => {
    res.send('client')
})

// Simple array to store previous messages
const messages = []

// Create a socket io connection and handle emissions
// that are received or to be sent out
io.on('connection', socket => {

    // When a new socket connects, we want to send all of the previous messages
    // from the message array
    io.to(socket.id).emit('Info for New User', messages)

    // When a new user opens our app in the browser
    socket.on('New User', nickname => {
        console.log(nickname, ' Has joined the chat')
        io.emit('New User', nickname)
    })

    // When we receive a message from a user
    socket.on('New Message', message => {
        messages.push(message)
        io.emit('New Message', message)
    })

    // When a user is typing into the message box
    socket.on('User Typing', user => {
        socket.broadcast.emit('User Typing', user)
    })

    // When a user started typing and then stopped
    socket.on('User Stopped Typing', user => {
        socket.broadcast.emit('User Stopped Typing', user)
    })
})