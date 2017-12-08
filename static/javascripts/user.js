function User () {}

User.getId = function () {
    return Auth.getUser().eight_id;
}

User.getProfileImageUrl = function () {
    return UserUtils.getProfileImageUrl(Auth.getUser());
}

User.getForename = function () {
    return Auth.getUser().name
}

function UserUtils () {}

UserUtils.getUserSharedMessage = function (user) {
	var knowledge = "";
	$.ajax({
		url: '/api/knowledge/' + user.eight_id,
		success: function (res) {
			knowledge = res['text'];
		},
		async: false
	})
	return knowledge;
}

UserUtils.getProfileImageUrl = function (user) {
    var src = 'static/images/assets/default-user-small.png'
    if (!!user.img_url) {
        src = user.img_url
    }
    return src
}

UserUtils.getUserPosition = function (user) {
    return user.position;
}