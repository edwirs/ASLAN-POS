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

    $('#frmForm').off('submit').on('submit', function (e) {
        e.preventDefault();

        let amount = parseFloat($('#id_amount').val()) || 0;

        if (amount <= 0){
            return message_error('El monto debe ser mayor a 0');
        }

        let form = this;
        let params = new FormData(form);
        let url_refresh = $(this).attr('data-url');

        submit_with_formdata({
            params: params,
            success: function(request){

                let url_redirect = url_refresh;

                let iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                document.body.appendChild(iframe);

                iframe.src = request.print_url;

                let redirected = false; // evita doble redirect

                function goBack(){
                    if(!redirected){
                        redirected = true;
                        iframe.remove();
                        toastr.success('Transacción guardada correctamente');
                        location.href = url_redirect;
                    }
                }

                iframe.onload = function(){
                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();

                    // si imprime
                    iframe.contentWindow.onafterprint = goBack;

                    // fallback si no dispara onafterprint
                    setTimeout(goBack, 1500);
                };
            }
        });
    });
});