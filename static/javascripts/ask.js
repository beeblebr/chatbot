function AskChat (parseContentToHtml) {
    var that = this;

    var chat = new Chat(parseContentToHtml);

    this.setup = function () {
        chat.setup();
        ChatUI.addChatInputKeyListener(that.listenChatInputKeyup);
        ChatUI.addSubmitButtonOnClickHandler(that.handleSubmit);
        ChatUI.addOptionsHandler(that.handleSpecifyOptionSelect);
        ChatUI.addOptionsSubmitHandler(that.handleOptionsSubmit);

        that.startConversation();
    }

    this.startConversation = function () {
        chat.addBotMessage(getWelcomeMessage(User.getForename()));
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
        that.sendQueryToApi(message);
    }

    this.handleOptionsSubmit = function () {
        var lastMessageOptions = chat.chatContent.getLastMessage().options;

        var selected = []
        for (var i = 0; i < lastMessageOptions.optionsList.length; i++) {
            var messageOption = lastMessageOptions.optionsList[i]
            if (messageOption.selected) {
                selected.push(messageOption.text)
            }
        }
        console.log(selected)
        that.sendSelectedOptionsToApi(selected.join('|'))
        // that.sendQueryToApi($(this).context.innerHTML);

        lastMessageOptions.active = false;
        ChatUI.enableChatInput();
    }

    this.handleSpecifyOptionSelect = function () {
        
        var lastMessageOptions = chat.chatContent.getLastMessage().options;

        lastMessageOptions.optionsList[$(this).index()].selected = !lastMessageOptions.optionsList[$(this).index()].selected;

        chat.updateHtmlState();

    }

    this.sendQueryToApi = function (message) {
        ChatUtils.validateUserInput(message);
        Api.sendQuery(message, User.getId())
        .then(that.handleUserInputApiSuccess)
        .catch(that.handleUserInputApiFailure);
    }

    this.sendSelectedOptionsToApi = function(options) {
        Api.sendSelectedOptions(options, User.getId())
        .then(that.handleUserInputApiSuccess)
        .catch(that.handleUserInputApiFailure);
    }

    this.handleUserInputApiSuccess = function (response) {
        switch(response.type) {
        case 'compromise':
            console.log(response.before_message);
            chat.addBotMessage(response.before_message);
            that.getUserFromApi(response.match.user_id);
            break;
        case 'found':
            that.getUserFromApi(response.match.user_id);
            break;
        case 'nothing_found':
            chat.addBotMessage(getDidNotFindText());
            break;
        case 'clarify':
            ChatUI.disableChatInput();
            that.specifyRequest(response.specify, getClarifyQuestion)
        /*case 'clarify_case':
            ChatUI.disableChatInput();
            that.specifyRequest(response.specify, getClarifyCaseQuestion);
            break;*/
        }
        /*if (!!response.match) {
            that.getUserFromApi(response.match.user_id);
        } else {
            that.specifyRequest(response.specify);
        }*/
    }

    this.handleUserInputApiFailure = function (response) {
        console.log('Failed to send data to server!', response)
    }

    this.getUserFromApi = function (userId) {
        Api.getUser(userId)
        .then(that.handleGetUserApiSucess)
        .catch(that.handleGetUserApiFailure);
    }

    this.handleGetUserApiSucess = function (response) {
        chat.addCard(
            getUserFoundText(response.name),
            response
        );
    }

    this.handleGetUserApiFailure = function (response) {
        console.log('Failed to ask user data from server!', response)
    }

    this.specifyRequest = function(specificationOptions, clarificationFn) {
        if (areSpecificationOptionsProvidedFromResponse(specificationOptions)) {
            chat.addOptions(
                clarificationFn(),
                specificationOptions);            
        } else {
            chat.addBotMessage(
                'No options provided'
                //getDidNotFindText()
            );
        }
    }

    var areSpecificationOptionsProvidedFromResponse = function (options) {
        return options && options.length !== 0
    }

    var addOtherToSpecificationOptions = function (options) {
        options[options.length] = 'Other';
    }
}

function getWelcomeMessage (forename) {
    return getRandomText(['Hi ' + forename + ', how can I assist you?',
        'Hi ' + forename + '! What’s on your mind?',
        'Hi ' + forename + '! What kind of expertise are you looking for?'])
}

function getSpecifyQuestion () {
    return getRandomText([
        'Could you tell me more details?',
        'In which context do you mean it?',
        'Could you give me more information?'])
}

function getClarifyQuestion() {
    return getRandomText([
        'In which context do you mean?\n Select all that apply and press "Done".'
    ])
}

function getUserFoundText (name) {
    return getRandomText([
        'Got it. ' + name + ' is a strong expert in this field!',
        'Found it. ' + name + ' recently worked on that!',
        'Got it. ' + name + ' knows a lot about this topic!'])
}

function getDidNotFindText () {
    return "Sorry, we couldn't find anything."
}


$(document).ready(function() {
    var parseContentToHTML = new ContentToHTMLParser().generateHTML;
    var chat = new AskChat(parseContentToHTML);
    chat.setup();
});