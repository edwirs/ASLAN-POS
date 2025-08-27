
$(function () {
    
    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });

    $('input[name="quantity"]').TouchSpin({
        min: 0,
        max: 1000000,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10
    });
    
    $('input[name="quantity"]').on('keypress', function (e) {
        const char = String.fromCharCode(e.which);

        // permitir solo números y un punto
        if (!/[0-9.]/.test(char)) {
            e.preventDefault();
            return false;
        }

        // no permitir más de un punto decimal
        if (char === '.' && $(this).val().includes('.')) {
            e.preventDefault();
            return false;
        }
    });
});