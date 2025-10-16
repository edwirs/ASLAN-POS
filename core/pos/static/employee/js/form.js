var input_birth_date, input_start_date, input_retire_date;

$(function () {
    input_birth_date = $('input[name="birth_date"]');
    input_start_date = $('input[name="start_date"]');
    input_retire_date = $('input[name="retire_date"]');

    input_birth_date.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
    });
    input_start_date.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
    });
    input_retire_date.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
    });
    
    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });

    $('input[name="salary"]')
        .TouchSpin({
            min: 0.01,
            max: 100000000,
            step: 0.01,
            decimals: 2,
            boostat: 5,
            maxboostedstep: 10,
            prefix: '$'
        })
        .on('change touchspin.on.min touchspin.on.max', function () {
            $('input[name="pvp"]').trigger("touchspin.updatesettings", {min: parseFloat($(this).val())});
        })
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'decimals'});
        });

    $('input[name="base_salary"]')
        .TouchSpin({
            min: 0.01,
            max: 100000000,
            step: 0.01,
            decimals: 2,
            boostat: 5,
            maxboostedstep: 10,
            prefix: '$'
        })
        .on('change touchspin.on.min touchspin.on.max', function () {
            $('input[name="pvp"]').trigger("touchspin.updatesettings", {min: parseFloat($(this).val())});
        })
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'decimals'});
        });

    $('input[name="dni"]')
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'numbers_letters'});
        })
        .on('keyup', function (e) {
            var value = $(this).val();
            $(this).val(value.toUpperCase());
        });
});