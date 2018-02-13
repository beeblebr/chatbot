
function ContentToHTMLParser () {
    this.generateHTML = function (content, knowledge) {
        var messageIndex = 0;
        var numberOfMessages = content.length
        return content.reduce(function(html, message) {
            var isLastElement = numberOfMessages === ++messageIndex
            return (
                html +
                '<div class="' + message.author + '">' +
                    addMessageToHtml(message.message, message.author) +
                    addOptionsToHtml(message.options, isLastElement) + 
                    addUserCardToHtml(message.card, message.knowledge) +
                '</div>'
            );
        }, '');
    }

    var addMessageToHtml = function (message, author) {
        return isBotMessage(author) ? addBotMessageToHtml(message) : addUserMessageToHtml(message);
    }

    var isBotMessage = function (author) {
        return author === 'bot'
    }

    var addBotMessageToHtml = function (message) {
        return '<div class="bubble">' + message + '</div>'
    }

    var addUserMessageToHtml = function (message) {
        var profileImage = getProfileImageElement()
        return '<div class="bubble">' + message + '</div>' + profileImage
    }

    var getProfileImageElement = function () {
        return '<img class="profile-image" src="' + User.getProfileImageUrl() + '"/>'
    }    

    var addOptionsToHtml = function (options, isActive) {
        if (!!options) {
            var activeId = isActive ? ' id="active-specify-list"' : ''
            var disabledClass = isActive ? '' : 'disabled';
            return '<ul class="choices options"' + activeId + '>' +
                options.optionsList.map(function(option) {
                    var selected = option.selected ? 'selected' : '';
                    return '<li class="' + selected + '" ' + disabledClass + '>' + option.text + '</li>';
                }).join('')
            + '</ul>'
            + '<button class="done">Done</button><br /><br />';
        } else {
            return ''
        }
    }

    var addUserCardToHtml = function (user, knowledge) {
        if (!!user) {
            return '<div class="results">\
                <div class="result">\
                    <ul class="employee">\
                        <li class="card">\
                            ' + getUserImageElement(user) + '\
                            <div>\
                                <p class="name">' + user.name + '</p>\
                                ' + getUserPositionElement(
                                    UserUtils.getUserPosition(user)) + '\
                                ' + getUserSharedElement(knowledge) + '\
                            </div>\
                        </li>\
                    </ul>\
                    <ul class="choices contact">\
                        <li class="phone"><a href="tel:' + user.phone + '">Call ' + user.name + '</a></li>\
                        <li class="message"><a href="mailto:' + user.email + '">Message ' + user.name + '</a></li>\
                    </ul>\
                </div>\
            </div>';
        } else {
            return ''
        }
    }

    var getUserImageElement = function (user) {        
        return '<img src="' + UserUtils.getProfileImageUrl(user) + '"/>'
    }

    var getUserPositionElement = function (position) {
        if (!!position) {
            return '<p class="position">' + position + '</p>'
        } else {
            return ''
        }
    }

    var getUserSharedElement = function(message) {
        if (!!message) {
            return '<p class="message">"' + message + '"</p>'
        } else {
            return ''
        }
    }

}