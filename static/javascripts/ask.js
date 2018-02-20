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

    this.performAction = function(response) {
        switch(response.type) {
        case 'FOUND':
            that.getUserFromApi(response.match.user_id, response.match.knowledge);
            console.log(response.match.user_id);
            break;
        case 'NOTHING_FOUND':
            chat.addBotMessage(getDidNotFindText());
            break;
        case 'CORPUS_CLARIFICATION_NEEDED':
            ChatUI.disableChatInput();
            that.specifyCorpusRequest(response.specify, getClarifyCorpusQuestion);
            break;
        case 'QUERY_CLARIFICATION_NEEDED':
            ChatUI.disableChatInput();
            var promises = [];
            for (var clarification in response.queryClarifications) {
                promises.push(new Promise(function(resolve, reject) {
                    
                }));
                that.specifyQueryRequest(response.queryClarifications[clarification], getClarifyQueryQuestion, clarification);
            }
            break;
        }
    }

    this.showLeadingMessages = function(response) {
        var promises = []
        if (response.leadingMessages) {
            for (var message of response.leadingMessages) {
                promises.push(new Promise(function(resolve, reject) {
                    chat.addBotMessage(message);
                    setTimeout(function() {
                        resolve();
                    }, 2300)
                }));
            }
        }
        return Promise.all(promises)
    }

    this.handleUserInputApiSuccess = function (response) {
        that.showLeadingMessages(response)
        .then(function() {
            that.performAction(response)
        })
    }

    this.handleUserInputApiFailure = function (response) {
        console.log('Failed to send data to server!', response)
    }

    this.getUserFromApi = function (userId, knowledge) {
        Api.getUser(userId)
        .then(function(response) {
            that.handleGetUserApiSucess(response, knowledge)
        })
        .catch(that.handleGetUserApiFailure);
    }

    this.handleGetUserApiSucess = function (response, knowledge) {
        chat.addCard(
            getUserFoundText(response.name),
            knowledge,
            response
        );
    }

    this.handleGetUserApiFailure = function (response) {
        console.log('Failed to ask user data from server!', response)
    }

    this.specifyCorpusRequest = function(specificationOptions, clarificationFn) {
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

    this.specifyQueryRequest = function(specificationOptions, clarificationFn, ambiguousPhrase) {
        if (areSpecificationOptionsProvidedFromResponse(specificationOptions)) {
            chat.addOptions(
                clarificationFn(ambiguousPhrase),
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

function getClarifyCorpusQuestion() {
    return getRandomText([
        'In which context do you mean?<br /> Select all that apply and press "Done".'
    ])
}

function getClarifyQueryQuestion(ambiguousPhrase) {
    return getRandomText([
        'I\'m not sure what "' + ambiguousPhrase + '" means. Which of the following best describes it?<br />Select all that apply and press "Done".'
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