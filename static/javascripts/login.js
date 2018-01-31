$(document).ready(function() {
    if (Auth.isUserLoggedIn()) {
        navigateToHome();
    }

    var eightIdElements = $('#eight-id-elements input');
    var eightIdElementsArray = eightIdElements.get();
    var submitButton = $('#eight-id-submit');
    setupPage();

    function setupPage () {
        setupEightId();
        particlesJS.load('index', 'javascripts/vendor/particles-login.json');
    }

    function setupEightId() {
        keyboardFocusToFirstEightId();
        addEightIdKeyListeners();
        addEightIdClickListener();
        addSubmitOnClickHandler();
    }

    function keyboardFocusToFirstEightId () {       
        focusElement($('#eight-id-1')); // Only works on desktop, would be nice to get this working on mobile
    }

    function addEightIdKeyListeners () {
        eightIdElements.keydown(handleKeyDown);
        eightIdElements.keypress(handleKeyPress);
        eightIdElements.keyup(handleKeyUp);
    }

    function handleKeyDown (event) {
        if (isNumberKeyPressed(event)) {
            if (isIdInputFilled(this)) {
                clearEightId(this);
            }
        } else if (isBackspaceKeyPressed(event)) {
            if (isIdInputEmpty(this)) {
                focusPreviousElement(this);
            } else {
                clearEightId(this);
            }
        }
    }

    function handleKeyPress (event) {
        event.preventDefault();
        if (isNumberKeyPressed(event)) {
            setEightId(this, getCharFromKeycode(getKeyCodeFromEvent(event)));
            focusNextElement(this);
        }
    }

    function handleKeyUp (event) {
        if (areAllIdsFilled()) {
            enableSubmitButton();
        } else {
            disableSubmitButton();
        }

        if (areAllIdsFilled() && isEnterKeyPressed(event)) {
            handleSubmit();
        }
    }

    // For keypad numbers
    function normalizeNumberInput (key) {
        return (key >= 96 && key <= 105) ? key-48 : key
    }

    function isNumberKeyPressed (event) {
        var key = normalizeNumberInput(getKeyCodeFromEvent(event))
        return key >= 48 && key <= 57;
    }

    function isBackspaceKeyPressed (event) {
        return getKeyCodeFromEvent(event) === 8;
    }

    function isEnterKeyPressed (event) {
        return getKeyCodeFromEvent(event) === 13;
    }

    function getKeyCodeFromEvent (event) {
        return event.which;
    }

    function getCharFromKeycode (key) {
       return String.fromCharCode(normalizeNumberInput(key))
    }

    function areAllIdsFilled () {
        return getNumberOfEmptyIds() === 0;
    }

    function areAllIdsEmpty () {
        return getNumberOfEmptyIds() === 8;
    }

    function enableSubmitButton () {
        submitButton.prop('disabled', false);
    }

    function disableSubmitButton () {
        submitButton.prop('disabled', true);
    }

    function focusNextElement (currentElement) {
        focusElement($(currentElement).next());
    }

    function focusPreviousElement (element) {
        focusElement($(element).prev());        
    }

    function isIdInputFilled (element) {
        return element.value.length == 1;
    }

    function isIdInputEmpty (element) {
        return element.value.length == 0;
    }

    function setEightId (element, id) {
        $(element).val(id);
    }

    function clearEightId (element) {
        $(element).val('');
    }

    function getNumberOfEmptyIds () {
        return eightIdElementsArray.reduce(function (numberOfEmptyElements, currentElement) {
            return numberOfEmptyElements + (currentElement.value === '' ? 1 : 0)
        }, 0);
    }
    
    function addEightIdClickListener () {
        eightIdElements.click(handleEightIdClick);
    }

    function handleEightIdClick () {
        if (!isIdInputFilled(this)) {
            if (areAllIdsEmpty()) {
                keyboardFocusToFirstEightId();
            } else {
                focusFirstEmptyElement();
            }            
        }
    }

    function focusFirstEmptyElement () {
        eightIdElements.each(function() {
            if (!isIdInputFilled(this)) {
                focusElement(this);
                return false;
            }
        });
    }

    function focusElement (element) {
        element.focus();
    }

    function addSubmitOnClickHandler () {
        submitButton.click(handleSubmit);
    }

    function handleSubmit () {
        Auth.logUserIn(getEightIdFromHtml(), loginSuccess, loginFailure);
    }

    function getEightIdFromHtml() {
        var eightId = '';
        eightIdElements.map(function(value) {
            value++;
            eightId += $('#eight-id-' + value).val();
        });
        return eightId;
    }

    function loginSuccess () {
        navigateToHome();
    }

    function loginFailure () {
        showErrorMessage();
    }

    function showErrorMessage () {
        $('label').addClass('error');
        $('label').html('Wrong 8-ID. Please try again.');
    }

    function hideErrorMessage () {
        $('label').removeClass('error');
        $('label').html('Enter your 8-ID to log in:');
    }
});
