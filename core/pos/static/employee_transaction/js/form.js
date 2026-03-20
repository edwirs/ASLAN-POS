var products = [];

if (typeof initial_products !== 'undefined') {
    try {
        products = typeof initial_products === 'string'
            ? JSON.parse(initial_products)
            : initial_products;
    } catch (e) {
        products = [];
    }
}

$(function () {

    $('.select2').select2({
        theme: 'bootstrap4',
        language: 'es'
    });

    $('input[name="amount"]').TouchSpin({
        min: 0,
        max: 100000000,
        step: 100,
        decimals: 0,
        prefix: '$'
    });

    // 🔥 FORZAR VALOR INICIAL
    setTimeout(function () {
        let amount = $('#id_amount').attr('value');
        if (amount !== undefined && amount !== '') {
            $('#id_amount').val(parseFloat(amount)).trigger('change');
        }
    }, 100);

    /* =========================
       AGREGAR PRODUCTO
    ========================== */
    $('#select_product').on('change', function () {

        let option = $("#select_product option:selected");
        let id = option.val();

        if (!id) return;

        let text = option.text();
        let pvp = parseFloat(option.data('pvp')) || 0;

        let exists = products.find(p => p.id == id);

        if (exists) {
            exists.quantity++;
        } else {
            products.push({
                id: id,
                name: text,
                pvp: pvp,
                quantity: 1
            });
        }

        renderProducts();
        calculateTotal();

        $(this).val(null).trigger('change');
    });

    /* =========================
       RENDER TABLA
    ========================== */
    function renderProducts() {

        let tbody = $('#tblProducts tbody');
        tbody.empty();

        products.forEach((p, index) => {

            let subtotal = p.pvp * p.quantity;

            tbody.append(`
                <tr>
                    <td>${p.name}</td>

                    <td>
                        <input type="number" min="1" value="${p.quantity}" 
                        class="form-control form-control-sm qty" data-index="${index}">
                    </td>

                    <td>$${formatMoney(p.pvp)}</td>

                    <td>$${formatMoney(subtotal)}</td>

                    <td>
                        <button class="btn btn-danger btn-sm remove" data-index="${index}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `);
        });
    }

    /* =========================
       FORMATO DINERO
    ========================== */
    function formatMoney(value) {
        return new Intl.NumberFormat('es-CO').format(value);
    }

    /* =========================
       CALCULAR TOTAL
    ========================== */
    function calculateTotal() {

        let total = 0;

        products.forEach(p => {
            total += p.pvp * p.quantity;
        });

        // input real (backend)
        $('#id_amount').val(total).trigger('change');

        // visual
        $('#total_amount').text(formatMoney(total));
    }

    /* =========================
       CAMBIAR CANTIDAD
    ========================== */
    $(document).on('change', '.qty', function () {

        let index = $(this).data('index');
        let value = parseInt($(this).val());

        if (value < 1) value = 1;

        products[index].quantity = value;

        renderProducts();
        calculateTotal();
    });

    /* =========================
       ELIMINAR PRODUCTO
    ========================== */
    $(document).on('click', '.remove', function () {

        let index = $(this).data('index');
        products.splice(index, 1);

        renderProducts();
        calculateTotal();
    });

    /* =========================
       CONTROL POR TIPO
    ========================== */
    $('#id_transaction_type').on('change', function () {
        toggleTransactionType();
    });

    function toggleTransactionType() {

        let type = $('#id_transaction_type').val();

        let source = $('#id_source');
        let productsCard = $('#card-products');
        let amount = $('#id_amount');

        if (type === 'product') {

            source.val('inventory').trigger('change');
            source.prop('disabled', true);

            productsCard.show();

            // 🔒 bloquear edición manual
            amount.prop('readonly', true);

        } else {

            source.prop('disabled', false);

            productsCard.hide();

            products = [];
            renderProducts();

            // 🔓 permitir edición
            amount.prop('readonly', false);
        }
    }

    if (products.length > 0) {
        $('#id_transaction_type').val('product').trigger('change');
    } else {
        toggleTransactionType();
    }

    /* =========================
       SUBMIT
    ========================== */
    $('#frmForm').off('submit').on('submit', function (e) {
        e.preventDefault();

        $('#id_transaction_type').trigger('change');
        let type = $('#id_transaction_type option:selected').val();

        if (type === 'product' && products.length === 0) {
            return message_error('Debe agregar al menos un producto');
        }

        let form = this;
        let params = new FormData(form);
        let url_redirect = $(this).attr('data-url');
        params.append('source', $('#id_source').val());

        params.append('products', JSON.stringify(products));

        let btn = $(this).find('button[type="submit"]');
        btn.prop('disabled', true);

        submit_with_formdata({
            params: params,
            success: function (request) {

                let iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                document.body.appendChild(iframe);

                iframe.src = request.print_url;

                let redirected = false;

                function goBack() {
                    if (!redirected) {
                        redirected = true;
                        iframe.remove();
                        toastr.success('Transacción guardada correctamente');
                        btn.prop('disabled', false);
                        location.href = url_redirect;
                    }
                }

                iframe.onload = function () {

                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();

                    let printMonitor = setInterval(function () {
                        if (document.hasFocus()) {
                            clearInterval(printMonitor);
                            goBack();
                        }
                    }, 500);

                };
            }
        });
    });
    if (products.length > 0) {
        renderProducts();

        // 🔥 SOLO recalcula si NO hay valor previo
        let currentAmount = parseFloat($('#id_amount').val()) || 0;

        if (currentAmount === 0) {
            calculateTotal();
        }
    } else {
        // 🔥 mantener valor existente
        let currentAmount = parseFloat($('#id_amount').val()) || 0;
        $('#id_amount').val(currentAmount).trigger('change');
    }
});