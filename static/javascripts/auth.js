function Auth () {}

Auth.isUserLoggedIn = function () {
    if (LocalStorage.containsUser()) {
        if (Auth.hasUserSessionTimedOut()) {
            Auth.logUserOut();
            return false;
        } else {
            Auth.updateUserSessionTimestamp();
            return true;
        }
    } else {
        return false;
    }
}

Auth.logUserIn = function (eightId, success, failure) {
    var apiLoginSuccess = function (response) {
        Auth.setUser(response);
        success();
    }
    var apiLoginFailure = function () {
        console.log('Login failed!');
        failure();
    }
    Api.login(eightId).then(apiLoginSuccess).catch(apiLoginFailure);
}


Auth.getUser = function () {
    return LocalStorage.getUser().value
}

Auth.getUserTimestamp = function () {
    return LocalStorage.getUser().timestamp
}

Auth.logUserOut = function () {
    LocalStorage.clearUser();
}
Auth.setUser = function (user) { 
    LocalStorage.setUser({ 
        "value": user, 
        "timestamp": new Date().getTime()
    });
}   

Auth.hasUserSessionTimedOut = function () {
    var currentTime = new Date().getTime();
    var timeoutHours = 6;
    
    return currentTime - Auth.getUserTimestamp() > hoursToMilliseconds(timeoutHours);
}

Auth.updateUserSessionTimestamp = function () {
    Auth.setUser(Auth.getUser());
}

function LocalStorage () {}

LocalStorage.containsUser = function () {
    return localStorage.getItem('user') && localStorage.getItem('user') !== 'null';
}

LocalStorage.getUser = function () {
    return JSON.parse(localStorage.getItem('user'));
}

LocalStorage.setUser = function (user) {
    localStorage.setItem('user', JSON.stringify(user));
}

LocalStorage.clearUser = function () {
    localStorage.setItem('user', null);
}

function hoursToMilliseconds (hours) {
    var msInSecond = 1000;
    var secondsInMinute = 60;
    var minutesInHour = 60;
    return hours * minutesInHour * secondsInMinute * msInSecond;
}