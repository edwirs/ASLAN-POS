var input_date;

$(function () {
    input_date = $('input[name="created_at"]');

    input_date.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
        maxDate: new Date()
    });
    
    $('.select2').select2({
        language: 'es',
        theme: 'bootstrap4'
    });

    $('input[name="amount"]').TouchSpin({
        min: 0,
        max: 1000000000,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10
    });
    
    $('input[name="amount"]').on('keypress', function (e) {
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