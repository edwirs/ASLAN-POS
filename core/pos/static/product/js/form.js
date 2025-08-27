var input_is_service;
var input_description;

$(function () {
    input_is_service = $('input[name="is_service"]');
    input_description = $('input[name="description"]');
    
    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });

    $('input[name="stock"]')
        .TouchSpin({
            min: 0,
            max: 1000000,
            step: 1,
        })
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'numbers'});
        });

    $('input[name="price"]')
        .TouchSpin({
            min: 0.01,
            max: 1000000,
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

    $('input[name="pvp"]')
        .TouchSpin({
            min: 0.01,
            max: 1000000,
            step: 0.01,
            decimals: 2,
            boostat: 5,
            maxboostedstep: 10,
            prefix: '$'
        })
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'decimals'});
        });
    
    function toggleFields() {
        if (input_is_service.prop('checked')) {
            $('#price, #stock').hide(); // Oculta los divs con los inputs
        } else {
            $('#price, #stock').show(); // Muestra los divs
        }
    }

    // Ejecutar al cargar la página
    toggleFields();

    // Ejecutar cuando se cambia el switch
    input_is_service.on('change', function () {
        toggleFields();
    });

    input_is_service.trigger('change');

    $('input[name="code"]')
        .on('keypress', function (e) {
            return validate_text_box({'event': e, 'type': 'numbers_letters'});
        })
        .on('keyup', function (e) {
            var value = $(this).val();
            $(this).val(value.toUpperCase());
        });
});