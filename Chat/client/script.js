(() => {
	// ---------------------------------------------------------
	// Select all HTML elements we will need for the project:  |
	// ---------------------------------------------------------

	// Nickname Elements We Need
	// 1. The nickname div that covers the whole screen
	// 2. The nickname submit button
	// 3. The input field our user types their nickname into
	const nickname = document.querySelector('.nickname')
	const nicknameSubmit = document.querySelector('.nickname__submit')
	const nicknameInput = document.getElementById('nickname')
	const nicknameColor = document.querySelector('.nickname__color')

	// Chat Elements We Need
	// 1. The input our user types their message into
	// 2. The chat messages div
	// 3. The message submit button
	const message = document.getElementById('message')
	const chatMessages = document.querySelector('.chat__messages')
	const sendNewMessage = document.querySelector('.chat__submit')
	const userTyping = document.querySelector('.chat__user-typing')

	// Create new io instance:
	const socket = io()

	// ---------------------------------------------------------
	//      Set a new nickname in the session storage object   |
	// ---------------------------------------------------------

	// If no nickname is set then display the nickname modal that covers the scree
	if(!sessionStorage.getItem('nickname')){
		nickname.style.display = 'initial'

		// Allow users to press enter to send their nickname
		nicknameInput.addEventListener('keyup', event => {
			if(event.keyCode === 13 && nicknameInput.value.length > 0){
				nicknameSubmit.click()
			}
		})

		nicknameSubmit.addEventListener('click', () => {
			// Set nickname and color choice in sessionStorage
			sessionStorage.setItem('nickname', nicknameInput.value)
			sessionStorage.setItem('color', nicknameColor.value)

			nickname.style.display = 'none'
			socket.emit('New User', {
				nickname: sessionStorage.getItem('nickname'),
			})
		})
	}





	// ------------------------------------
	// Functions to create new messages:  |
	// ------------------------------------

	// Create a new user joined message
	const newUserJoined = nickname => {
		return `
			<div class="chat__new-user-joined">
				<i>${nickname} has joined the chat</i>
			</div>
		`;
	};

	// Create a new message from a user
	const newUserMessage = (user, message, color) => {
		console.log(color, ' in func')
		return `
			<div class="chat__user-message">
				<div class="chat__user-nickname" style="color: ${color}">
					${user}
				</div>
				<div class="chat__user-text">
					${message}
				</div>
			</div>
		`
	}


	const userTypingMessage = user => {
		return `
			<div class="chat__new-user-joined">
				<i>${user} is currently typing</i>
			</div>
		`;
	}

	// ------------------------------------
	//          Socket Events             |
	// ------------------------------------

	// When a new user Joins we want to send them the previous messages
	socket.on('Info for New User', messages => {
		messages.forEach(message => {
			chatMessages.innerHTML += newUserMessage(message.nickname, message.message, message.color)
		})
	})	


	// When the socket receives a new user
	socket.on('New User', user => {
		chatMessages.innerHTML += newUserJoined(user.nickname)
	})

	// Allow users to press enter to send their message
	message.addEventListener('keyup', event => {
		if(event.keyCode === 13 && message.value.length > 0){
			sendNewMessage.click()
		}
	})

	// When the user clicks to send a new message emit that message and their nickname
	sendNewMessage.addEventListener('click', () => {
		socket.emit('New Message', {
			nickname: sessionStorage.getItem('nickname'),
			message: message.value,
			color: sessionStorage.getItem('color')
		})
		return message.value = ''
	})

	// as the user is typing emit that it is happening
	message.addEventListener('focusin', () => {
		socket.emit('User Typing', sessionStorage.getItem('nickname'))
	})

	// When the user stops typing emit an event that it happened
	message.addEventListener('focusout', () => {
		socket.emit('User Stopped Typing', sessionStorage.getItem('nickname'))
	})


	// When the socket receives a new message
	socket.on('New Message', message => {
		chatMessages.innerHTML += newUserMessage(message.nickname, message.message, message.color)
	})

	// When the socket receives a 'User Typing' event
	socket.on('User Typing', user => {
		userTyping.innerHTML = userTypingMessage(user)
	})

	// When a user stops typing clear the user typing notification
	socket.on('User Stopped Typing', user => {
		userTyping.textContent = ''
	})
})()