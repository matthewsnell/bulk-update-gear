$(document).ready(function () {
    $('#loading-message').hide();
    $('#gear-form').submit(function () {
        $('#loading-message').show();
        $('#gear_submit_button').prop("disabled", true);
    });
});