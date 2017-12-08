function ShareChat (parseContentToHtml) {
    var that = this;

    var chat = new Chat(parseContentToHtml);

    this.setup = function () {
        chat.setup();
        ChatUI.addChatInputKeyListener(that.listenChatInputKeyup);
        ChatUI.addSubmitButtonOnClickHandler(that.handleSubmit);
        ChatUI.addOptionsHandler(that.handleOptions);

        that.startConversation();
    }

    this.startConversation = function () {
        chat.addBotMessage(getShareWelcomeMessage(User.getForename()));
    }

    this.listenChatInputKeyup = function (event) {
        if (!ChatUI.isChatInputEmpty()) {
            ChatUI.showSendTextButton()
        } else {
            ChatUI.showDictateButton()
        }
        
        if (ChatUtils.isEnterPress(event.keyCode)) {
            that.handleSubmit();
        }
    }

    this.handleSubmit = function () {
        var message = ChatUtils.cleanChatInputText(ChatUI.getChatInput());
        ChatUI.clearChatInput();

        chat.addUserMessage(message);
        that.sendMessageToAPI(message);
    }

    this.sendMessageToAPI = function (message) {
        Api.sendShareMessage(message, User.getId())
        .then(that.handleApiResponse)
        .catch(that.handleApiResponse)
    }

    this.handleApiResponse = function (response) {
        if (response.status = 200) {
            chat.addOptions(getThanksText(), ['Yes', 'No'])
        }
    } 

    this.handleOptions = function () {
        var lastMessageOptions = chat.chatContent.getLastMessage().options;
        lastMessageOptions.optionsList.map(function(option) {
            return option.selected = false;
        })
        lastMessageOptions.optionsList[$(this).index()].selected = true;
        lastMessageOptions.active = false;
        
        chat.updateHtmlState();

        if ($(this).index() === 0) {
            chat.addBotMessage(
                'Go ahead, I\'m still listening!'
            );
        } else {
            chat.addBotMessage(
                'Thanks for sharing!'
            );
        }
    }
}

function getThanksText () {
    return getRandomText(['Great stuff! Thanks for contributing to the network. Got anything else for me today?',
                    'Thanks for sharing your expertise with us! Any more topics you have been working on?'])
}

function getShareWelcomeMessage (forename) {
    return  getRandomText(['Hi ' + forename + ', tell me something you\'ve been working on.',
        'Hi ' + forename + '! What are the three main topics you have been working on?']);
}


$(document).ready(function() {
    var parseContentToHTML = new ContentToHTMLParser().generateHTML;
    var chat = new ShareChat(parseContentToHTML);
    chat.setup();
});
