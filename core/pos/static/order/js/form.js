// Configuración para que AJAX envíe el CSRF Token automáticamente
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken_pos = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Usamos la nueva variable aquí
            xhr.setRequestHeader("X-CSRFToken", csrftoken_pos);
        }
    }
});

/*************************************************
 * VARIABLES GLOBALES
 *************************************************/
let select_paymentmethod;
let select_transfermethods;
let transferCol;
let input_cash, input_change, input_propina;

/*************************************************
 * READY
 *************************************************/
$(function () {

    // CAMPOS
    select_paymentmethod   = $('#id_paymentmethod');
    select_transfermethods = $('#id_transfermethods');
    transferCol            = select_transfermethods.closest('.col');

    input_cash    = $('#id_cash');
    input_change  = $('#id_change');
    input_propina = $('#id_propina');

    /*************************************************
     * SELECT2 (NO ocultar aquí)
     *************************************************/
    select_paymentmethod.select2({
        theme: 'bootstrap4',
        language: 'es'
    });

    select_transfermethods.select2({
        theme: 'bootstrap4',
        language: 'es'
    });

    /*************************************************
     * FUNCIONES CENTRALES
     *************************************************/
    function hideTransfer() {
        select_transfermethods.val(null).trigger('change');
        transferCol.hide();
    }

    function showTransfer(options = []) {
        select_transfermethods.empty();
        options.forEach(opt => {
            select_transfermethods.append(
                new Option(opt.text, opt.value)
            );
        });
        transferCol.show();
        select_transfermethods.trigger('change');
    }

    /*************************************************
     * LOGICA PAYMENT → TRANSFER
     *************************************************/
    select_paymentmethod.on('change', function () {
        const value = $(this).val();

        if (value === 'transfer') {
            showTransfer([
                { value: 'nequi', text: 'Nequi' },
                { value: 'daviplata', text: 'Daviplata' }
            ]);

        } else if (value === 'mixto') {
            showTransfer([
                { value: 'nequi_cash', text: 'Nequi + Efectivo' },
                { value: 'daviplata_cash', text: 'Daviplata + Efectivo' },
                { value: 'nequi_daviplata', text: 'Nequi + Daviplata' }
            ]);

        } else {
            hideTransfer();
        }
    });

    /*************************************************
     * TOUCHSPIN
     *************************************************/
    input_cash.TouchSpin({
        min: 0,
        max: 100000000,
        step: 100,
        decimals: 0
    }).on('change', function () {
        const cash  = parseFloat($(this).val()) || 0;
        const total = parseFloat($('#id_total').val()) || 0;
        input_change.val(Math.max(cash - total, 0));
    });

    input_propina.TouchSpin({
        min: 0,
        max: 100000000,
        step: 100,
        decimals: 0
    });

});

/*************************************************
 * APERTURA DEL MODAL DESDE TARJETA
 *************************************************/
document.addEventListener('DOMContentLoaded', function () {

    /*************************************************
     * CLICK EN TARJETA → VER PEDIDO DE LA MESA
     *************************************************/
    document.querySelectorAll('.table-card').forEach(card => {
        card.addEventListener('click', function () {
            const url = this.dataset.url;
            if (url) {
                window.location.href = url;
            }
        });
    });

    document.querySelectorAll('.btn-open-table').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const modalEl = document.getElementById('myModalEdit');

            // RESET COMPLETO DEL MODAL
            $('#myModalEdit form')[0].reset();
            $('#id_paymentmethod').val(null).trigger('change');
            $('#id_transfermethods').val(null).trigger('change');

            // OCULTAR TRANSFER SIEMPRE AL ABRIR
            $('#id_transfermethods').closest('.col').hide();

            // TOTAL
            const total = parseNumberES(this.dataset.total);
            modalEl.querySelector('#id_total').value = total;

            // MOSTRAR MODAL
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        });
    });

	// Botón ver pedido
    document.querySelectorAll('.btn-view-order').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const orderId = this.dataset.orderId;
            if (orderId) {
                window.location.href = `/order/detail/${orderId}/`;
            }
        });
    });
	
	// Botón limpiar mesa
    document.querySelectorAll('.btn-clear-table').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const tableId = this.dataset.tableId;
            if (confirm('¿Desea eliminar el pedido de esta mesa?')) {
                console.log('Eliminar pedido mesa:', tableId);
            }
        });
    });

    document.querySelectorAll('.product_card').forEach(card => {
        card.addEventListener('click', function () {

            const product = {
                id: this.dataset.id,
                name: this.dataset.name,
                price: parseFloat(this.dataset.price)
            };

            order.addProduct(product);
        });
    });

    $(function () {
        const modalEl = document.getElementById('myModalEdit');

        $('.btn-open-table').on('click', function() {
            // Guardamos el order_id en el botón de guardar para usarlo luego
            $('#btnSaveEdit').data('order-id', this.dataset.orderId);
        });

        $('#btnSaveEdit').on('click', function () {
            const orderId = $(this).data('order-id');
            const form = document.getElementById('formEditSale');
            const cash  = parseFloat($('#id_cash').val()) || 0;
            const total = parseFloat($('#id_total').val()) || 0;

            // =============================
            // VALIDACIONES
            // =============================
            if (cash <= 0) {
                toastr.warning('Debe ingresar el valor en efectivo');
                $('#id_cash').focus();
                return;
            }

            if (cash < total) {
                toastr.error('El efectivo ingresado no puede ser menor al total');
                $('#id_cash').focus();
                return;
            }

            const formData = new FormData(form);
            
            // Añadimos parámetros extra para la acción en el view
            formData.append('action', 'create_sale');
            formData.append('order_id', orderId);

            $.ajax({
                url: window.location.pathname, // O la URL de tu OrderCreateView
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (response.hasOwnProperty('error')) {
                        toastr.error(response.error);
                    } else {
                        toastr.success('Venta realizada con éxito');
                        location.reload(); // Recargamos para ver la mesa libre
                    }
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    toastr.error(errorThrown);
                }
            });
        });
    });
});

/*************************************************
 * UTILIDADES
 *************************************************/
function parseNumberES(value) {
    if (!value) return 0;
    return Number(
        value.toString()
            .replace(/\./g, '')
            .replace(',', '.')
    ) || 0;
}

function formatCOP(value) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(value);
}


let order = {
    products: [],
    total: 0,

    addProduct(product) {
        let found = this.products.find(p => p.id === product.id);
        if (found) {
            found.qty += 1;
        } else {
            product.qty = 1;
            this.products.push(product);
        }
        this.render();
    },

    calculateTotal() {
        this.total = this.products.reduce(
            (sum, p) => sum + (p.qty * p.price),
            0
        );
    },

    render() {
        this.calculateTotal();

        let tbody = document.querySelector('#tblProductsBarra tbody');
        tbody.innerHTML = '';

        this.products.forEach(p => {
            tbody.innerHTML += `
                <tr>
                    <td>${p.name}</td>
                    <td class="text-center">${p.qty}</td>
                    <td class="text-end">$${(p.qty * p.price).toFixed(0)}</td>
                </tr>
            `;
        });

        document.querySelector('[name="total"]').value = this.total.toFixed(0);
    }
};
