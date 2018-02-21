function Api () {}

Api.login = function (eightId) {
    return Api.getUser(eightId);
}

Api.getUser = function (eightId) {
    return new Promise(function (resolve, reject) {
        $.ajax({
            type: 'GET',
            url: MAIN_URL + 'api/users/' + eightId,
            dataType: 'json'})
        .done(resolve)
        .fail(reject)
    });
}

Api.sendQuery = function (message, eightId) {
    var url = MAIN_URL + 'api/query?user_id=' + eightId + '&text=' + encodeURIComponent(message)
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: 'GET',
            url: url})
        .done(resolve)
        .fail(reject);
    });    
}

Api.sendSelectedOptionsCorpus = function(options, eightId) {
    var url = MAIN_URL + 'api/clarify_corpus?user_id=' + eightId + '&options=' + encodeURIComponent(options)
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: 'GET',
            url: url})
        .done(resolve)
        .fail(reject);
    })
}

Api.sendSelectedOptionsQuery = function(queryClarificationChoices, eightId) {
    var url = MAIN_URL + 'api/clarify_query'
    queryClarificationChoices['user_id'] = eightId;
    console.log(queryClarificationChoices)
    return new Promise(function(resolve, reject) {
        $.ajax({
            type: 'POST',
            data: queryClarificationChoices,
            url: url})
        .done(resolve)
        .fail(reject);
    })
}

Api.sendShareMessage = function (message, eightId) {
    var url = MAIN_URL + 'api/knowledges/',
    data = JSON.stringify({
        text: message,
        eight_id: eightId
    });
    return new Promise (function (resolve, reject) {
        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            dataType: 'json',
            crossDomain: true,
            contentType: 'application/json; charset=utf-8'})
        .always(function (response) {
            resolve(response)
        });
    });    
}