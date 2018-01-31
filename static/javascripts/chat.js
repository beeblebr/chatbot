
$(document).ready(function() {
    setupPage();

    function setupPage () {    
        addAutoGrowToChatInput();
        addChatInputFocusListeners();

        particlesJS.load('page', '../javascripts/vendor/particles-chat.json');
    }

    function addAutoGrowToChatInput () {
        $('#chat-input').autoGrow();
    }

    function addChatInputFocusListeners () {
        $('#chat-input').focusin(makeChatInputBorderDark);
        $('#chat-input').focusout(makeChatInputBorderLight);
    }
    function makeChatInputBorderDark () {
        $('#chat-input').parent().css('border-color', '#78879B');
    }
    function makeChatInputBorderLight () {
        $('#chat-input').parent().css('border-color', '#D9DEE8');
    }
})

function getRandomText(array) {
    return array[Math.floor((Math.random() * array.length) + 1) - 1];
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function Chat (parseContentToHtml) {
    this.chatContent = new ChatContent();
    var that = this;

    this.setup = function () {
        ChatUI.addDictateButtonOnClickHandler(that.handleDictate);
        ChatUI.addInfoButtonOnClickHandler(that.handleInfo);
    }

    this.startConversation = function () {
        that.addBotMessage(getWelcomeMessage());
    }

    this.handleDictate = function () {
        that.addBotMessage(
            'Voice input not yet available. Please type in your request.')
    }

    this.handleInfo = function () {
        that.addBotMessage(
            'You need a hand? Mail <a href="mailto:concierge@thyssenkrupp.com" target="_top">concierge@thyssenkrupp.com</a>!'
        );
    }

    this.updateHtmlState = function () {
        ChatUI.setContentHTML(parseContentToHtml(that.chatContent.content))
    }

    this.addBotMessage = function (message) {
        that.chatContent.addBotMessage(message);
        ChatUI.mockBotTyping(message.length)
        .then(that.updateHtmlState);
    }

    this.addUserMessage = function (message) {
        ChatUtils.validateUserInput(message);
        that.chatContent.addUserMessage(message);
        that.updateHtmlState();
    }

    this.addOptions = function (message, options) {
        that.chatContent.addOptions(message, options);
        ChatUI.mockBotTyping(message.length)
        .then(that.updateHtmlState);
    }

    this.addCard = function (message, card) {
        that.chatContent.addCard(message, card);
        ChatUI.mockBotTyping(message.length)
        .then(that.updateHtmlState);
    }
}

function ChatContent () {
    this.content = []
    var that = this;

    this.getLastMessage = function () {
        var content = that.content
        return content[content.length - 1]
    }

    this.addBotMessage = function (message) {
        that.addMessage('bot', message);
    }

    this.addUserMessage = function (message) {
        that.addMessage('user', message);
    }


    this.addMessage = function (author, message) {
        that.content.push({ 
            author: author,
            message: message
        });
    }

    this.addOptions = function (message, options) {
        that.content.push({ 
            author: 'bot',
            message: message,
            options: {
                optionsList: options.map(function(option) {
                    return {text: option, selected: false}
                }),
                active: true
            },
        });
    }

    this.addCard = function (message, card) {
        that.content.push({ 
            author: 'bot',
            message: message,
            card: card 
        });
    }
}


function ChatUI () {}

ChatUI.setContentHTML = function (content) {
    $('.content').html(content)
}

ChatUI.addChatInputKeyListener = function (handler) {
    $('#chat-input').keyup(handler);
}

ChatUI.addSubmitButtonOnClickHandler = function (handler) {
    $('.chat-input').on('click', '.icon.submit', handler);
}

ChatUI.addDictateButtonOnClickHandler = function (handler) {
    $('.chat-input').on('click', '.icon.dictate', handler);
}

ChatUI.addInfoButtonOnClickHandler = function (handler) {
    $('nav a.navigation.info').click(handler)
}

ChatUI.addOptionsHandler = function (handler) {
    $('div.content').on('click', '#active-specify-list li', handler);
}

ChatUI.addOptionsSubmitHandler = function(handler) {
    $('div.content').on('click', 'button.done', handler);
}

ChatUI.isChatInputEmpty = function () {
    return ChatUI.getChatInput() === ''
}

ChatUI.getChatInput = function () {
    return $('#chat-input').val()
}

ChatUI.clearChatInput = function () {
    $('#chat-input').val('');
}

ChatUI.disableChatInput = function() {
    $("#chat-input").prop('disabled', true);
}

ChatUI.enableChatInput = function() {
    $("#chat-input").prop('disabled', false);
}

ChatUI.showSendTextButton = function () {
    $('.chat-input .icon').removeClass('dictate');
    $('.chat-input .icon').addClass('submit');
}

ChatUI.showDictateButton = function () {
    $('.chat-input .icon').removeClass('submit');
    $('.chat-input .icon').addClass('dictate');
}

ChatUI.mockBotTyping = function (messageLength) {
    ChatUI.showBotIsTyping();
    return new Promise(function(resolve, reject) {
        setTimeout(function() {
            ChatUI.hideBotIsTyping();
            resolve();
        }, ChatUtils.getMockTypingTime(messageLength))
    });
}

ChatUI.showBotIsTyping = function () {
    $('div.main div.pending').css('visibility', 'visible');
}

ChatUI.hideBotIsTyping = function () {
    $('div.main div.pending').css('visibility', 'hidden');
}

function ChatUtils () {}
ChatUtils.cleanChatInputText = function (text) {
    return text.replace(/(\r\n|\n|\r)/gm, '');
}

ChatUtils.isEnterPress = function (keyCode) {
    var keyboardEnterKeyCode = 13
    return  keyCode === keyboardEnterKeyCode
}

ChatUtils.validateUserInput = function (input) {
    if (input === '') {
        throw new Error('Invalid input by user')
    }
}

ChatUtils.getMockTypingTime = function (messageLength) {
    if (messageLength < 30) {
        return 1000
    } else if (messageLength > 50) {
        return 2500
    } else {
        return messageLength * 50
    }
}