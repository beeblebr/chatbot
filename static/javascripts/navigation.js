function navigateToHome () {
    navigateTo(MAIN_URL + 'home');
}

function navigateToLogin () {
    navigateTo(MAIN_URL);
}

function navigateTo (url) {
    window.location.href = url;
}