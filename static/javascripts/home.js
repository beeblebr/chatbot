$(document).ready(function() {
    if (!Auth.isUserLoggedIn()) {
        navigateToLogin();
        return;
    }
    var user = Auth.getUser()
    
    setNameText(user.name)
    setUserImage(user.img_url)

    setLogOutButtonHandler()    

    particlesJS.load('home', 'javascripts/vendor/particles-home.json');
});

function setLogOutButtonHandler () {
    $('#home-logout').click(handleLogOut)
}

function handleLogOut () {
    Auth.logUserOut();
    navigateToLogin();
}

function setNameText (name) {
    $('.first-name').text(function() {
        return name;
    });
}

function setUserImage (url) {
    if (!!url) {
        $('#user_photo').attr("src", url);
    } else {
        $('#user_photo').attr("src", '/images/assets/default-user.png');
    }
}
