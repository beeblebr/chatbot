function AskChat (parseContentToHtml) {
    var that = this;

    var chat = new Chat(parseContentToHtml);

    this.setup = function () {
        chat.setup();
        ChatUI.addChatInputKeyListener(that.listenChatInputKeyup);
        ChatUI.addSubmitButtonOnClickHandler(that.handleSubmit);
        ChatUI.addOptionsHandler(that.handleSpecifyOptionSelect);
        ChatUI.addOptionsSubmitHandler(that.handleOptionsSubmit);

        that.queryClarificationInProgress = false;
        that.queryClarifications = null;
        that.currentAmbiguousPhrase = null;
        that.queryClarificationChoices = {};
        that.currentResponse = null;

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
        that.sendSelectedOptionsToApi(selected.join('|'), that.clarificationType);

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

    this.sendSelectedOptionsToApi = function(options, clarificationType) {
        if (clarificationType == 'CORPUS_CLARIFICATION_NEEDED') {
            Api.sendSelectedOptionsCorpus(options, User.getId())
            .then(that.handleUserInputApiSuccess)
            .catch(that.handleUserInputApiFailure);
        } else if (clarificationType == 'QUERY_CLARIFICATION_NEEDED') {
            that.queryClarificationChoices[that.currentAmbiguousPhrase] = options;
            that.currentResponse['leadingMessages'] = [];
            if (Object.keys(that.queryClarifications).length == 0) {
                that.queryClarificationInProgress = false;
                chat.addBotMessage('Great! Give me a minute while I find you the best match.');
                Api.sendSelectedOptionsQuery(that.queryClarificationChoices, User.getId())
                .then(that.handleUserInputApiSuccess)
                .catch(that.handleUserInputApiFailure);
            } else {
                that.handleUserInputApiSuccess(that.currentResponse);
            }
        }
    }

    this.performAction = function(response) {
        if (that.queryClarificationInProgress) {
            response.type = 'QUERY_CLARIFICATION_NEEDED';
        }
        switch (response.type) {
        case 'FOUND':
            that.getUserFromApi(response.match.user_id, response.match.knowledge);
            console.log(response.match.user_id);
            break;
        case 'NOTHING_FOUND':
            chat.addBotMessage(getDidNotFindText());
            break;
        case 'CORPUS_CLARIFICATION_NEEDED':
            ChatUI.disableChatInput();
            that.clarificationType = response.type;
            that.specifyCorpusRequest(response.specify, getClarifyCorpusQuestion);
            break;
        case 'QUERY_CLARIFICATION_NEEDED':
            ChatUI.disableChatInput();
            that.clarificationType = response.type;
            var ambiguousPhrase = Object.keys(response.queryClarifications)[0]
            if (ambiguousPhrase == undefined) {
                that.queryClarificationInProgress = false;
                that.currentAmbiguousPhrase = null;
                that.queryClarifications = null;
                that.currentResponse = null;
            } else {
                that.queryClarificationInProgress = true;
                that.currentAmbiguousPhrase = ambiguousPhrase;
                console.log('setting that.queryClarifications');
                that.queryClarifications = response.queryClarifications;
                that.currentResponse = response;
            }
            that.specifyQueryRequest(response.queryClarifications[ambiguousPhrase], getClarifyQueryQuestion, ambiguousPhrase);
            delete response.queryClarifications[ambiguousPhrase];
            console.log(response.queryClarifications)
            break;
        }
    }

    this.showLeadingMessages = function(response) {
        var promises = []
        console.log(response)
        if ('leadingMessages' in response) {
            for (var message of response.leadingMessages) {
                promises.push(new Promise(function(resolve, reject) {
                    chat.addBotMessage(message);
                    setTimeout(function() {
                        resolve();
                    }, 1000)
                }));
            }
        }
        return Promise.all(promises)
    }

    this.handleUserInputApiSuccess = function (response) {
        console.log(response.type);
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