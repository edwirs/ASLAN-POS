var input_date, input_due_date;

$(function () {

    /* =========================
       DATE PICKERS
    ========================== */
    input_date = $('input[name="date"]');
    input_due_date = $('input[name="due_date"]');

    input_date.datetimepicker({
        format: 'YYYY-MM-DD HH:mm',
        locale: 'es',
        sideBySide: true
    });

    input_due_date.datetimepicker({
        format: 'YYYY-MM-DD',
        locale: 'es'
    });


    /* =========================
       SELECT2
    ========================== */
    $('.select2').select2({
        theme: 'bootstrap4',
        language: 'es'
    });


    /* =========================
       MONTO
    ========================== */
    $('input[name="amount"]').TouchSpin({
        min: 0,
        max: 100000000,
        step: 100,
        decimals: 0,
        prefix: '$',
        boostat: 5,
        maxboostedstep: 10
    }).on('keypress', function (e) {
        return validate_text_box({
            event: e,
            type: 'decimals'
        });
    });


    /* =========================
       CANTIDAD PRODUCTO
    ========================== */
    $('input[name="quantity"]').TouchSpin({
        min: 1,
        max: 1000,
        step: 1
    });


    /* =========================
       MOSTRAR CAMPOS DINÁMICOS
    ========================== */
    $('select[name="transaction_type"]').on('change', function () {

        var type = $(this).val();

        // reset
        $('.field-product').hide();
        $('.field-amount').hide();

        if(type === 'product'){
            $('.field-product').fadeIn();
        }
        else{
            $('.field-amount').fadeIn();
        }
    });


    /* =========================
       VALIDACIÓN
    ========================== */
    $('form').on('submit', function(e){

        var type = $('select[name="transaction_type"]').val();
        var amount = $('input[name="amount"]').val();
        var product = $('select[name="product"]').val();

        if(type !== 'product' && (!amount || parseFloat(amount) <= 0)){
            e.preventDefault();
            alert("Debe ingresar un monto válido");
            return false;
        }

        if(type === 'product' && !product){
            e.preventDefault();
            alert("Debe seleccionar un producto");
            return false;
        }
    });

});