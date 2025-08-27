$(function () {
    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });

    $('input[name="names"]')
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'letters'});
        });

    $('input[name="dni"]')
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'numbers'});
        });

    $('input[name="mobile"]')
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'numbers'});
        });
});